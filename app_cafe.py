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
    padding-top: 1.4rem;
    padding-bottom: 3rem;
    max-width: 980px;
}
.hero-box {
    padding: 1.2rem 1.3rem;
    border-radius: 16px;
    border: 1px solid rgba(128,128,128,0.22);
    margin-bottom: 1rem;
}
.alert-box {
    padding: 12px 14px;
    border-radius: 12px;
    border: 1px solid rgba(255,0,0,0.18);
    background-color: rgba(255,0,0,0.05);
    margin-bottom: 12px;
}
.summary-box {
    padding: 12px 14px;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,0.2);
    background-color: rgba(250,250,250,0.7);
    margin-bottom: 12px;
}
.small-note {
    opacity: 0.75;
    font-size: 0.92rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- Email ----------
def valid_email(email: str) -> bool:
    return len(email) > 5 and "@" in email and "." in email

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
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)

# ---------- Setup Type ----------
setup_type = st.radio(
    t("Setup Type", "开店方式"),
    [t("New cafe (from scratch)", "从零开店"), t("Take over existing cafe", "接手现有咖啡店")]
)

# ---------- Market-Informed Defaults ----------
if setup_type == t("New cafe (from scratch)", "从零开店"):
    DEFAULT_INVEST = 290000
    DEFAULT_RENT = 10000
    DEFAULT_STAFF = 4
    DEFAULT_SALARY = 4500
    DEFAULT_OTHER = 5000
    DEFAULT_PRICE = 5.5
    DEFAULT_COST = 1.9
    DEFAULT_SALES = 200
else:
    DEFAULT_INVEST = 150000
    DEFAULT_RENT = 9500
    DEFAULT_STAFF = 4
    DEFAULT_SALARY = 4500
    DEFAULT_OTHER = 4500
    DEFAULT_PRICE = 5.5
    DEFAULT_COST = 1.8
    DEFAULT_SALES = 230

# ---------- Core Calculations ----------
def calc(price, cost, sales, rent, labour, other):
    revenue = price * sales * 30
    cogs = cost * sales * 30
    fixed = rent + labour + other
    total = fixed + cogs
    profit = revenue - total
    gross_margin_per_sale = price - cost
    gross_margin_pct = ((price - cost) / price) if price > 0 else 0
    breakeven = fixed / gross_margin_per_sale / 30 if gross_margin_per_sale > 0 else None

    return {
        "revenue": revenue,
        "cogs": cogs,
        "fixed": fixed,
        "total": total,
        "profit": profit,
        "gross_margin_per_sale": gross_margin_per_sale,
        "gross_margin_pct": gross_margin_pct,
        "breakeven": breakeven
    }

def payback_months(invest, profit):
    if profit <= 0:
        return None
    return invest / profit

def verdict_label(profit, months, gap):
    if profit < 0:
        return t("🔴 Not worth doing", "🔴 不建议做")
    if gap < 0:
        return t("🔴 Not worth doing", "🔴 不建议做")
    if months is None:
        return t("🔴 Not worth doing", "🔴 不建议做")
    if profit < 5000 or months > 36 or gap < 20:
        return t("🟡 Possible, but fragile", "🟡 能做，但很脆弱")
    return t("🟢 Looks workable", "🟢 整体可做")

def decision_message(profit, months, gap):
    if profit < 0 or gap < 0:
        return t(
            "At these assumptions, this does not look commercially sound.",
            "按这组假设看，这个项目在商业上不够成立。"
        )
    if profit < 5000 or (months is not None and months > 36) or gap < 20:
        return t(
            "This may work, but only with disciplined execution and very little room for mistakes.",
            "这个项目不是不能做，但前提是执行必须很稳，而且容错空间很小。"
        )
    return t(
        "This looks commercially workable on paper, although execution will still matter a lot.",
        "从纸面模型看，这个项目是能成立的，但最终仍然高度依赖执行。"
    )

