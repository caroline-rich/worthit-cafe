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

# ---------- Setup Type ----------
setup_type = st.radio(
    t("Setup Type", "开店方式"),
    [t("New cafe (from scratch)", "从零开店"), t("Take over existing cafe", "接手现有咖啡店")]
)

# ---------- Defaults ----------
if setup_type == t("New cafe (from scratch)", "从零开店"):
    DEFAULT_INVEST = 280000
else:
    DEFAULT_INVEST = 150000  # lower fit-out cost for takeover

DEFAULT_RENT = 10000
DEFAULT_STAFF = 4
DEFAULT_SALARY = 4500
DEFAULT_OTHER = 5000
DEFAULT_PRICE = 5.5
DEFAULT_COST = 1.8
DEFAULT_SALES = 220

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

def payback_months(invest, profit):
    if profit <= 0:
        return None
    return invest / profit

def verdict_label(profit):
    if profit < 0:
        return t("🔴 Not Worth It", "🔴 不值得做")
    elif profit < 5000:
        return t("🟡 Borderline", "🟡 勉强可行")
    else:
        return t("🟢 Worth It", "🟢 值得做")

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

    # Base case
    if base_profit < 0:
        score -= 45
    elif base_profit < 5000:
        score -= 20

    # Downside
    if cons_profit < 0:
        score -= 25

    # Payback
    if months is None:
        score -= 20
    elif months > 48:
        score -= 20
    elif months > 30:
        score -= 10

    # Break-even buffer
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

# ---------- UI ----------
st.title("WorthIt? ☕")
st.write(t("Should you open a cafe in Melbourne?", "在墨尔本开咖啡店值得吗？"))
st.caption(t(
    "Default assumptions reflect a more realistic Melbourne operating environment.",
    "默认参数更接近墨尔本真实经营环境。"
))

# ---------- Hidden Cost Reality ----------
with st.expander(t("Where does the money go?", "钱都花在哪里？")):
    if lang == "English":
        st.write("• Fit-out / refurbishment")
        st.write("• Rent bond and upfront lease costs")
        st.write("• Equipment")
        st.write("• Cash buffer for the first few months")
        st.write("• Compliance, council, and unexpected setup costs")
    else:
        st.write("• 装修 / 改造")
        st.write("• 押金和前期租约成本")
        st.write("• 设备")
        st.write("• 前几个月的现金缓冲")
        st.write("• 合规、Council 和其他意外开店成本")

# ---------- Inputs ----------
col1, col2 = st.columns(2)

with col1:
    invest = st.number_input(t("Initial Investment", "初始投资"), value=DEFAULT_INVEST)
    rent = st.number_input(t("Monthly Rent", "每月租金"), value=DEFAULT_RENT)
    staff = st.number_input(t("Staff Count", "员工数量"), value=DEFAULT_STAFF)

with col2:
    salary = st.number_input(t("Salary per Staff", "每人月薪"), value=DEFAULT_SALARY)
    other = st.number_input(t("Other Fixed Costs", "其他固定成本"), value=DEFAULT_OTHER)

price = st.number_input(t("Average Price per Sale", "平均每单售价"), value=DEFAULT_PRICE)
cost = st.number_input(t("Average Cost per Sale", "平均每单成本"), value=DEFAULT_COST)
sales = st.number_input(t("Daily Sales", "日销量"), value=DEFAULT_SALES)

if st.button(t("Run Analysis", "开始分析")):
    st.session_state.analysis_done = True
    st.session_state.pro_unlocked = False

