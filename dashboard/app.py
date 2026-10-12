from pathlib import Path
from zipfile import ZipFile
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='RetailIQ | Retail intelligence', page_icon='🛍️', layout='wide')
ROOT = Path(__file__).resolve().parents[1]
COLOR = '#0d9488'

@st.cache_data(show_spinner='Preparing Olist data…')
def load_data():
    with ZipFile(ROOT / 'data' / 'archive (4).zip') as z:
        def read(name, cols):
            with z.open(name) as f:
                return pd.read_csv(f, usecols=cols)
        orders = read('olist_orders_dataset.csv', ['order_id','customer_id','order_status','order_purchase_timestamp','order_delivered_customer_date','order_estimated_delivery_date'])
        customers = read('olist_customers_dataset.csv', ['customer_id','customer_unique_id','customer_state'])
        payments = read('olist_order_payments_dataset.csv', ['order_id','payment_value'])
        reviews = read('olist_order_reviews_dataset.csv', ['order_id','review_score'])
        items = read('olist_order_items_dataset.csv', ['order_id','seller_id','price'])
        sellers = read('olist_sellers_dataset.csv', ['seller_id','seller_state'])
    # Aggregate one-to-many tables before joins: never multiply payment totals.
    payments = payments.groupby('order_id', as_index=False).payment_value.sum()
    reviews = reviews.groupby('order_id', as_index=False).review_score.mean()
    orders = orders.merge(customers, on='customer_id', validate='many_to_one')
    orders = orders.merge(payments, on='order_id', how='left', validate='one_to_one')
    orders = orders.merge(reviews, on='order_id', how='left', validate='one_to_one')
    for col in ['order_purchase_timestamp','order_delivered_customer_date','order_estimated_delivery_date']:
        orders[col] = pd.to_datetime(orders[col], errors='coerce')
    orders['month'] = orders.order_purchase_timestamp.dt.to_period('M').astype(str)
    orders['delivery_days'] = (orders.order_delivered_customer_date-orders.order_purchase_timestamp).dt.total_seconds()/86400
    orders['delay_days'] = (orders.order_delivered_customer_date-orders.order_estimated_delivery_date).dt.total_seconds()/86400
    return orders, items.merge(sellers, on='seller_id', validate='many_to_one')


def customer_summary(frame):
    snapshot = frame.order_purchase_timestamp.max() + pd.Timedelta(days=1)
    result = frame.groupby('customer_unique_id').agg(
        orders=('order_id','nunique'), spend=('payment_value','sum'),
        last_purchase=('order_purchase_timestamp','max'))
    result['recency_days'] = (snapshot-result.last_purchase).dt.days
    result['segment'] = 'One-time, recent'
    result.loc[result.orders >= 2, 'segment'] = 'Repeat, recent'
    result.loc[result.recency_days >= 90, 'segment'] = 'One-time, inactive 90+ days'
    result.loc[(result.orders >= 2) & (result.recency_days >= 90), 'segment'] = 'Repeat, inactive 90+ days'
    return result


def chart(fig):
    fig.update_layout(template='plotly_white', height=370, paper_bgcolor='white', plot_bgcolor='white', font=dict(family='Arial',color='#52647b',size=12), title_font=dict(size=16,color='#16243a'), margin=dict(l=25,r=25,t=60,b=30), colorway=['#087f73','#3979b7','#93b9b0','#dfb86c','#8490b8'])
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(gridcolor='#eef2f7', zeroline=False, automargin=True)
    st.plotly_chart(fig, use_container_width=True)

