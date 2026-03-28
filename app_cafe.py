import streamlit as st
import re

st.set_page_config(page_title="WorthIt? | Melbourne Cafe", page_icon="☕", layout="centered")

# ---------- Session State ----------
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "pro_unlocked" not in st.session_state:
    st.session_state.pro_unlocked = False
if "email_submitted" not in st.session_state:
    st.session_state.email_submitted = False

# ---------- Theme-friendly CSS ----------
st.markdown("""
<style>
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 980px;
}
.hero {
    border-radius: 18px;
    padding: 1.4rem 1.4rem 1.2rem 1.4rem;
    border: 1px solid rgba(128,128,128,0.25);
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 0.35rem;
}
.hero-subtitle {
    opacity: 0.8;
    line-height: 1.6;
    font-size: 1rem;
}
.callout {
    border-radius: 16px;
    padding: 1rem 1.1rem;
    border: 1px solid rgba(128,128,128,0.25);
    margin: 0.8rem 0 1rem 0;
}
.big-number {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0.15rem 0;
}
.small-muted {
    opacity: 0.75;
    font-size: 0.95rem;
}
.pro-box {
    border-radius: 16px;
    padding: 1rem 1.1rem;
    border: 1px dashed rgba(128,128,128,0.35);
    margin: 0.6rem 0 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ---------- Language ----------
lang = st.radio("Language / 语言", ["English", "中文"], horizontal=True)

def t(en, cn):
    return en if lang == "English" else cn

# ---------- Helpers ----------
def valid_email(email):
    return len(email) > 5 and "@" in email and "." in email

def calc(price, cost, sales, rent, labour, other):
    revenue = price * sales * 30
    cogs = cost * sales * 30
    total = rent + labour + other + cogs
    profit = revenue - total

    margin = price - cost
    fixed = rent + labour + other

    if margin > 0:
        breakeven = fixed / margin / 30
    else:
        breakeven = None

    return {
        "revenue": revenue,
        "cogs": cogs,
        "cost": total,
        "profit": profit,
        "breakeven": breakeven
    }

def get_industry_thresholds():
    # Food & Beverage thresholds
    return 18, 24, 30

def get_buffer():
    # Food & Beverage safety buffer
    return 30

def payback_assessment(invest, monthly_profit):
    if monthly_profit <= 0:
        return None, t("❌ Not recoverable", "❌ 无法回本")

    months = invest / monthly_profit
    fast, acceptable, slow = get_industry_thresholds()

    if months <= fast:
        label = t("🟢 Fast return", "🟢 回本很快")
    elif months <= acceptable:
        label = t("🟡 Acceptable", "🟡 可以接受")
    elif months <= slow:
        label = t("🟠 Slow return", "🟠 回本较慢")
    else:
        label = t("🔴 Too slow", "🔴 回本过慢")

    return months, label

def verdict_label(profit):
    if profit > 5000:
        return t("🟢 Worth It", "🟢 值得做")
    elif profit >= 0:
        return t("🟡 Borderline", "🟡 勉强可行")
    else:
        return t("🔴 Not Worth It", "🔴 不值得做")

def score_label(score):
    if score >= 75:
        return t("🟢 Low to Moderate Risk", "🟢 低到中等风险")
    elif score >= 50:
        return t("🟡 Medium Risk", "🟡 中等风险")
    else:
        return t("🔴 High Risk", "🔴 高风险")

def risk_score(profit, conservative_profit, payback_months, breakeven_gap):
    score = 100
    buffer = get_buffer()

    if profit < 0:
        score -= 45
    elif profit < 5000:
        score -= 20

    if conservative_profit < 0:
        score -= 25

    if payback_months is None:
        score -= 20
    else:
        _, acceptable, slow = get_industry_thresholds()
        if payback_months > slow:
            score -= 20
        elif payback_months > acceptable:
            score -= 10

    if breakeven_gap < 0:
        score -= 20
    elif breakeven_gap < buffer:
        score -= 10

    return max(0, min(100, score))

def recommendations(profit, conservative_profit, payback_months, gap):
    recs = []
    buffer = get_buffer()

    if profit < 0:
        recs.append(t(
            "Reduce fixed costs before investing — especially rent and labour.",
            "投资前优先压低固定成本，尤其是租金和人工。"
        ))

    if gap < 0:
        recs.append(t(
            "Your current sales assumption is below break-even. Reassess demand, foot traffic, and conversion assumptions.",
            "你当前的销量假设低于盈亏平衡点，需要重新评估需求、客流和转化率。"
        ))
    elif gap < buffer:
        recs.append(t(
            "You are only slightly above break-even. Build a larger sales safety buffer before committing capital.",
            "你只是略高于盈亏平衡点，建议先建立更大的销量安全垫。"
        ))

    if conservative_profit < 0:
        recs.append(t(
            "The downside case turns loss-making. Improve margin of safety before proceeding.",
            "保守情景下会亏损，说明安全垫不足，建议先提升抗风险能力。"
        ))

    if payback_months is not None:
        _, acceptable, slow = get_industry_thresholds()
        if payback_months > slow:
            recs.append(t(
                "Capital recovery is too slow for a cafe. Only proceed if there is a strong location or concept advantage.",
                "对咖啡店来说，资金回收过慢。除非地段或定位有明显优势，否则不建议继续。"
            ))
        elif payback_months > acceptable:
            recs.append(t(
                "Capital recovery is acceptable but not strong. Tighten your assumptions and protect downside risk.",
                "资金回收可以接受，但并不强。建议收紧关键假设并增强抗风险能力。"
            ))

    if not recs:
        recs.append(t(
            "This cafe setup looks relatively healthy. Stress-test rent, labour, and demand before final commitment.",
            "这个咖啡店模型整体相对健康，但在最终投资前仍建议继续压力测试租金、人工和需求。"
        ))

    return recs

def analyst_view(score):
    if score < 50:
        return t(
            "This cafe opportunity currently looks weak. Unless assumptions can be materially improved, the investment case is not attractive.",
            "这个咖啡店项目目前看起来偏弱。除非关键假设能明显改善，否则投资吸引力不高。"
        )
    elif score < 75:
        return t(
            "This cafe may work, but it needs tighter operating assumptions and stronger downside protection.",
            "这个咖啡店项目不是不能做，但需要更严格的经营假设和更强的抗风险能力。"
        )
    else:
        return t(
            "This cafe appears reasonably investable under current assumptions, though it still requires real-world validation.",
            "按照当前假设，这个咖啡店项目具备一定投资可行性，但仍需结合真实市场验证。"
        )

# ---------- Defaults: Melbourne cafe starter model ----------
DEFAULT_INVEST = 250000.0
DEFAULT_RENT = 6000.0
DEFAULT_STAFF = 3
DEFAULT_SALARY = 4000.0
DEFAULT_OTHER = 5000.0
DEFAULT_PRICE = 5.38
DEFAULT_COST = 1.75
DEFAULT_SALES = 300

# ---------- Hero ----------
st.markdown(f"""
<div class="hero">
    <div class="hero-title">WorthIt? ☕</div>
    <div class="hero-subtitle">
        {t(
            "Should you open a cafe in Melbourne? Pressure-test the numbers before you commit capital.",
            "在墨尔本开咖啡店值得吗？在你投入资金前，先把数字算清楚。"
        )}
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- Cafe Reality Check ----------
with st.container(border=True):
    st.subheader(t("Reality Check: Melbourne cafes are harder than they look", "现实情况：墨尔本咖啡店比看起来更难做"))

    if lang == "English":
        st.write("• Melbourne coffee pricing is already high by everyday standards, so raising price further is not always easy.")
        st.write("• Labour is usually one of the biggest costs in a cafe.")
        st.write("• Rent pressure can quickly wipe out a “busy-looking” business.")
        st.write("• Peak-hour trade often hides weak off-peak demand.")
    else:
        st.write("• 墨尔本日常咖啡价格已经不低，所以继续提价并不总是容易。")
        st.write("• 人工通常是咖啡店最大的成本之一。")
        st.write("• 租金压力很容易吞掉一个“看起来很忙”的生意。")
        st.write("• 高峰时段的热闹，常常掩盖了非高峰时段的疲弱需求。")

# ---------- Inputs ----------
with st.container(border=True):
    st.subheader(t("Cafe Setup", "咖啡店基础设置"))

    c1, c2 = st.columns(2)
    with c1:
        invest = st.number_input(t("Initial Investment ($)", "初始投资 ($)"), min_value=0.0, value=DEFAULT_INVEST, step=1000.0)
        rent = st.number_input(t("Monthly Rent ($)", "每月租金 ($)"), min_value=0.0, value=DEFAULT_RENT, step=500.0)
        staff = st.number_input(t("Staff Count", "员工数量"), min_value=0, value=DEFAULT_STAFF, step=1)
    with c2:
        salary = st.number_input(t("Salary per Staff ($/month)", "每人月薪 ($/月)"), min_value=0.0, value=DEFAULT_SALARY, step=100.0)
        other = st.number_input(t("Other Fixed Costs ($/month)", "其他固定成本 ($/月)"), min_value=0.0, value=DEFAULT_OTHER, step=100.0)

with st.container(border=True):
    st.subheader(t("Sales Assumptions", "销售假设"))

    c1, c2, c3 = st.columns(3)
    with c1:
        price = st.number_input(t("Average Price per Sale", "平均每单售价"), min_value=0.0, value=DEFAULT_PRICE, step=0.1)
    with c2:
        cost = st.number_input(t("Average Cost per Sale", "平均每单成本"), min_value=0.0, value=DEFAULT_COST, step=0.05)
    with c3:
        sales = st.number_input(t("Daily Sales Volume", "日销量"), min_value=0, value=DEFAULT_SALES, step=10)

if st.button(t("Run Cafe Analysis", "开始分析咖啡店"), use_container_width=True, type="primary"):
    st.session_state.analysis_done = True
    st.session_state.pro_unlocked = False
    st.session_state.email_submitted = False

# ---------- Results ----------
if st.session_state.analysis_done:
    labour = staff * salary

    base = calc(price, cost, sales, rent, labour, other)
    conservative = calc(price, cost * 1.05, sales * 0.8, rent, labour, other)
    optimistic = calc(price, cost, sales * 1.15, rent, labour, other)

    revenue = base["revenue"]
    total = base["cost"]
    profit = base["profit"]
    breakeven = base["breakeven"]

    with st.container(border=True):
        st.subheader(t("Final Answer", "最终结论"))
        st.info(verdict_label(profit))

        m1, m2, m3 = st.columns(3)
        m1.metric(t("Revenue", "收入"), f"${revenue:,.0f}")
        m2.metric(t("Cost", "成本"), f"${total:,.0f}")
        m3.metric(t("Monthly Profit", "月利润"), f"${profit:,.0f}")

    with st.container(border=True):
        st.subheader(t("Break-even Requirement", "盈亏平衡要求"))

        if breakeven is not None:
            gap = sales - breakeven
            buffer = get_buffer()

            st.markdown(f"""
            <div class="callout">
                <div class="small-muted">{t("Required daily sales to break even", "达到盈亏平衡所需日销量")}</div>
                <div class="big-number">{breakeven:,.0f} {t("units/day", "单位/天")}</div>
                <div class="small-muted">{t("Your assumption", "你的假设")}：{sales:,.0f} {t("units/day", "单位/天")}</div>
                <div class="small-muted">{t("Recommended safety buffer for cafes", "咖啡店建议安全垫")}：+{buffer} {t("units/day", "单位/天")}</div>
            </div>
            """, unsafe_allow_html=True)

            if gap >= buffer:
                st.success(t(
                    f"You are above break-even by {gap:,.0f} units/day, with a healthy buffer.",
                    f"你每天比盈亏平衡点多卖 {gap:,.0f} 单位，且安全垫较健康。"
                ))
            elif gap >= 0:
                st.warning(t(
                    f"You are above break-even by {gap:,.0f} units/day, but the buffer is thin.",
                    f"你每天比盈亏平衡点多卖 {gap:,.0f} 单位，但安全垫偏薄。"
                ))
            else:
                st.error(t(
                    f"You are below break-even by {abs(gap):,.0f} units/day.",
                    f"你每天比盈亏平衡点少卖 {abs(gap):,.0f} 单位。"
                ))
        else:
            gap = -999
            st.error(t(
                "Break-even cannot be calculated because average price per sale must be higher than average cost per sale.",
                "无法计算盈亏平衡点，因为平均每单售价必须高于平均每单成本。"
            ))

    with st.container(border=True):
        st.subheader(t("Capital Return", "资金回报"))

        months, payback_label = payback_assessment(invest, profit)

        if months is not None:
            st.metric(t("Payback Period", "回本周期"), f"{months:,.1f} {t('months', '个月')}")
            st.info(payback_label)
        else:
            st.error(payback_label)

        fast, acceptable, slow = get_industry_thresholds()
        st.caption(t(
            f"For cafes, a rough benchmark is: fast ≤ {fast} months, acceptable ≤ {acceptable} months, slow ≤ {slow} months.",
            f"对于咖啡店，粗略标准为：快速回本 ≤ {fast}个月，可接受 ≤ {acceptable}个月，较慢 ≤ {slow}个月。"
        ))

    with st.container(border=True):
        st.subheader(t("Scenario Analysis", "情景分析"))

        c1, c2, c3 = st.columns(3)

        with c1:
            st.caption(t("Conservative", "保守"))
            st.write(t("20% lower sales, 5% higher unit cost", "销量下降20%，单位成本上升5%"))
            st.metric("P/L", f"${conservative['profit']:,.0f}")

        with c2:
            st.caption(t("Base", "基准"))
            st.write(t("Your current assumptions", "你当前输入的假设"))
            st.metric("P/L", f"${profit:,.0f}")

        with c3:
            st.caption(t("Optimistic", "乐观"))
            st.write(t("15% higher sales", "销量上升15%"))
            st.metric("P/L", f"${optimistic['profit']:,.0f}")

    with st.container(border=True):
        st.subheader(t("Unlock Pro Cafe Analysis", "解锁专业版咖啡店分析"))
        st.markdown(f"""
        <div class="pro-box">
            {t(
                "Enter your email to unlock deeper judgement, risk scoring, key flags, and recommendations for your cafe model.",
                "输入邮箱后可解锁更深入的咖啡店投资判断、风险评分、关键风险点和改善建议。"
            )}
        </div>
        """, unsafe_allow_html=True)

        email = st.text_input(t("Email Address", "邮箱地址"))

        if st.button(t("Unlock with Email", "输入邮箱解锁"), use_container_width=True):
            if valid_email(email):
                st.session_state.email_submitted = True
                st.session_state.pro_unlocked = True
                st.success(t(
                    f"Unlocked for {email}",
                    f"已为 {email} 解锁"
                ))
            else:
                st.error(t(
                    "Please enter a valid email address.",
                    "请输入有效的邮箱地址。"
                ))

    if st.session_state.pro_unlocked:
        score = risk_score(
            profit=profit,
            conservative_profit=conservative["profit"],
            payback_months=months,
            breakeven_gap=gap
        )

        recs = recommendations(
            profit=profit,
            conservative_profit=conservative["profit"],
            payback_months=months,
            gap=gap
        )

        with st.container(border=True):
            st.subheader(t("Pro Cafe Analysis", "专业版咖啡店分析"))

            c1, c2 = st.columns(2)
            with c1:
                st.metric(t("Risk Score", "风险评分"), f"{score}/100")
            with c2:
                st.info(score_label(score))

            st.markdown("### " + t("Key Risk Flags", "关键风险点"))
            if profit < 0:
                st.write("• " + t("Base case is loss-making", "基准情景本身亏损"))
            if conservative["profit"] < 0:
                st.write("• " + t("Downside scenario turns loss-making", "保守情景下转为亏损"))
            if gap < 0:
                st.write("• " + t("Required daily sales exceed current assumption", "回本所需日销量高于当前假设"))
            if months is not None:
                _, acceptable, slow = get_industry_thresholds()
                if months > acceptable:
                    st.write("• " + t("Capital recovery is relatively slow for a cafe", "对咖啡店来说，资金回收偏慢"))

            st.markdown("### " + t("Recommendations", "改善建议"))
            for r in recs:
                st.write("• " + r)

            st.markdown("### " + t("Analyst View", "分析师判断"))
            st.write(analyst_view(score))