# ---------- Results ----------
if st.session_state.analysis_done:
    labour = staff * salary

    base = calc(price, cost, sales, rent, labour, other)
    cons = calc(price, cost * 1.05, sales * 0.8, rent, labour, other)
    opt = calc(price, cost, sales * 1.15, rent, labour, other)

    revenue = base["revenue"]
    total = base["total"]
    profit = base["profit"]
    breakeven = base["breakeven"]

    months = payback_months(invest, profit)
    gap = sales - breakeven if breakeven is not None else -999

    st.subheader(t("Base Result", "基础结果"))
    st.write(f"**{t('Revenue', '收入')}**: ${revenue:,.0f}")
    st.write(f"**{t('Cost', '成本')}**: ${total:,.0f}")
    st.write(f"**{t('Profit', '利润')}**: ${profit:,.0f}")

    if breakeven is not None:
        st.write(f"**{t('Break-even daily sales', '盈亏平衡日销量')}**: {breakeven:,.0f} {t('units/day', '单位/天')}")
    else:
        st.write(f"**{t('Break-even daily sales', '盈亏平衡日销量')}**: {t('Not calculable', '无法计算')}")

    st.markdown("### " + t("Before you decide", "在你决定之前"))
    if lang == "English":
        st.write("• Is this actually profitable, or just looks busy?")
        st.write("• What happens if sales drop or costs rise?")
        st.write("• Where are the hidden risks?")
        st.write("• What would need to change to make this work?")
    else:
        st.write("• 这个生意是真的赚钱吗，还是只是看起来很忙？")
        st.write("• 如果销量下降、成本上升，会发生什么？")
        st.write("• 隐藏的风险在哪里？")
        st.write("• 如果想把它做成，需要改变什么？")

    email = st.text_input(t("Enter email", "输入邮箱"))

    if st.button(t("Get My Full Analysis", "获取完整分析")):
        if valid_email(email):
            st.session_state.pro_unlocked = True
            st.success(t("Full analysis unlocked below ↓", "完整分析已解锁 ↓"))
        else:
            st.error(t("Please enter a valid email address.", "请输入有效邮箱地址。"))