st.markdown('\n<style>\n.stApp{background:#f4f7fb;color:#16243a}\n[data-testid="stHeader"]{background:rgba(244,247,251,.96)}\n.block-container{padding-top:2.4rem;padding-bottom:2rem;max-width:1440px}\nh1,h2,h3{letter-spacing:-.035em;color:#16243a}\nh3{font-size:1.35rem!important}\n[data-testid="stSidebar"]{background:#fff;border-right:1px solid #e2e8f0}\n[data-testid="stSidebar"] .block-container{padding-top:2rem}\n[data-testid="stMetric"]{background:#fff;border:1px solid #e0e8f1;border-radius:16px;padding:19px 20px;box-shadow:0 4px 16px #172b4d05;min-height:118px}\n[data-testid="stMetricLabel"]{color:#5b6b82;font-size:.8rem}\n[data-testid="stMetricValue"]{font-size:clamp(1.35rem,2vw,2rem);font-weight:650;letter-spacing:-.04em}\n[data-testid="stCaptionContainer"]{color:#607087}\n[data-testid="stVerticalBlockBorderWrapper"]>div{border-radius:16px}\n[data-testid="stPlotlyChart"], [data-testid="stDataFrame"]{background:white;border:1px solid #e0e8f1;border-radius:16px;overflow:hidden}\n[data-baseweb="tab-list"]{gap:8px;background:#e9eef5;border-radius:12px;padding:5px;margin-bottom:22px}\nbutton[data-baseweb="tab"]{padding:10px 20px;border-radius:9px;height:44px}\nbutton[data-baseweb="tab"][aria-selected="true"]{background:white;color:#087f73;box-shadow:0 2px 6px #172b4d10}\n[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none}\n.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:#087f73;border:0;border-radius:10px;min-height:46px;font-weight:650}\n.stButton>button,.stDownloadButton>button{border-radius:10px}\n[data-testid="stFileUploaderDropzone"]{border:1px dashed #91abc6;border-radius:16px;background:#edf4fb;padding:28px}\n[data-testid="stAlert"]{border-radius:12px}\n[data-testid="stSidebar"] [role="radiogroup"]{gap:4px}\n[data-testid="stSidebar"] [role="radiogroup"] label{padding:10px 12px;border-radius:10px}\n[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#e8f3f2;font-weight:600}\n.brand{display:flex;align-items:center;gap:10px;font-weight:750;font-size:21px;letter-spacing:-.7px;margin-bottom:22px}\n.brand-mark{background:#087f73;color:white;display:inline-flex;align-items:center;justify-content:center;width:35px;height:35px;border-radius:10px;font-size:17px}\n.hero{background:linear-gradient(110deg,#112339,#203e57);color:white;border-radius:22px;padding:32px 36px;margin:8px 0 28px;position:relative;overflow:hidden;border:1px solid #314d66}\n.hero h1{color:white!important;font-size:clamp(2rem,3.5vw,3rem);font-weight:720;margin:8px 0 12px;padding:0;max-width:850px}\n.hero p{color:#c6d6e7;max-width:750px;line-height:1.6;margin:0}\n.eyebrow{color:#8de0cf;font-size:11px;letter-spacing:2px;font-weight:700;text-transform:uppercase}\n.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:22px}\n.chip{font-size:11px;padding:6px 11px;border:1px solid #536b80;border-radius:6px;color:#e2edf7}\n.empty{border:1px dashed #c6d3e0;background:#f9fbfd;border-radius:16px;padding:48px 26px;text-align:center;color:#66788f;min-height:235px}\n.empty strong{display:block;color:#243c55;font-size:19px;margin:14px 0 9px}\n.section-label{font-size:11px;font-weight:750;letter-spacing:1.5px;color:#087f73;text-transform:uppercase;margin:4px 0 10px}\n.footer{border-top:1px solid #dce5ef;padding-top:18px;margin-top:36px;font-size:11px;color:#6a7b90;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}\n@media(max-width:768px){.block-container{padding:1.5rem 1rem}.hero{padding:25px 22px}.hero h1{font-size:2rem} [data-testid="stMetric"]{padding:15px;min-height:100px}[data-testid="stMetricValue"]{font-size:1.6rem}button[data-baseweb="tab"]{padding:8px 12px;font-size:12px}}\n</style>\n', unsafe_allow_html=True)
st.markdown('<div class="brand"><span class="brand-mark">R</span>RetailIQ</div><div class="hero"><div class="eyebrow">Commerce intelligence</div><h1>Every order. A clearer picture.</h1><p>Explore sales, understand retention and test the economics of your next customer intervention.</p><div class="chips"><span class="chip">OLIST DATASET</span><span class="chip">HISTORICAL ANALYSIS</span><span class="chip">BRL</span></div></div>', unsafe_allow_html=True)
try:
    orders, items = load_data()
except Exception as exc:
    st.error('Could not load the repository dataset. Keep data/archive (4).zip in its original location.')
    st.exception(exc)
    st.stop()

st.sidebar.markdown('<div class="brand"><span class="brand-mark">R</span>RetailIQ</div>', unsafe_allow_html=True)
page = st.sidebar.radio('Explore', ['Sales overview','Customers & retention','Sellers & delivery','ROI calculator','Research findings'])
delivered = orders.loc[orders.order_status.eq('delivered')].copy()
minimum, maximum = delivered.order_purchase_timestamp.min().date(), delivered.order_purchase_timestamp.max().date()
st.sidebar.caption('Filters apply to the first three pages. Research and ROI assumptions are separate.')
dates = st.sidebar.date_input('Purchase dates', (minimum, maximum), min_value=minimum, max_value=maximum)
states = st.sidebar.multiselect('Customer states', sorted(delivered.customer_state.dropna().unique()))
if len(dates) != 2:
    st.info('Select both a start and an end date.'); st.stop()