def payback_label(months):
    if months is None:
        return t("Not recoverable", "无法回本")
    if months <= 18:
        return t("Fast return", "回本较快")
    if months <= 30:
        return t("Acceptable", "回本可接受")
    if months <= 48:
        return t("Slow return", "回本偏慢")
    return t("Too slow", "回本过慢")

def risk_score(base_profit, cons_profit, months, gap, gross_margin_pct):
    score = 100

    if base_profit < 0:
        score -= 35
    elif base_profit < 5000:
        score -= 18

    if cons_profit < 0:
        score -= 22
    elif cons_profit < 5000:
        score -= 10

    if months is None:
        score -= 18
    elif months > 48:
        score -= 18
    elif months > 36:
        score -= 10
    elif months > 24:
        score -= 5

    if gap < 0:
        score -= 20
    elif gap < 15:
        score -= 12
    elif gap < 30:
        score -= 6

    if gross_margin_pct < 0.6:
        score -= 10
    elif gross_margin_pct < 0.65:
        score -= 5

    return max(0, min(100, int(round(score))))

def risk_label(score):
    if score >= 75:
        return t("🟢 Low to Moderate Risk", "🟢 低到中等风险")
    if score >= 55:
        return t("🟡 Medium Risk", "🟡 中等风险")
    return t("🔴 High Risk", "🔴 高风险")

def executive_summary(score, profit, cons_profit, months, gap):
    if score < 55:
        return t(
            "This model is currently too weak. The downside case breaks too easily, and the business is not protected against normal operating pressure.",
            "这个模型目前偏弱。下行情景太容易失效，面对正常经营压力时，安全垫不够。"
        )
    if score < 75:
        return t(
            "This business may work, but the model is fragile. It needs tighter cost control, cleaner execution, and a bigger sales buffer.",
            "这个项目有可能能做，但模型偏脆弱。它需要更严格的成本控制、更稳定的执行，以及更大的销量安全垫。"
        )
    return t(
        "This model looks relatively workable on paper. It is not obviously broken, but success will still depend on location, labour discipline, and repeat demand.",
        "这个模型在纸面上相对成立。它没有明显结构性问题，但最终成败仍取决于地段、人工纪律和复购需求。"
    )

def top_priorities(base_profit, cons_profit, months, gap):
    priorities = []

    if gap < 0:
        priorities.append(t(
            "Lift daily sales above break-even through better location, stronger foot traffic, or a sharper offer.",
            "把日销量拉到盈亏平衡点以上——靠更好的地段、更强的客流或更有竞争力的产品。"
        ))

    if base_profit < 0:
        priorities.append(t(
            "Reduce fixed costs, especially rent and staffing.",
            "降低固定成本，尤其是租金和人工。"
        ))

    if cons_profit < 0:
        priorities.append(t(
            "Build more downside protection because the current assumptions are still too optimistic.",
            "建立更强的下行保护，因为目前的假设仍然偏乐观。"
        ))

    if months is not None and months > 30:
        priorities.append(t(
            "Improve payback speed by raising margin, lifting sales, or reducing upfront capital.",
            "通过提高利润率、提升销量或降低前期投入，改善回本速度。"
        ))

    if not priorities:
        priorities.append(t(
            "Protect gross margin and don't let wages drift too high.",
            "保护毛利率，不要让人工成本失控。"
        ))
        priorities.append(t(
            "Stress-test slower weekdays, not just good weekends.",
            "要测试工作日慢时段，而不是只看好周末。"
        ))
        priorities.append(t(
            "Keep execution disciplined before expanding staffing.",
            "在人手扩张前先保持执行纪律。"
        ))

    return priorities[:3]

