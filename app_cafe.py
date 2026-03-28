import streamlit as st

st.set_page_config(page_title="WorthIt? | Melbourne Cafe", page_icon="☕", layout="centered")

# ---------- Session ----------
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "pro_unlocked" not in st.session_state:
    st.session_state.pro_unlocked = False

# ---------- Language ----------
lang = st.radio("Language / 语言", ["English", "中文"], horizontal=True)

def t(en, cn):
    return en if lang == "English" else cn

# ---------- Email ----------
def valid_email(email):
    return len(email) > 5 and "@" in email and "." in email

# ---------- Calculation ----------
def calc(price, cost, sales, rent, labour, other):
    revenue = price * sales * 30
    cogs = cost * sales * 30
    total = rent + labour + other + cogs
    profit = revenue - total

    margin = price - cost
    fixed = rent + labour + other
    breakeven = fixed / margin / 30 if margin > 0 else None

    return {
        "revenue": revenue,
        "cogs": cogs,
        "total": total,
        "profit": profit,
        "margin": margin,
        "fixed": fixed,
        "breakeven": breakeven
    }

def scenario_calc(price, cost, sales, rent, labour, other, sales_change=1.0, cost_change=1.0):
    return calc(price, cost * cost_change, sales * sales_change, rent, labour, other)

def verdict(profit):
    if profit < 0:
        return t("🔴 Not Worth It", "🔴 不值得做")
    elif profit < 5000:
        return t("🟡 Borderline", "🟡 勉强可行")
    else:
        return t("🟢 Worth It", "🟢 值得做")

def payback_months(invest, profit):
    if profit <= 0:
        return None
    return invest / profit

def payback_label(months):
    if months is None:
        return t("❌ Not recoverable", "❌ 无法回本")
    if months <= 18:
        return t("🟢 Fast return", "🟢 回本很快")
    elif months <= 30:
        return t("🟡 Acceptable", "🟡 可以接受")
    elif months <= 48:
        return t("🟠 Slow return", "🟠 回本较慢")
    else:
        return t("🔴 Too slow", "🔴 回本过慢")

def risk_score(base_profit, cons_profit, months, gap):
    score = 100

    if base_profit < 0:
        score -= 45
    elif base_profit < 5000:
        score -= 20

    if cons_profit < 0:
        score -= 25

    if months is None:
        score -= 20
    elif months > 48:
        score -= 20
    elif months > 30:
        score -= 10

    if gap < 0:
        score -= 20
    elif gap < 30:
        score -= 10

    return max(0, min(100, score))

def risk_label(score):
    if score >= 75:
        return t("🟢 Low to Moderate Risk", "🟢 低到中等风险")
    elif score >= 50:
        return t("🟡 Medium Risk", "🟡 中等风险")
    else:
        return t("🔴 High Risk", "🔴 高风险")

# ---------- Defaults ----------
DEFAULT_INVEST = 250000.0
DEFAULT_RENT = 6000.0
DEFAULT_STAFF = 3
DEFAULT_SALARY = 4000.0
DEFAULT_OTHER = 5000.0
DEFAULT_PRICE = 5.38
DEFAULT_COST = 1.75
DEFAULT_SALES = 300

# ---------- Header ----------
st.title("WorthIt? ☕")
st.write(t(
    "Should you open a cafe in Melbourne?",
    "在墨尔本开咖啡店值得吗？"
))
st.caption(t(
    "Pressure-test the numbers before you commit capital.",
    "在投入资金之前，先把数字算清楚。"
))

# ---------- Reality Check ----------
with st.container(border=True):
    st.subheader(t(
        "Reality Check: Melbourne cafes are harder than they look",
        "现实情况：墨尔本咖啡店比看起来更难做"
    ))

    if lang == "English":
        st.write("• Melbourne coffee prices are already relatively high, so raising price further is not always easy.")
        st.write("• Labour is usually one of the biggest costs in a cafe.")
        st.write("• Rent can wipe out a business that still looks busy from the outside.")
        st.write("• Peak-hour traffic often hides weak off-peak demand.")
    else:
        st.write("• 墨尔本咖啡价格本来就不低，所以继续提价并不总是容易。")
        st.write("• 人工通常是咖啡店最大的成本之一。")
        st.write("• 很多店看起来很忙，但租金就足以吞掉利润。")
        st.write("• 高峰时段的热闹，常常掩盖了非高峰时段的疲弱需求。")