start, end = dates
frame = delivered.loc[delivered.order_purchase_timestamp.ge(pd.Timestamp(start)) & delivered.order_purchase_timestamp.lt(pd.Timestamp(end)+pd.Timedelta(days=1))].copy()
if states:
    frame = frame.loc[frame.customer_state.isin(states)]
if frame.empty and page in ['Sales overview','Customers & retention','Sellers & delivery']:
    st.info('No delivered orders match these filters. Choose a wider range.'); st.stop()
st.sidebar.caption('Only delivered orders are included in the interactive analysis. Amounts are Brazilian reais (BRL).')

if page == 'Sales overview':
    st.subheader('Sales overview')
    total = frame.payment_value.sum()
    cols = st.columns(4)
    cols[0].metric('Collected payments', f'R$ {total / 1_000_000:,.2f}M' if total >= 1_000_000 else f'R$ {total:,.0f}')
    cols[1].metric('Delivered orders', f'{len(frame):,}')
    cols[2].metric('Unique customers', f'{frame.customer_unique_id.nunique():,}')
    cols[3].metric('Average payment / order', f'R$ {frame.payment_value.mean():,.2f}')
    st.caption('Payments include freight and are not profit. Missing payments are excluded from the average.')
    monthly = frame.groupby('month', as_index=False).agg(payments=('payment_value','sum'), orders=('order_id','nunique'))
    chart(px.line(monthly, x='month', y='payments', markers=True, title='Monthly collected payments', color_discrete_sequence=[COLOR]))
    geo = frame.groupby('customer_state', as_index=False).agg(payments=('payment_value','sum'), orders=('order_id','nunique')).sort_values('payments', ascending=False)
    chart(px.bar(geo, x='customer_state', y='payments', title='Collected payments by customer state', color_discrete_sequence=[COLOR]))
    st.download_button('Download state summary', geo.to_csv(index=False), 'retailiq_state_summary.csv', 'text/csv')

elif page == 'Customers & retention':
    st.subheader('Customers & retention')
    summary = customer_summary(frame)
    a,b,c = st.columns(3)
    a.metric('Repeat customers', f'{(summary.orders >= 2).mean():.2%}')
    b.metric('Orders per customer', f'{summary.orders.mean():.2f}')
    c.metric('Inactive 90+ days', f'{(summary.recency_days >= 90).mean():.2%}')
    st.caption('Recomputed within your selected period. Inactivity is measured at its latest observed purchase + 1 day; it is not a live churn prediction.')
    segments = summary.groupby('segment').size().rename('customers').reset_index()
    chart(px.bar(segments, x='segment', y='customers', color_discrete_sequence=[COLOR], title='Customer segments'))
    activity = frame[['customer_unique_id','order_purchase_timestamp']].copy()
    activity['period'] = activity.order_purchase_timestamp.dt.to_period('M')
    activity['cohort'] = activity.groupby('customer_unique_id').period.transform('min')
    activity['age'] = (activity.period.dt.year-activity.cohort.dt.year)*12 + activity.period.dt.month-activity.cohort.dt.month
    counts = activity.groupby(['cohort','age']).customer_unique_id.nunique().unstack()
    retention = counts.div(counts[0], axis=0)
    # Zero means observed but no returning customers; future months remain blank.
    latest = activity.period.max()
    for cohort in retention.index:
        horizon = (latest.year-cohort.year)*12+latest.month-cohort.month
        for age in retention.columns:
            if age <= horizon and pd.isna(retention.loc[cohort, age]): retention.loc[cohort, age] = 0
    retention.index = retention.index.astype(str)
    chart(px.imshow(retention, aspect='auto', color_continuous_scale='Teal', zmin=0, zmax=1,
                    labels=dict(x='Months after first purchase', y='First purchase month', color='Retention'), title='Monthly customer retention'))
    st.caption('Cohorts use the first purchase observed within your filters. Blank cells are not yet observable; month 0 is 100%.')
    st.download_button('Download retention table', retention.to_csv(), 'retailiq_retention.csv', 'text/csv')