def scenario_note(base_profit, cons_profit, opt_profit):
    if cons_profit < 0 and opt_profit > 0:
        return t(
            "This is highly execution-sensitive: it can work, but only if reality stays close to your stronger assumptions.",
            "这是一个高度依赖执行的项目：它不是不能做，但只有现实接近较强假设时才更容易成立。"
        )
    if cons_profit >= 0:
        return t(
            "The model still holds up in a softer case, which is a meaningful positive sign.",
            "即使在更弱的情景下模型仍能成立，这是一个比较强的正面信号。"
        )
    return t(
        "The model is not robust enough yet. Small changes in reality can break it.",
        "这个模型目前还不够稳健，现实中的小波动就可能把它打穿。"
    )

# ---------- Header ----------
st.markdown(f"""
<div class="hero-box">
    <h1 style="margin-bottom:0.35rem;">WorthIt? ☕</h1>
    <div>{t("Should you open a cafe in Melbourne?", "在墨尔本开咖啡店值得吗？")}</div>
    <div class="small-note" style="margin-top:0.45rem;">
        {t("Market-informed default assumptions for Melbourne cafe economics.", "基于墨尔本市场现实设定的默认参数。")}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="summary-box">
<b>{t("Why these defaults?", "为什么默认值这样设？")}</b><br><br>
{t(
    "These defaults are designed to reflect a more realistic Melbourne cafe setup, not an overly optimistic spreadsheet. A new cafe usually needs heavier upfront capital for fit-out, equipment and opening cash buffer. A take-over usually starts with lower upfront capital, but ongoing rent, labour and demand risk still matter.",
    "这些默认值是为了更接近墨尔本咖啡店的真实经营环境，而不是一个过度乐观的表格模型。从零开店通常需要更重的前期投入，包括装修、设备和开业现金缓冲；接手现有店虽然前期投入通常较低，但租金、人工和客流风险仍然真实存在。"
)}
</div>
""", unsafe_allow_html=True)

with st.expander(t("Why are New vs Take Over defaults different?", "为什么从零开店和接手店默认值不同？")):
    st.write(t(
        "A new cafe usually needs much heavier upfront capital for fit-out, equipment, approvals, and opening cash buffer. A take-over usually starts with lower upfront capital, but the ongoing operating pressure is still real.",
        "从零开店通常需要更重的前期投入，包括装修、设备、审批和开业现金缓冲；接手现有店的前期投入通常更低，但持续经营压力仍然存在。"
    ))

# ---------- Inputs ----------
col1, col2 = st.columns(2)

with col1:
    invest = st.number_input(t("Initial Investment", "初始投资"), value=DEFAULT_INVEST, step=5000)
    rent = st.number_input(t("Monthly Rent", "每月租金"), value=DEFAULT_RENT, step=500)
    staff = st.number_input(t("Staff Count", "员工数量"), value=DEFAULT_STAFF, step=1)

with col2:
    salary = st.number_input(t("Salary per Staff", "每人月薪"), value=DEFAULT_SALARY, step=250)
    other = st.number_input(t("Other Fixed Costs", "其他固定成本"), value=DEFAULT_OTHER, step=250)

price = st.number_input(t("Average Price per Sale", "平均每单售价"), value=DEFAULT_PRICE, step=0.1)
cost = st.number_input(t("Average Cost per Sale", "平均每单成本"), value=DEFAULT_COST, step=0.1)
sales = st.number_input(t("Daily Sales", "日销量"), value=DEFAULT_SALES, step=5)

if st.button(t("Run Analysis", "开始分析")):
    st.session_state.analysis_done = True
    st.session_state.pro_unlocked = False

