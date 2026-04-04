import io
import requests
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="WorthIt? | Cafe", page_icon="☕", layout="centered")

# ---------- Session ----------
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "pro_unlocked" not in st.session_state:
    st.session_state.pro_unlocked = False

# ---------- Language ----------
lang = st.radio("Language / 语言", ["English", "中文"], horizontal=True)

def t(en, cn):
    return en if lang == "English" else cn

# ---------- CSS ----------
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    max-width: 900px;
}
.hero-box {
    padding: 1.2rem;
    border-radius: 16px;
    border: 1px solid rgba(128,128,128,0.2);
    margin-bottom: 1rem;
}
.alert-box {
    padding: 12px;
    border-radius: 12px;
    border: 1px solid rgba(255,0,0,0.2);
    background-color: rgba(255,0,0,0.05);
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------- Email ----------
def valid_email(email: str) -> bool:
    return len(email) > 5 and "@" in email

# ---------- Airtable ----------
def save_to_airtable(email, language, setup_type, invest, rent, staff, salary, other, price, cost, sales, profit, risk_score_value):
    try:
        url = f"https://api.airtable.com/v0/{st.secrets['AIRTABLE_BASE_ID']}/{st.secrets['AIRTABLE_TABLE_NAME']}"
        headers = {
            "Authorization": f"Bearer {st.secrets['AIRTABLE_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "fields": {
                "email": email,
                "language": language,
                "setup_type": setup_type,
                "investment": invest,
                "rent": rent,
                "staff": staff,
                "salary": salary,
                "other": other,
                "price": price,
                "cost": cost,
                "sales": sales,
                "profit": profit,
                "risk_score": risk_score_value,
                "created_at": datetime.now().isoformat(timespec="seconds")
            }
        }
        requests.post(url, json=payload, headers=headers)
        return True
    except:
        return False

# ---------- Inputs ----------
setup_type = st.radio(
    t("Setup Type", "开店方式"),
    [t("New cafe", "从零开店"), t("Take over", "接手咖啡店")]
)

invest = st.number_input(t("Initial Investment", "初始投资"), value=280000)
rent = st.number_input(t("Monthly Rent", "月租金"), value=10000)
staff = st.number_input(t("Staff Count", "员工数"), value=4)
salary = st.number_input(t("Salary per Staff", "人均工资"), value=4500)
other = st.number_input(t("Other Costs", "其他成本"), value=5000)

price = st.number_input(t("Price", "售价"), value=5.5)
cost = st.number_input(t("Cost", "成本"), value=1.8)
sales = st.number_input(t("Daily Sales", "日销量"), value=220)

# ---------- Calculation ----------
def calc():
    revenue = price * sales * 30
    labour = staff * salary
    cogs = cost * sales * 30
    fixed = rent + labour + other
    total = fixed + cogs
    profit = revenue - total
    margin = price - cost
    breakeven = fixed / margin / 30 if margin > 0 else 0
    return revenue, total, profit, labour, cogs, fixed, breakeven

if st.button(t("Run Analysis", "开始分析")):
    st.session_state.analysis_done = True
    st.session_state.pro_unlocked = False

# ---------- Result ----------
if st.session_state.analysis_done:

    st.markdown(f"""
    <div class="alert-box">
    <b>{t("Most people underestimate cafe costs by 20–30%",
          "大多数人低估咖啡店成本 20–30%")}</b><br>
    {t("Small mistakes can turn profit into loss.",
       "一个小误差就可能从盈利变成亏损")}
    </div>
    """, unsafe_allow_html=True)

    revenue, total, profit, labour, cogs, fixed, breakeven = calc()

    st.subheader(t("Base Result", "基础结果"))
    st.write(f"Revenue: ${revenue:,.0f}")
    st.write(f"Cost: ${total:,.0f}")
    st.write(f"Profit: ${profit:,.0f}")

    # ---------- Email Gate ----------
    st.markdown("### " + t("Get Full Risk Breakdown", "获取完整风险分析"))

    st.markdown(t(
        "This is not a calculator — it tells you if your cafe will survive.",
        "这不是计算器，而是判断你的咖啡店能不能活下来"
    ))

    email = st.text_input(t("Enter email", "输入邮箱"))

    st.markdown(t(
        "Free · No spam · Instant access",
        "免费 · 不骚扰 · 即时解锁"
    ))

    st.markdown(t(
        "Before deciding, understand your real risk.",
        "做决定前，先看清真实风险"
    ))

    if st.button(t("Unlock Full Risk Breakdown (Free)", "免费解锁完整分析")):
        if valid_email(email):
            save_to_airtable(
                email, lang, setup_type,
                invest, rent, staff, salary, other,
                price, cost, sales, profit, 50
            )
            st.session_state.pro_unlocked = True
            st.success(t(
                "Unlocked ↓ (most people realise they were wrong here)",
                "已解锁 ↓（大多数人会在这里发现自己算错了）"
            ))
        else:
            st.error(t("Enter valid email", "请输入有效邮箱"))

# ---------- Pro ----------
if st.session_state.pro_unlocked:

    st.markdown("---")
    st.subheader(t("Full Risk Breakdown", "完整风险拆解"))

    revenue, total, profit, labour, cogs, fixed, breakeven = calc()
    gap = sales - breakeven

    # 1 Reality
    st.markdown("### " + t("1. Reality Check", "1. 现实检查"))
    if profit < 0:
        st.error(t(f"You are losing ${profit:,.0f}/month.",
                   f"每月亏损 ${profit:,.0f}"))
    else:
        st.success(t(f"You make ${profit:,.0f}/month.",
                     f"每月盈利 ${profit:,.0f}"))

    # 2 Break-even
    st.markdown("### " + t("2. Break-even Point", "2. 盈亏平衡点"))
    st.write(t(f"You need {breakeven:,.0f} sales/day.",
               f"每天需要 {breakeven:,.0f} 单"))

    if gap < 0:
        st.error(t(f"{abs(gap):,.0f} below break-even",
                   f"低于盈亏平衡 {abs(gap):,.0f} 单"))
    elif gap < 30:
        st.warning(t(f"Only {gap:,.0f} above break-even",
                     f"只高出 {gap:,.0f} 单"))
    else:
        st.success(t(f"{gap:,.0f} above break-even",
                     f"高出 {gap:,.0f} 单"))

    # 3 Cost structure
    st.markdown("### " + t("3. Cost Structure", "3. 成本结构"))
    st.write(f"Rent: ${rent:,.0f}")
    st.write(f"Staff: ${labour:,.0f}")
    st.write(f"COGS: ${cogs:,.0f}")
    st.write(f"Other: ${other:,.0f}")

    # 4 Risk
    st.markdown("### " + t("4. Biggest Risk", "4. 最大风险"))
    if profit < 0:
        st.write(t("Costs too high vs sales",
                   "成本相对销量过高"))
    elif gap < 20:
        st.write(t("Very thin margin",
                   "安全垫很薄"))
    else:
        st.write(t("Execution dependent",
                   "高度依赖执行"))

    # 5 Action
    st.markdown("### " + t("5. What Needs to Change", "5. 需要改变"))
    if profit < 0:
        st.write(t("Reduce cost or increase sales",
                   "降低成本或提高销量"))
    elif gap < 20:
        st.write(t("Increase pricing or volume",
                   "提高定价或销量"))
    else:
        st.write(t("Maintain stability",
                   "保持稳定运营"))
