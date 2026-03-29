import streamlit as st

st.set_page_config(page_title="WorthIt?", page_icon="☕", layout="centered")

# ---------- Session ----------
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "pro_unlocked" not in st.session_state:
    st.session_state.pro_unlocked = False

# ---------- Language ----------
lang = st.radio("Language / 语言", ["English", "中文"], horizontal=True)

def t(en, cn):
    return en if lang == "English" else cn

# ---------- Style ----------
st.markdown("""
<style>
.block-container {max-width: 900px;}
.card {
    padding: 16px;
    border-radius: 16px;
    border: 1px solid rgba(120,120,120,0.2);
    margin-bottom: 12px;
}
.big {font-size: 22px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# ---------- Setup ----------
setup = st.radio(
    t("Setup Type", "开店方式"),
    [t("New cafe", "从零开店"), t("Takeover", "接手现有店")]
)

DEFAULT_INVEST = 280000 if setup == t("New cafe", "从零开店") else 150000
DEFAULT_RENT = 10000
DEFAULT_STAFF = 4
DEFAULT_SALARY = 4500
DEFAULT_OTHER = 5000
DEFAULT_PRICE = 5.5
DEFAULT_COST = 1.8
DEFAULT_SALES = 220

# ---------- Calc ----------
def calc(price, cost, sales, rent, labour, other):
    rev = price * sales * 30
    cogs = cost * sales * 30
    total = rent + labour + other + cogs
    profit = rev - total

    margin = price - cost
    fixed = rent + labour + other
    breakeven = fixed / margin / 30 if margin > 0 else None

    return rev, total, profit, breakeven

def risk(profit, cons, months, gap):
    s = 100
    if profit < 0: s -= 40
    if cons < 0: s -= 25
    if months and months > 36: s -= 15
    if gap < 0: s -= 20
    return max(0, min(100, s))

# ---------- UI ----------
st.title("WorthIt? ☕")
st.caption(t("Test your cafe idea before you commit money",
             "在投入资金前先测试你的咖啡店想法"))

# ---------- Inputs ----------
c1, c2 = st.columns(2)
with c1:
    invest = st.number_input("Investment", value=DEFAULT_INVEST)
    rent = st.number_input("Rent", value=DEFAULT_RENT)
    staff = st.number_input("Staff", value=DEFAULT_STAFF)
with c2:
    salary = st.number_input("Salary", value=DEFAULT_SALARY)
    other = st.number_input("Other", value=DEFAULT_OTHER)

price = st.number_input("Price", value=DEFAULT_PRICE)
cost = st.number_input("Cost", value=DEFAULT_COST)
sales = st.number_input("Daily Sales", value=DEFAULT_SALES)

if st.button(t("Run Analysis", "开始分析")):
    st.session_state.analysis_done = True
    st.session_state.pro_unlocked = False

# ---------- Base ----------
if st.session_state.analysis_done:

    labour = staff * salary
    rev, total, profit, breakeven = calc(price, cost, sales, rent, labour, other)

    cons_profit = calc(price, cost*1.05, sales*0.8, rent, labour, other)[2]

    months = invest / profit if profit > 0 else None
    gap = sales - breakeven if breakeven else -999

    st.markdown(f"""
    <div class="card">
    <div class="big">{t("Base Result", "基础结果")}</div>
    {t("Profit", "利润")}: ${profit:,.0f}
    </div>
    """, unsafe_allow_html=True)

    email = st.text_input(t("Enter email to unlock", "输入邮箱解锁"))

    if st.button(t("Unlock", "解锁")):
        if "@" in email:
            st.session_state.pro_unlocked = True

# ---------- PRO ----------
if st.session_state.pro_unlocked:

    labour = staff * salary
    rev, total, profit, breakeven = calc(price, cost, sales, rent, labour, other)
    cons_profit = calc(price, cost*1.05, sales*0.8, rent, labour, other)[2]

    months = invest / profit if profit > 0 else None
    gap = sales - breakeven if breakeven else -999
    score = risk(profit, cons_profit, months, gap)

    # Executive Summary
    st.markdown(f"""
    <div class="card">
    <div class="big">{t("Executive Summary", "执行摘要")}</div>
    {t(
    "This business is viable but fragile. Small changes can break it.",
    "这个生意可以成立，但很脆弱，小变化就可能亏损。"
    )}
    </div>
    """, unsafe_allow_html=True)

    # Score
    st.subheader(t("Risk Score", "风险评分"))
    st.progress(score/100)
    st.write(score)

    # Top 3
    st.subheader(t("Top 3 Actions", "最重要的三件事"))

    if gap < 0:
        st.write("1. Increase sales volume")
    if profit < 0:
        st.write("2. Reduce fixed costs")
    if cons_profit < 0:
        st.write("3. Improve downside buffer")

    # Brutal truth
    st.subheader(t("If this was my money", "如果这是我的钱"))
    if score < 50:
        st.error(t("I would not do this.",
                   "我不会做这个生意"))
    elif score < 75:
        st.warning(t("Only if I fix the weak points first.",
                     "除非先修正问题，否则不建议做"))
    else:
        st.success(t("This is worth trying.",
                     "这个项目可以尝试"))