# ---------- Results ----------
if st.session_state.analysis_done:
    labour = staff * salary

    base = calc(price, cost, sales, rent, labour, other)
    cons = calc(price, cost * 1.08, sales * 0.82, rent, labour, other)
    opt = calc(price, cost, sales * 1.12, rent, labour, other)

    profit = base["profit"]
    months = payback_months(invest, profit)
    gap = sales - base["breakeven"] if base["breakeven"] is not None else -999
    score = risk_score(profit, cons["profit"], months, gap, base["gross_margin_pct"])
    verdict = verdict_label(profit, months, gap)

    st.markdown(f"""
    <div class="alert-box">
        <b>{t("Most people underestimate cafe costs by 20–30%.",
              "大多数人会低估咖啡店成本 20–30%。")}</b><br>
        {t("A small modelling error can flip a 'good-looking' cafe into a bad investment.",
           "一个小小的建模误差，就可能把“看起来不错”的咖啡店变成坏投资。")}
    </div>
    """, unsafe_allow_html=True)

    st.subheader(t("Base Result", "基础结果"))

    c1, c2, c3 = st.columns(3)
    c1.metric(t("Monthly Revenue Run-Rate", "月收入水平"), f"${base['revenue']:,.0f}")
    c2.metric(t("Estimated Monthly Operating Profit", "预计月经营利润"), f"${profit:,.0f}")
    c3.metric(
        t("Break-even Volume / Day", "盈亏平衡日单量"),
        t("N/A", "无法计算") if base["breakeven"] is None else f"{base['breakeven']:,.0f}"
    )

    st.markdown("### " + t("Can you do it?", "这个项目能做吗？"))
    st.write(f"**{verdict}**")
    st.write(decision_message(profit, months, gap))

    if profit < 0 or gap < 0:
        st.error(t(
            "Based on these inputs: no — not in its current form.",
            "按这组输入看：不建议——至少以目前形式不建议做。"
        ))
    elif profit < 5000 or (months is not None and months > 36) or gap < 20:
        st.warning(t(
            "Based on these inputs: maybe — but the model is fragile.",
            "按这组输入看：勉强能做——但模型偏脆弱。"
        ))
    else:
        st.success(t(
            "Based on these inputs: yes — this looks commercially workable on paper.",
            "按这组输入看：可以——纸面上商业逻辑是成立的。"
        ))

    st.markdown("### " + t("Get Full Risk Breakdown", "获取完整风险分析"))
    st.write(t(
        "This is not just a calculator. It shows whether the cafe actually has enough economics to survive.",
        "这不只是一个计算器，而是在判断这家咖啡店的经济模型是否真的足以活下来。"
    ))

    email = st.text_input(t("Enter your email", "输入邮箱"))
    st.caption(t("Free · No spam · Instant access", "免费 · 不骚扰 · 即时解锁"))

    if st.button(t("Unlock Full Risk Breakdown (Free)", "免费解锁完整风险分析")):
        if valid_email(email):
            save_ok, save_error = save_to_airtable(
                email=email,
                language=lang,
                setup_type=setup_type,
                invest=invest,
                rent=rent,
                staff=staff,
                salary=salary,
                other=other,
                price=price,
                cost=cost,
                sales=sales,
                profit=profit,
                risk_score_value=score
            )
            st.session_state.pro_unlocked = True

            if save_ok:
                st.success(t(
                    "Full analysis unlocked ↓",
                    "完整分析已解锁 ↓"
                ))
            else:
                st.warning(t(
                    "Analysis unlocked, but lead saving failed.",
                    "分析已解锁，但邮箱保存失败。"
                ))
                st.caption(save_error)
        else:
            st.error(t("Please enter a valid email address.", "请输入有效邮箱地址。"))