# ---------- Inputs ----------
with st.container(border=True):
    st.subheader(t("Cafe Setup", "咖啡店基础设置"))

    c1, c2 = st.columns(2)
    with c1:
        invest = st.number_input(t("Initial Investment ($)", "初始投资 ($)"), value=DEFAULT_INVEST)
        rent = st.number_input(t("Monthly Rent ($)", "每月租金 ($)"), value=DEFAULT_RENT)
        staff = st.number_input(t("Staff Count", "员工数量"), value=DEFAULT_STAFF)
    with c2:
        salary = st.number_input(t("Salary per Staff ($/month)", "每人月薪 ($/月)"), value=DEFAULT_SALARY)
        other = st.number_input(t("Other Fixed Costs ($/month)", "其他固定成本 ($/月)"), value=DEFAULT_OTHER)

with st.container(border=True):
    st.subheader(t("Sales Assumptions", "销售假设"))

    c1, c2, c3 = st.columns(3)
    with c1:
        price = st.number_input(t("Average Price per Sale", "平均每单售价"), value=DEFAULT_PRICE)
    with c2:
        cost = st.number_input(t("Average Cost per Sale", "平均每单成本"), value=DEFAULT_COST)
    with c3:
        sales = st.number_input(t("Daily Sales Volume", "日销量"), value=DEFAULT_SALES)

if st.button(t("Run Cafe Analysis", "开始分析咖啡店")):
    st.session_state.analysis_done = True
    st.session_state.pro_unlocked = False

# ---------- Results ----------
if st.session_state.analysis_done:
    labour = staff * salary

    base = calc(price, cost, sales, rent, labour, other)
    cons = scenario_calc(price, cost, sales, rent, labour, other, sales_change=0.8, cost_change=1.05)
    opt = scenario_calc(price, cost, sales, rent, labour, other, sales_change=1.15, cost_change=1.0)

    months = payback_months(invest, base["profit"])
    gap = sales - base["breakeven"] if base["breakeven"] is not None else -999

    with st.container(border=True):
        st.subheader(t("Result", "结果"))
        st.write(f"**{t('Revenue', '收入')}**: ${base['revenue']:,.0f}")
        st.write(f"**{t('Cost', '成本')}**: ${base['total']:,.0f}")
        st.write(f"**{t('Profit', '利润')}**: ${base['profit']:,.0f}")

        if base["breakeven"] is not None:
            st.write(f"**{t('Break-even daily sales', '盈亏平衡日销量')}**: {base['breakeven']:,.0f} {t('units/day', '单位/天')}")

    with st.container(border=True):
        st.subheader(t("Before you decide", "在你决定之前"))

        if lang == "English":
            st.write("• Is this actually profitable, or does it just look busy?")
            st.write("• What happens if sales drop or costs rise?")
            st.write("• Where are the hidden risks in this setup?")
            st.write("• What would need to change to make this work?")
        else:
            st.write("• 这个生意是真的赚钱吗，还是只是看起来很忙？")
            st.write("• 如果销量下降、成本上升，会发生什么？")
            st.write("• 这个模型里隐藏的风险在哪里？")
            st.write("• 如果想把它做成，需要改变什么？")

        email = st.text_input(t("Enter email", "输入邮箱"))

        if st.button(t("Get My Result", "获取完整分析")):
            if valid_email(email):
                st.session_state.pro_unlocked = True
                st.success(t("Analysis unlocked below ↓", "分析已解锁 ↓"))
            else:
                st.error(t("Please enter a valid email address.", "请输入有效邮箱地址。"))