# ---------- PRO ----------
if st.session_state.analysis_done and st.session_state.pro_unlocked:
    labour = staff * salary
    base = calc(price, cost, sales, rent, labour, other)
    cons = calc(price, cost * 1.05, sales * 0.8, rent, labour, other)
    opt = calc(price, cost, sales * 1.15, rent, labour, other)

    revenue = base["revenue"]
    total = base["total"]
    profit = base["profit"]
    breakeven = base["breakeven"]

    months = payback_months(invest, profit)
    gap = sales - breakeven if breakeven is not None else -999
    score = risk_score(profit, cons["profit"], months, gap)

    st.markdown("---")
    st.subheader(t("Pro Analysis", "专业分析"))

    # 1. Final decision
    st.markdown("### " + t("1. Final Decision", "1. 最终判断"))
    if score < 50:
        st.error(t(
            "Honestly — this does not look like a strong cafe opportunity right now.",
            "说实话，这个咖啡店项目目前看起来并不是一个很强的机会。"
        ))
    elif score < 75:
        st.warning(t(
            "This could work, but it is riskier and more fragile than it first appears.",
            "这个项目不是不能做，但它比表面看起来更脆弱、风险也更高。"
        ))
    else:
        st.success(t(
            "This looks reasonably workable on paper, although real execution will still determine the outcome.",
            "从模型上看，这个项目是可以做的，但最终结果仍然非常依赖实际执行。"
        ))

    # 2. Score summary
    st.markdown("### " + t("2. Score Summary", "2. 评分总结"))
    st.write(f"**{t('Risk Score', '风险评分')}**: {score}/100")
    st.write(f"**{t('Risk Level', '风险等级')}**: {risk_label(score)}")
    st.write(f"**{t('Payback View', '回本判断')}**: {payback_label(months)}")
    st.write(f"**{t('Decision Label', '决策标签')}**: {verdict_label(profit)}")

    # 3. What is driving the result
    st.markdown("### " + t("3. What Is Driving the Result", "3. 结果为什么会这样"))
    drivers = []

    if profit < 0:
        drivers.append(t(
            f"The base case is already loss-making at ${profit:,.0f} per month.",
            f"基础情景下，月利润已经是亏损 ${profit:,.0f}。"
        ))
    else:
        drivers.append(t(
            f"The base case shows monthly profit of ${profit:,.0f}.",
            f"基础情景下，月利润约为 ${profit:,.0f}。"
        ))

    if cons["profit"] < 0:
        drivers.append(t(
            f"In the conservative case, profit falls to ${cons['profit']:,.0f}, which means the model breaks under moderate pressure.",
            f"在保守情景下，利润降到 ${cons['profit']:,.0f}，说明这个模型在中等压力下就会失效。"
        ))
    else:
        drivers.append(t(
            f"In the conservative case, profit remains at ${cons['profit']:,.0f}, which suggests some resilience.",
            f"在保守情景下，利润仍有 ${cons['profit']:,.0f}，说明它有一定韧性。"
        ))

    if breakeven is not None:
        if gap < 0:
            drivers.append(t(
                f"Your expected daily sales are about {abs(gap):,.0f} units below break-even.",
                f"你的预期日销量比盈亏平衡点低约 {abs(gap):,.0f} 单位。"
            ))
        elif gap < 30:
            drivers.append(t(
                f"You are only {gap:,.0f} units/day above break-even, so the safety buffer is thin.",
                f"你每天只比盈亏平衡点高 {gap:,.0f} 单位，安全垫偏薄。"
            ))
        else:
            drivers.append(t(
                f"You are about {gap:,.0f} units/day above break-even, which gives some room for error.",
                f"你每天比盈亏平衡点高约 {gap:,.0f} 单位，说明还有一定犯错空间。"
            ))

    if months is None:
        drivers.append(t(
            "At the current base case, the business does not recover the initial investment.",
            "按当前基础情景，这个生意无法回收初始投资。"
        ))
    elif months > 30:
        drivers.append(t(
            f"Payback is about {months:,.1f} months, which is slow for a cafe.",
            f"回本周期约为 {months:,.1f} 个月，对咖啡店来说偏慢。"
        ))
    else:
        drivers.append(t(
            f"Payback is about {months:,.1f} months, which is within a more reasonable range.",
            f"回本周期约为 {months:,.1f} 个月，算是相对合理的区间。"
        ))

    for d in drivers:
        st.write("• " + d)

    # 4. Biggest risks
    st.markdown("### " + t("4. Biggest Risks", "4. 最大风险点"))
    risks = []

    if profit < 0:
        risks.append(t(
            "The model loses money even before real-world execution issues are considered.",
            "在还没考虑现实执行偏差之前，这个模型本身就已经亏钱。"
        ))
    if cons["profit"] < 0:
        risks.append(t(
            "A mild downside scenario turns the business loss-making.",
            "只要出现温和的下行情景，这个生意就会亏损。"
        ))
    if gap < 0:
        risks.append(t(
            "The current expected sales level is not enough to support the business.",
            "当前预期销量不足以支撑这个生意。"
        ))
    if months is not None and months > 30:
        risks.append(t(
            "Capital is tied up for too long before being recovered.",
            "资金被占用的时间太长，回收速度偏慢。"
        ))
    if rent >= 12000:
        risks.append(t(
            "Rent is high enough to create major fixed-cost pressure.",
            "租金已经高到会对固定成本形成明显压力。"
        ))
    if staff >= 5:
        risks.append(t(
            "The staffing model may be too heavy for the current sales assumption.",
            "按当前销量假设，这个人员配置可能偏重。"
        ))

    if not risks:
        risks.append(t(
            "There are no obvious structural red flags, but execution risk still matters.",
            "目前没有特别明显的结构性红旗，但执行风险仍然很重要。"
        ))

    for r in risks:
        st.write("• " + r)

    # 5. What needs to change
    st.markdown("### " + t("5. What Needs to Change", "5. 如果要做，需要改变什么"))
    changes = []

    if profit < 0:
        changes.append(t(
            "You need to reduce fixed costs — especially rent, staffing, or both.",
            "你需要降低固定成本，尤其是租金、人员配置，或者两者都降。"
        ))
    if gap < 0:
        changes.append(t(
            "You need materially higher daily sales. That usually means a better location, stronger foot traffic, or a better offer.",
            "你需要明显更高的日销量。这通常意味着更好的地段、更强的客流，或者更有吸引力的产品。"
        ))
    elif gap < 30:
        changes.append(t(
            "You need a larger buffer above break-even. Right now there is too little room for error.",
            "你需要更大的安全垫。现在留给犯错的空间太小了。"
        ))
    if cons["profit"] < 0:
        changes.append(t(
            "You need more downside protection, because the current assumptions are still too optimistic.",
            "你需要更强的下行保护，因为目前的假设仍然偏乐观。"
        ))
    if months is not None and months > 30:
        changes.append(t(
            "You need faster capital recovery — either through better margins, stronger daily sales, or lower setup cost.",
            "你需要更快回本——要么提高利润率，要么提升日销量，要么降低前期投入。"
        ))

    if not changes:
        changes.append(t(
            "The model already looks relatively healthy. The focus should be on execution discipline, staffing efficiency, and demand consistency.",
            "这个模型整体已经相对健康。接下来重点应放在执行纪律、人员效率和需求稳定性上。"
        ))

    for c in changes:
        st.write("• " + c)

    # 6. Scenario comparison
    st.markdown("### " + t("6. Scenario Comparison", "6. 情景对比"))
    st.write(f"**{t('Conservative Case Profit', '保守情景利润')}**: ${cons['profit']:,.0f}")
    st.write(f"**{t('Base Case Profit', '基础情景利润')}**: ${profit:,.0f}")
    st.write(f"**{t('Optimistic Case Profit', '乐观情景利润')}**: ${opt['profit']:,.0f}")

    if cons["profit"] < 0 and opt["profit"] > 0:
        st.write(t(
            "This is a highly execution-sensitive business: it can work, but only if reality stays close to your optimistic assumptions.",
            "这是一个非常依赖执行的生意：它不是不能做，但只有现实接近乐观假设时才更容易成立。"
        ))
    elif cons["profit"] >= 0:
        st.write(t(
            "The model still holds up under downside pressure, which is a strong sign.",
            "即使在下行情景下，这个模型仍能成立，这是一个比较强的信号。"
        ))
    else:
        st.write(t(
            "The model is not robust enough yet. Small changes in reality can break it.",
            "这个模型还不够稳健，现实中的小波动就可能把它打穿。"
        ))

    # 7. Reality check
    st.markdown("### " + t("7. Reality Check", "7. 现实提醒"))
    st.write(t(
        "A cafe can look busy and still lose money.",
        "咖啡店可以看起来很忙，但仍然亏钱。"
    ))
    st.write(t(
        "What matters is margin, cost control, staff efficiency, and consistency — not just traffic.",
        "真正重要的是利润率、成本控制、人员效率和稳定性，而不只是客流。"
    ))

    # 8. Plain-English summary
    st.markdown("### " + t("8. Plain-English Summary", "8. 大白话总结"))
    if score < 50:
        st.write(t(
            "If this were my money, I would not rush into it. The model is too weak in its current form.",
            "如果这是我自己的钱，我不会急着做。以现在的模型来看，它还不够强。"
        ))
    elif score < 75:
        st.write(t(
            "This can work, but you should assume it will be harder than it looks. You need more buffer.",
            "这个项目不是不能做，但你要默认它会比看起来更难。你需要更大的安全垫。"
        ))
    else:
        st.write(t(
            "This is one of the better-looking cases — but success still depends on execution, not just the spreadsheet.",
            "这是相对更好看的情况之一——但最终成不成，仍然取决于执行，而不只是表格。"
        ))
