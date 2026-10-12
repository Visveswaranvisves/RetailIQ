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
    fig.update_layout(template='plotly_white', margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig, use_container_width=True)

st.title('RetailIQ')
st.caption('Retail performance, customer retention and intervention economics • Olist historical data')
try:
    orders, items = load_data()
except Exception as exc:
    st.error('Could not load the repository dataset. Keep data/archive (4).zip in its original location.')
    st.exception(exc)
    st.stop()

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
    cols[0].metric('Collected payments', f'R$ {total:,.0f}')
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

st.divider()
st.caption('RetailIQ • Visveswaran V • Portfolio demonstration | Data: Olist Brazilian E-Commerce Public Dataset')
