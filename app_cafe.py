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

# ---------- Email ----------
def valid_email(email):
    return len(email) > 5 and "@" in email and "." in email

# ---------- Mode ----------
mode = st.radio(
    t("Setup Type", "开店方式"),
    [t("New cafe (from scratch)", "从零开店"), t("Take over existing cafe", "接手现有咖啡店")]
)

# ---------- Defaults ----------
if mode == t("New cafe (from scratch)", "从零开店"):
    DEFAULT_INVEST = 280000
else:
    DEFAULT_INVEST = 150000  # takeover cheaper

DEFAULT_RENT = 10000
DEFAULT_STAFF = 4
DEFAULT_SALARY = 4500
DEFAULT_OTHER = 5000
DEFAULT_PRICE = 5.5
DEFAULT_COST = 1.8
DEFAULT_SALES = 220

# ---------- Calc ----------
def calc(price, cost, sales, rent, labour, other):
    revenue = price * sales * 30
    cogs = cost * sales * 30
    total = rent + labour + other + cogs
    profit = revenue - total

    margin = price - cost
    fixed = rent + labour + other
    breakeven = fixed / margin / 30 if margin > 0 else None

    return revenue, total, profit, breakeven

# ---------- UI ----------
st.title("WorthIt? ☕")

st.caption(t(
    "Default numbers reflect realistic Melbourne conditions.",
    "默认参数基于墨尔本真实经营情况"
))

# ---------- Cost Explanation ----------
with st.expander(t("Where does the money go?", "钱都花在哪里？")):
    if lang == "English":
        st.write("• Fit-out (build, plumbing, compliance)")
        st.write("• Rent bond (3–6 months)")
        st.write("• Equipment")
        st.write("• Cash buffer (first 3–6 months)")
    else:
        st.write("• 装修（施工、水电、合规）")
        st.write("• 押金（3–6个月租金）")
        st.write("• 设备")
        st.write("• 前期现金缓冲（3–6个月）")

# ---------- Inputs ----------
col1, col2 = st.columns(2)

with col1:
    invest = st.number_input(t("Initial Investment", "初始投资"), value=DEFAULT_INVEST)
    rent = st.number_input(t("Monthly Rent", "每月租金"), value=DEFAULT_RENT)
    staff = st.number_input(t("Staff Count", "员工数量"), value=DEFAULT_STAFF)

with col2:
    salary = st.number_input(t("Salary per Staff", "每人月薪"), value=DEFAULT_SALARY)
    other = st.number_input(t("Other Costs", "其他成本"), value=DEFAULT_OTHER)

price = st.number_input(t("Price per Sale", "客单价"), value=DEFAULT_PRICE)
cost = st.number_input(t("Cost per Sale", "单笔成本"), value=DEFAULT_COST)
sales = st.number_input(t("Daily Sales", "日销量"), value=DEFAULT_SALES)

if st.button(t("Run Analysis", "开始分析")):
    st.session_state.analysis_done = True
    st.session_state.pro_unlocked = False

# ---------- Results ----------
if st.session_state.analysis_done:

    labour = staff * salary
    revenue, total, profit, breakeven = calc(price, cost, sales, rent, labour, other)

    st.subheader(t("Result", "结果"))

    st.write(f"{t('Revenue', '收入')}: ${revenue:,.0f}")
    st.write(f"{t('Cost', '成本')}: ${total:,.0f}")
    st.write(f"{t('Profit', '利润')}: ${profit:,.0f}")

    if breakeven:
        st.write(f"{t('Break-even', '盈亏平衡')}: {breakeven:,.0f} {t('units/day', '单/天')}")

    # ---------- Email Gate ----------
    st.markdown("### " + t("Before you decide", "在你决定之前"))

    if lang == "English":
        st.write("• Is this actually profitable?")
        st.write("• What if sales drop?")
        st.write("• Where are the risks?")
    else:
        st.write("• 这个生意真的赚钱吗？")
        st.write("• 如果销量下降怎么办？")
        st.write("• 风险在哪里？")

    email = st.text_input(t("Enter email", "输入邮箱"))

    if st.button(t("Get My Result", "获取结果")):
        if valid_email(email):
            st.session_state.pro_unlocked = True
            st.success(t("Unlocked ↓", "已解锁 ↓"))
        else:
            st.error(t("Invalid email", "邮箱不正确"))

# ---------- PRO ----------
if st.session_state.analysis_done and st.session_state.pro_unlocked:

    st.subheader(t("Should You Do This?", "该不该做？"))

    if profit < 0:
        st.error(t("Not a good idea", "不建议做"))
    elif profit < 5000:
        st.warning(t("Risky", "有风险"))
    else:
        st.success(t("Looks viable", "可以考虑"))

    st.subheader(t("Reality", "现实"))

    st.write(t(
        "Many cafes look busy but barely make money.",
        "很多咖啡店看起来很忙，但其实赚不到钱"
    ))
