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

    return revenue, total, profit, breakeven

# ---------- Defaults ----------
DEFAULT_INVEST = 250000.0
DEFAULT_RENT = 6000.0
DEFAULT_STAFF = 3
DEFAULT_SALARY = 4000.0
DEFAULT_OTHER = 5000.0
DEFAULT_PRICE = 5.38
DEFAULT_COST = 1.75
DEFAULT_SALES = 300

# ---------- UI ----------
st.title("WorthIt? ☕")

st.write(t(
    "Should you open a cafe in Melbourne?",
    "在墨尔本开咖啡店值得吗？"
))

# ---------- Inputs ----------
col1, col2 = st.columns(2)

with col1:
    invest = st.number_input("Initial Investment", value=DEFAULT_INVEST)
    rent = st.number_input("Monthly Rent", value=DEFAULT_RENT)
    staff = st.number_input("Staff Count", value=DEFAULT_STAFF)

with col2:
    salary = st.number_input("Salary per Staff", value=DEFAULT_SALARY)
    other = st.number_input("Other Costs", value=DEFAULT_OTHER)

price = st.number_input("Price per Sale", value=DEFAULT_PRICE)
cost = st.number_input("Cost per Sale", value=DEFAULT_COST)
sales = st.number_input("Daily Sales", value=DEFAULT_SALES)

if st.button("Run Analysis"):
    st.session_state.analysis_done = True
    st.session_state.pro_unlocked = False

# ---------- Results ----------
if st.session_state.analysis_done:

    labour = staff * salary

    revenue, total, profit, breakeven = calc(price, cost, sales, rent, labour, other)

    st.subheader("Result")

    st.write(f"Revenue: ${revenue:,.0f}")
    st.write(f"Cost: ${total:,.0f}")
    st.write(f"Profit: ${profit:,.0f}")

    if breakeven:
        st.write(f"Break-even: {breakeven:,.0f} per day")

    # ---------- Email Unlock ----------
    st.markdown("### Before you decide:")

    st.write("""
• Is this actually profitable, or just looks busy?  
• What happens if sales drop?  
• Where are the hidden risks?  
• What needs to change to make this work?
""")

    email = st.text_input("Enter email")

    if st.button("Get My Result"):
        if valid_email(email):
            st.session_state.pro_unlocked = True
            st.success("Analysis unlocked below ↓")
        else:
            st.error("Enter valid email")

# ---------- PRO ----------
if st.session_state.pro_unlocked:

    st.subheader("Should You Do This?")

    if profit < 0:
        st.error("Honestly — this doesn't look like a good idea.")
    elif profit < 5000:
        st.warning("This might work, but it's riskier than it looks.")
    else:
        st.success("This looks viable — but execution matters.")

    st.subheader("What’s Driving This")

    if profit < 0:
        st.write("• You're losing money in base case")

    if sales < breakeven:
        st.write("• Sales below break-even")

    st.subheader("What Needs to Change")

    if profit < 0:
        st.write("• Reduce rent or staff")

    if sales < breakeven:
        st.write("• Increase demand / location")

    st.subheader("Reality Check")

    st.write("""
A cafe can look busy and still lose money.

What matters is margin, cost control, and consistency — not just traffic.
""")