# ---------- Pro ----------
if st.session_state.analysis_done and st.session_state.pro_unlocked:
    labour = staff * salary

    base = calc(price, cost, sales, rent, labour, other)
    cons = calc(price, cost * 1.08, sales * 0.82, rent, labour, other)
    opt = calc(price, cost, sales * 1.12, rent, labour, other)

    profit = base["profit"]
    months = payback_months(invest, profit)
    gap = sales - base["breakeven"] if base["breakeven"] is not None else -999
    score = risk_score(profit, cons["profit"], months, gap, base["gross_margin_pct"])

    st.markdown("---")
    st.subheader(t("Full Risk Breakdown", "完整风险拆解"))

    # 1 Executive summary
    st.markdown("### " + t("1. Executive Summary", "1. 执行摘要"))
    st.caption(t(
        "This is a simplified operating view, not a formal valuation, tax model, or accounting forecast.",
        "这是一个简化的经营判断视角，不是正式估值、税务模型或会计预测。"
    ))
    st.markdown(f"""
    <div class="summary-box">
    <b>{risk_label(score)}</b><br><br>
    {executive_summary(score, profit, cons["profit"], months, gap)}
    </div>
    """, unsafe_allow_html=True)

    # 2 Final decision
    st.markdown("### " + t("2. Final Decision", "2. 最终判断"))
    st.write(f"**{t('Decision', '判断')}**: {verdict_label(profit, months, gap)}")
    st.write(f"**{t('Payback View', '回本判断')}**: {payback_label(months)}")
    if months is not None:
        st.write(f"**{t('Estimated Payback', '预计回本周期')}**: {months:,.1f} {t('months', '个月')}")
    else:
        st.write(f"**{t('Estimated Payback', '预计回本周期')}**: {t('Not recoverable at current base case', '按当前基础情景无法回本')}")

    # 3 Unit economics
    st.markdown("### " + t("3. Unit Economics", "3. 单位经济模型"))
    st.write(f"**{t('Average selling price', '平均售价')}**: ${price:,.2f}")
    st.write(f"**{t('Average direct cost', '平均直接成本')}**: ${cost:,.2f}")
    st.write(f"**{t('Gross margin per sale', '单笔毛利')}**: ${base['gross_margin_per_sale']:,.2f}")
    st.write(f"**{t('Gross margin %', '毛利率')}**: {base['gross_margin_pct']*100:,.1f}%")
    if base["gross_margin_pct"] < 0.6:
        st.warning(t(
            "The gross margin is thin for a cafe model. Small input errors will hurt quickly.",
            "这个咖啡店模型的毛利率偏薄，输入稍有偏差就会很快受伤。"
        ))
    else:
        st.success(t(
            "The gross margin is not the main problem. Execution and cost control matter more.",
            "毛利率本身不是最核心的问题，更关键的是执行和成本控制。"
        ))

    # 4 Break-even
    st.markdown("### " + t("4. Break-even Analysis", "4. 盈亏平衡分析"))
    if base["breakeven"] is not None:
        st.write(f"**{t('Break-even sales needed', '达到盈亏平衡所需日销量')}**: {base['breakeven']:,.0f} {t('sales/day', '单/天')}")
        st.write(f"**{t('Your assumed sales', '你的假设日销量')}**: {sales:,.0f} {t('sales/day', '单/天')}")
        st.write(f"**{t('Buffer vs break-even', '相对盈亏平衡的安全垫')}**: {gap:,.0f} {t('sales/day', '单/天')}")
        if gap < 0:
            st.error(t(
                "You are below break-even. The model loses money before allowing for normal real-world variance.",
                "你低于盈亏平衡点。还没考虑现实波动，这个模型就已经亏钱了。"
            ))
        elif gap < 20:
            st.warning(t(
                "You are only slightly above break-even. This is a fragile operating model.",
                "你只比盈亏平衡略高一点，这个经营模型很脆弱。"
            ))
        else:
            st.success(t(
                "You have a meaningful buffer above break-even, which gives the model more resilience.",
                "你在盈亏平衡点之上有一定缓冲，这会让模型更有韧性。"
            ))
    else:
        st.error(t(
            "Break-even cannot be calculated because margin per sale is not positive.",
            "由于单笔毛利不是正数，无法计算盈亏平衡点。"
        ))

    # 5 Cost structure
    st.markdown("### " + t("5. Cost Structure", "5. 成本结构"))
    rent_share = rent / base["total"] if base["total"] > 0 else 0
    labour_share = labour / base["total"] if base["total"] > 0 else 0
    cogs_share = base["cogs"] / base["total"] if base["total"] > 0 else 0
    other_share = other / base["total"] if base["total"] > 0 else 0

    st.write(f"**{t('Rent', '租金')}**: ${rent:,.0f} ({rent_share*100:,.1f}%)")
    st.write(f"**{t('Labour', '人工')}**: ${labour:,.0f} ({labour_share*100:,.1f}%)")
    st.write(f"**{t('COGS', '原料成本')}**: ${base['cogs']:,.0f} ({cogs_share*100:,.1f}%)")
    st.write(f"**{t('Other fixed costs', '其他固定成本')}**: ${other:,.0f} ({other_share*100:,.1f}%)")

    largest_cost = max(
        [("rent", rent_share), ("labour", labour_share), ("cogs", cogs_share), ("other", other_share)],
        key=lambda x: x[1]
    )[0]

    if largest_cost == "labour":
        st.write(t(
            "Labour is the heaviest cost block. That means rostering discipline and sales productivity matter a lot.",
            "人工是最大的成本块，这意味着排班纪律和人效非常重要。"
        ))
    elif largest_cost == "rent":
        st.write(t(
            "Rent is the heaviest cost block. That means location quality must justify the fixed-cost burden.",
            "租金是最大的成本块，这意味着地段质量必须足以支撑这部分固定成本。"
        ))
    elif largest_cost == "cogs":
        st.write(t(
            "Direct product cost is carrying a lot of weight. Margin control matters more than it looks.",
            "原料成本占比很高，毛利控制比看起来更重要。"
        ))
    else:
        st.write(t(
            "Other fixed costs are heavier than expected. The overhead structure needs to stay disciplined.",
            "其他固定成本比预期更重，整体费用结构需要保持纪律。"
        ))

    # 6 Scenario comparison
    st.markdown("### " + t("6. Scenario Comparison", "6. 情景对比"))
    st.write(f"**{t('Conservative case profit', '保守情景利润')}**: ${cons['profit']:,.0f}")
    st.write(f"**{t('Base case profit', '基础情景利润')}**: ${base['profit']:,.0f}")
    st.write(f"**{t('Optimistic case profit', '乐观情景利润')}**: ${opt['profit']:,.0f}")
    st.write(scenario_note(base["profit"], cons["profit"], opt["profit"]))

    # 7 Sensitivity
    st.markdown("### " + t("7. Sensitivity Check", "7. 敏感性检查"))
    sales_down_10 = calc(price, cost, sales * 0.9, rent, labour, other)["profit"]
    cost_up_10 = calc(price, cost * 1.1, sales, rent, labour, other)["profit"]
    rent_up_10 = calc(price, cost, sales, rent * 1.1, labour, other)["profit"]

    st.write(f"**{t('If sales fall 10%', '如果销量下降 10%')}**: ${sales_down_10:,.0f}")
    st.write(f"**{t('If direct cost rises 10%', '如果直接成本上升 10%')}**: ${cost_up_10:,.0f}")
    st.write(f"**{t('If rent rises 10%', '如果租金上升 10%')}**: ${rent_up_10:,.0f}")

    biggest_hit = min(
        [("sales", sales_down_10), ("cost", cost_up_10), ("rent", rent_up_10)],
        key=lambda x: x[1]
    )[0]

    if biggest_hit == "sales":
        st.write(t(
            "The model is most sensitive to demand. Foot traffic and repeat business are doing most of the heavy lifting.",
            "这个模型对需求最敏感，客流和复购在承担最大的成败压力。"
        ))
    elif biggest_hit == "cost":
        st.write(t(
            "The model is most sensitive to input cost inflation. Margin discipline matters.",
            "这个模型对成本通胀最敏感，毛利纪律很重要。"
        ))
    else:
        st.write(t(
            "The model is highly exposed to occupancy cost. Rent quality really matters here.",
            "这个模型对租金非常敏感，地段质量在这里真的很关键。"
        ))

    # 8 Biggest risks
    st.markdown("### " + t("8. Biggest Risks", "8. 最大风险点"))
    risks = []

    if profit < 0:
        risks.append(t(
            "The base case is already loss-making.",
            "基础情景本身已经亏损。"
        ))
    if cons["profit"] < 0:
        risks.append(t(
            "A modest downside case turns the model loss-making.",
            "只要出现温和下行情景，模型就会转亏。"
        ))
    if gap < 0:
        risks.append(t(
            "Expected daily sales are below break-even.",
            "预期日销量低于盈亏平衡点。"
        ))
    if months is not None and months > 36:
        risks.append(t(
            "Capital recovery is too slow for this type of small business risk.",
            "对于这种小生意风险级别来说，资金回收太慢。"
        ))
    if staff >= 5:
        risks.append(t(
            "The staffing model may be too heavy for the current sales assumption.",
            "按当前销量假设，这个人员配置可能偏重。"
        ))
    if rent >= 12000:
        risks.append(t(
            "Rent is high enough to create meaningful fixed-cost pressure.",
            "租金已经高到会形成明显固定成本压力。"
        ))
    if base["gross_margin_pct"] < 0.6:
        risks.append(t(
            "Margin per sale is thinner than ideal for a resilient cafe model.",
            "单笔毛利偏薄，不利于形成有韧性的咖啡店模型。"
        ))

    if not risks:
        risks.append(t(
            "There are no major structural red flags in the current inputs, but execution risk still matters.",
            "按当前输入没有明显的结构性红旗，但执行风险依然重要。"
        ))

    for r in risks:
        st.write("• " + r)

    # 9 Priorities
    st.markdown("### " + t("9. Top 3 Priorities", "9. 最优先的三件事"))
    priorities = top_priorities(base["profit"], cons["profit"], months, gap)
    for i, p in enumerate(priorities, start=1):
        st.write(f"**{i}.** {p}")

    # 10 What needs to change
    st.markdown("### " + t("10. What Needs to Change", "10. 如果要做，需要改变什么"))
    changes = []
    if profit < 0:
        changes.append(t(
            "You need a materially better operating model: lower rent, leaner labour, stronger demand, or some combination of the three.",
            "你需要一个明显更好的经营模型：更低租金、更轻人工、更强需求，或者三者组合。"
        ))
    if gap < 20:
        changes.append(t(
            "You need a larger sales buffer above break-even. Right now the model leaves too little room for error.",
            "你需要更大的销量安全垫。现在这个模型留给犯错的空间太小。"
        ))
    if cons["profit"] < 0:
        changes.append(t(
            "You need downside protection, because current assumptions are too easy to break.",
            "你需要更强的下行保护，因为当前假设太容易被打破。"
        ))
    if months is not None and months > 30:
        changes.append(t(
            "You need faster capital recovery, either through lower entry cost or better cash generation.",
            "你需要更快回本，要么降低进入成本，要么提升现金创造能力。"
        ))
    if not changes:
        changes.append(t(
            "The model is already in a relatively healthy range. The next job is disciplined execution, not spreadsheet heroics.",
            "这个模型已经落在相对健康区间。接下来更重要的是执行纪律，而不是继续在表格里做文章。"
        ))

    for c in changes:
        st.write("• " + c)

    # 11 Plain-English close
    st.markdown("### " + t("11. Plain-English Summary", "11. 大白话总结"))
    if score < 55:
        st.write(t(
            "If this were my money, I would not rush into it. The model is too weak in its current form.",
            "如果这是我自己的钱，我不会急着做。按现在的模型，它还不够强。"
        ))
    elif score < 75:
        st.write(t(
            "This can work, but it will probably be harder than the spreadsheet makes it look.",
            "这个项目不是不能做，但大概率会比表格看起来更难。"
        ))
    else:
        st.write(t(
            "This is one of the better-looking cases. It still needs execution, but it is not obviously broken.",
            "这是相对更好看的情况之一。它仍然需要执行，但至少不是明显有问题的模型。"
        ))