elif page == 'Sellers & delivery':
    st.subheader('Sellers & delivery')
    matched = items.merge(frame[['order_id','review_score']], on='order_id', validate='many_to_one')
    sales = matched.groupby(['seller_id','seller_state'], as_index=False).agg(item_sales=('price','sum'), orders=('order_id','nunique'))
    # Reviews averaged once per seller/order, not once per item.
    scores = matched.drop_duplicates(['seller_id','order_id']).groupby('seller_id', as_index=False).review_score.mean()
    sales = sales.merge(scores, on='seller_id', validate='one_to_one').sort_values('item_sales', ascending=False)
    a,b,c = st.columns(3)
    a.metric('Active sellers', f'{len(sales):,}')
    a.caption('Sellers with orders in the selected window')
    b.metric('Average delivery', f'{frame.delivery_days.mean():.1f} days')
    valid = frame.dropna(subset=['delay_days'])
    c.metric('Late deliveries', f'{valid.delay_days.gt(0).mean():.1%}')
    chart(px.bar(sales.head(15), x='seller_id', y='item_sales', color='seller_state', title='Top 15 sellers by item sales'))
    st.caption('Item sales exclude freight. Order reviews reflect the whole order, not an individual seller.')
    valid = valid.assign(delivery=valid.delay_days.gt(0).map({True:'Late',False:'On time / early'}))
    reviews = valid.groupby('delivery', as_index=False).agg(average_review=('review_score','mean'), reviewed_orders=('review_score','count'))
    chart(px.bar(reviews, x='delivery', y='average_review', hover_data=['reviewed_orders'], range_y=[0,5], color_discrete_sequence=[COLOR], title='Delivery timing and review score'))
    st.dataframe(sales.head(100), hide_index=True, use_container_width=True)
    st.download_button('Download seller summary', sales.to_csv(index=False), 'retailiq_sellers.csv', 'text/csv')

elif page == 'ROI calculator':
    st.subheader('Proactive retention: break-even calculator')
    st.write('Explore a hypothetical intervention. The success rate is an assumption, not a measured voucher effect.')
    a,b = st.columns(2)
    customers = a.number_input('Customers targeted', min_value=1, value=18021, step=100)
    revenue = a.number_input('Revenue at risk per customer (BRL)', min_value=0.01, value=146.72)
    cost = a.number_input('Intervention cost per customer (BRL)', min_value=0.0, value=15.0)
    margin = b.slider('Contribution margin (%)', 1, 100, 30)/100
    success = b.slider('Assumed incremental retention (%)', 0, 100, 15)/100
    fixed = b.number_input('Fixed campaign cost (BRL)', min_value=0.0, value=0.0)
    spend = customers*cost + fixed
    recovered = customers*revenue*margin*success
    net = recovered-spend
    threshold = spend/(customers*revenue*margin)
    x,y,z = st.columns(3)
    x.metric('Campaign cost', f'R$ {spend:,.0f}')
    y.metric('Net incremental contribution', f'R$ {net:,.0f}')
    z.metric('Break-even retention lift', f'{threshold:.1%}')
    if threshold > 1: st.warning('These assumptions cannot break even, even at 100% incremental retention.')
    st.caption('Net contribution = customers × revenue at risk × margin × incremental retention − campaign cost. Costs apply to all targeted customers. Incremental retention means customers retained because of the intervention.')
    sensitivity = pd.DataFrame({'Retention lift (%)':range(101)})
    sensitivity['Net contribution (BRL)'] = customers*revenue*margin*sensitivity['Retention lift (%)']/100-spend
    fig = px.line(sensitivity, x='Retention lift (%)', y='Net contribution (BRL)', color_discrete_sequence=[COLOR])
    fig.add_hline(y=0, line_dash='dash'); chart(fig)
    st.caption('Initial customer count and approximate revenue at risk come from the repository research summary. The original ~10.2% break-even calculation used revenue, without a contribution-margin adjustment. Set margin to 100% to reproduce that framing.')

else:
    st.subheader('Research findings')
    st.info('Saved results from docs/model_results_summary.md. Models are not retrained or served by this dashboard; these figures do not change with sidebar filters.')
    a,b,c = st.columns(3)
    a.metric('Churn classifier ROC-AUC', '0.746')
    b.metric('Spend model R²', '0.0351')
    c.metric('Spend model MAE', 'R$ 110.65')
    st.write('The reported CLV target is historical customer spend, not future lifetime value. Its low R² limits predictive usefulness.')
    st.markdown('**Voucher analysis:** the research reports a +1.64 percentage-point unadjusted churn difference and a +17.48-point adjusted estimate. These observational estimates depend on causal assumptions; they do not establish that vouchers cause churn or that a new retention campaign will succeed.')
    st.markdown('**Fairness:** regional and price-tier gaps were reported. Their causes and statistical uncertainty require further evaluation; sample size alone does not establish why a gap exists.')
    for name, caption in [('shap_churn_summary.png','Saved churn feature attribution'),('shap_clv_summary.png','Saved historical-spend feature attribution'),('fairness_regional_gaps.png','Saved regional audit'),('fairness_price_tier_gaps.png','Saved price-tier audit')]:
        path = ROOT/'docs'/name
        if path.exists():
            with st.expander(caption): st.image(str(path), use_container_width=True)

st.markdown('<div class="footer"><span>RetailIQ · Built by Visveswaran V</span><span>Olist historical data · Portfolio research</span></div>', unsafe_allow_html=True)