# ---------- PRO ----------
if st.session_state.analysis_done and st.session_state.pro_unlocked:
    labour = staff * salary
    base = calc(price, cost, sales, rent, labour, other)
    cons = scenario_calc(price, cost, sales, rent, labour, other, sales_change=0.8, cost_change=1.05)
    opt = scenario_calc(price, cost, sales, rent, labour, other, sales_change=1.15, cost_change=1.0)

    months = payback_months(invest, base["profit"])
    gap = sales - base["breakeven"] if base["breakeven"] is not None else -999
    score = risk_score(base["profit"], cons["profit"], months, gap)

    with st.container(border=True):
        st.subheader(t("Should You Do This?", "到底该不该做？"))

        if score < 50:
            st.error(t(
                "Honestly — this doesn’t look like a good idea right now.",
                "说实话，这个项目现在看起来不太值得做。"
            ))
        elif score < 75:
            st.warning(t(
                "This might work, but it’s riskier than it looks.",
                "这个项目不是不能做，但风险比你想的要高。"
            ))
        else:
            st.success(t(
                "This looks reasonably viable — but execution will matter a lot.",
                "这个项目看起来是可行的，但执行会非常关键。"
            ))

    with st.container(border=True):
        st.subheader(t("What’s Driving This Outcome", "为什么会是这个结果"))

        bullets = []

        if base["profit"] < 0:
            bullets.append(t(
                "Your base case is already loss-making. That is the biggest problem.",
                "你的基础情景本身已经亏损，这是最大的问题。"
            ))
        else:
            bullets.append(t(
                f"Your base case shows monthly profit of ${base['profit']:,.0f}.",
                f"你的基础情景显示月利润约为 ${base['profit']:,.0f}。"
            ))

        if cons["profit"] < 0:
            bullets.append(t(
                "A moderate downside case turns this into a loss, which means the model is fragile.",
                "只要出现中等程度的下行，这个模型就会亏损，说明它很脆弱。"
            ))
        else:
            bullets.append(t(
                "Even in the conservative case, the business still stays above water.",
                "即使在保守情景下，这个生意也还能维持不亏。"
            ))

        if gap < 0:
            bullets.append(t(
                f"Your expected daily sales are about {abs(gap):,.0f} units below break-even.",
                f"你的预期日销量比盈亏平衡点低约 {abs(gap):,.0f} 单位。"
            ))
        elif gap < 30:
            bullets.append(t(
                f"You are only {gap:,.0f} units/day above break-even, which is a thin safety margin.",
                f"你每天只比盈亏平衡点高 {gap:,.0f} 单位，安全垫偏薄。"
            ))
        else:
            bullets.append(t(
                f"You are about {gap:,.0f} units/day above break-even, which gives you some operating buffer.",
                f"你每天比盈亏平衡点高约 {gap:,.0f} 单位，说明有一定经营缓冲。"
            ))

        if months is None:
            bullets.append(t(
                "At the current base case, the business does not recover the initial investment.",
                "按当前基础情景，这个生意无法回收初始投资。"
            ))
        elif months > 30:
            bullets.append(t(
                f"Payback is about {months:,.1f} months, which is slow for a cafe.",
                f"回本周期约为 {months:,.1f} 个月，对咖啡店来说偏慢。"
            ))
        else:
            bullets.append(t(
                f"Payback is about {months:,.1f} months, which is within a reasonable range for a cafe.",
                f"回本周期约为 {months:,.1f} 个月，对咖啡店来说还算合理。"
            ))

        for b in bullets:
            st.write("• " + b)

    with st.container(border=True):
        st.subheader(t("What Needs to Change", "如果要做，需要改变什么"))

        changes = []

        if base["profit"] < 0:
            changes.append(t(
                "You need to reduce fixed costs — especially rent, staffing, or both.",
                "你需要降低固定成本，尤其是租金、人员配置，或者两者都降。"
            ))

        if gap < 0:
            changes.append(t(
                "You need materially higher daily sales. That usually means stronger demand, better location, or a different concept.",
                "你需要明显更高的日销量。这通常意味着更强的需求、更好的地段，或不同的经营定位。"
            ))
        elif gap < 30:
            changes.append(t(
                "You need a larger buffer above break-even. Right now the model leaves little room for error.",
                "你需要更大的安全垫。现在这个模型留给犯错的空间太小了。"
            ))

        if cons["profit"] < 0:
            changes.append(t(
                "You need more downside protection. Current assumptions are still too optimistic.",
                "你需要更强的下行保护。目前的假设仍然偏乐观。"
            ))

        if months is not None and months > 30:
            changes.append(t(
                "You need faster capital recovery — either through better margin, stronger volume, or lower upfront cost.",
                "你需要更快回本——要么提高利润率，要么增加销量，要么降低前期投入。"
            ))

        if not changes:
            changes.append(t(
                "The model already looks relatively healthy. Focus on execution discipline, staffing, and demand consistency.",
                "这个模型整体已经相对健康。接下来重点是执行、人员安排和需求稳定性。"
            ))

        for c in changes:
            st.write("• " + c)

    with st.container(border=True):
        st.subheader(t("Reality Check", "现实提醒"))
        st.write(t(
            "A cafe can look busy and still lose money.",
            "咖啡店可以看起来很忙，但仍然亏钱。"
        ))
        st.write(t(
            "What matters is margin, cost control, and consistency — not just traffic.",
            "真正重要的是利润率、成本控制和稳定性，而不只是客流。"
        ))

    with st.container(border=True):
        st.subheader(t("Risk Summary", "风险总结"))
        st.write(f"**{t('Risk score', '风险评分')}**: {score}/100")
        st.write(f"**{t('Risk level', '风险等级')}**: {risk_label(score)}")
        st.write(f"**{t('Payback view', '回本判断')}**: {payback_label(months)}")
