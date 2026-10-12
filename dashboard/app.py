from pathlib import Path
from zipfile import ZipFile
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image, ImageDraw


def make_tab_icon():
    """Browser-tab icon: purple tile with a white shopping bag and gold clasp (UI theme colours)."""
    try:
        s = 256
        img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, s - 1, s - 1), radius=60, fill='#6d3fe0')
        d.arc((92, 46, 164, 140), 180, 360, fill='#e4dbfa', width=14)
        d.rounded_rectangle((60, 96, 196, 212), radius=20, fill='#ffffff')
        d.rounded_rectangle((60, 96, 196, 118), radius=10, fill='#ece7fd')
        d.ellipse((116, 132, 140, 156), fill='#e0b862')
        return img
    except Exception:
        return '🛍️'


st.set_page_config(page_title='RetailIQ | Retail intelligence', page_icon=make_tab_icon(), layout='wide')
ROOT = Path(__file__).resolve().parents[1]
COLOR = '#6d4fd8'

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
    fig.update_layout(template='plotly_white', height=370, paper_bgcolor='white', plot_bgcolor='white', font=dict(family='Arial',color='#5b5675',size=12), title_font=dict(size=16,color='#1b1730'), margin=dict(l=25,r=25,t=60,b=30), colorway=['#6d4fd8','#a58de8','#2fb7a6','#f2b27a','#8c97d9'])
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(gridcolor='#efeaf9', zeroline=False, automargin=True)
    st.plotly_chart(fig, use_container_width=True)


# ---------- E-commerce illustrations (inline SVG, purple theme) ----------
def svg_icon(inner, color='#6d3fe0', size=22, sw=2):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg" fill="none" '
            f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>')

IC_SEARCH = svg_icon('<circle cx="11" cy="11" r="7"/><path d="M20 20 L16 16"/>', '#8a85a3', 18)
IC_BELL = svg_icon('<path d="M6 17 V11 a6 6 0 0 1 12 0 V17 l2 2 H4 Z"/><path d="M10 21 h4"/>', '#1b1730', 22)
IC_CART = svg_icon('<path d="M2 3 h3 l3 12 h10 l3 -8 H6.5"/><circle cx="9" cy="20" r="1.6"/><circle cx="17" cy="20" r="1.6"/>', '#1b1730', 22)
IC_ORDERS = svg_icon('<path d="M3 4 h2.5 l2.5 10 h9 l2.5 -7 H7"/><circle cx="9" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/>', '#1f9d8e', 20)
IC_CHURN = svg_icon('<path d="M3 7 L10 14 L14 10 L21 17"/><path d="M15 17 H21 V11"/>', '#e2793f', 20)
IC_CAUSAL = svg_icon('<circle cx="5" cy="12" r="2.5"/><circle cx="19" cy="6" r="2.5"/><circle cx="19" cy="18" r="2.5"/><path d="M7.3 11 L16.7 7 M7.3 13 L16.7 17"/>', '#c58a14', 20)
IC_FAIR = svg_icon('<path d="M12 3 V21 M7 21 H17"/><path d="M5 7 H19"/><path d="M5 7 L2.5 14 a2.8 2.8 0 0 0 5 0 Z"/><path d="M19 7 L16.5 14 a2.8 2.8 0 0 0 5 0 Z"/>', '#5d9a14', 20)

BRAND_SVG = (
    '<svg viewBox="0 0 40 40" width="38" height="38" xmlns="http://www.w3.org/2000/svg" fill="none">'
    '<rect x="1" y="1" width="38" height="38" rx="12" fill="#6d3fe0"/>'
    '<path d="M14 15 a6 6 0 0 1 12 0" stroke="#e4dbfa" stroke-width="2.6" stroke-linecap="round"/>'
    '<rect x="9" y="15" width="22" height="17" rx="5" fill="#fff"/>'
    '<rect x="9" y="15" width="22" height="5" rx="2.5" fill="#ece7fd"/>'
    '<circle cx="20" cy="24.5" r="2.3" fill="#e0b862"/>'
    '</svg>'
)

HERO_ART_SVG = (
    '<svg viewBox="0 0 440 280" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke-linecap="round" stroke-linejoin="round">'
    '<defs><linearGradient id="cardg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8a68e8"/><stop offset="1" stop-color="#bba8f1"/></linearGradient></defs>'
    '<ellipse cx="240" cy="160" rx="180" ry="105" fill="#dccffa" opacity=".55"/>'
    # delivered / retention card (right)
    '<rect x="326" y="16" width="102" height="154" rx="18" fill="#fff" stroke="#e6defa" stroke-width="2"/>'
    '<text x="377" y="40" text-anchor="middle" font-family="Arial" font-size="10" fill="#8a85a3">Order status</text>'
    '<circle cx="377" cy="80" r="27" fill="#f4effe" stroke="#6d3fe0" stroke-width="4"/>'
    '<path d="M365 80 l8 9 l16 -19" stroke="#6d3fe0" stroke-width="5"/>'
    '<text x="377" y="130" text-anchor="middle" font-family="Arial" font-size="15" font-weight="700" fill="#1b1730">Delivered</text>'
    '<rect x="345" y="140" width="64" height="16" rx="8" fill="#ece7fd"/>'
    '<text x="377" y="152" text-anchor="middle" font-family="Arial" font-size="9" font-weight="700" fill="#6d3fe0">▲ REPEAT BUYER</text>'
    # shopping bag
    '<path d="M168 98 C168 52 244 52 244 98" stroke="#8f7bd0" stroke-width="9"/>'
    '<path d="M128 98 H286 L302 234 Q303 246 291 246 H123 Q111 246 112 234 Z" fill="#b9a8ea"/>'
    '<path d="M128 98 H286 L288 116 H126 Z" fill="#cdbff3"/>'
    '<rect x="192" y="120" width="30" height="24" rx="6" fill="#e0b862" stroke="#c79a3d" stroke-width="2"/>'
    '<circle cx="207" cy="132" r="3.5" fill="#c79a3d"/>'
    # credit card
    '<g transform="translate(228 156) rotate(-13)">'
    '<rect x="0" y="0" width="190" height="116" rx="16" fill="url(#cardg)" stroke="#fff" stroke-width="2"/>'
    '<text x="18" y="30" font-family="Arial" font-size="15" font-weight="700" fill="#fff">RetailIQ</text>'
    '<rect x="18" y="44" width="34" height="26" rx="6" fill="#ece7fd"/>'
    '<path d="M18 57 H52 M35 44 V70" stroke="#bba8f1" stroke-width="1.6"/>'
    '<g stroke="#fff" stroke-width="2.4" opacity=".9"><path d="M150 40 q6 8 0 16"/><path d="M158 34 q10 14 0 28"/></g>'
    '<g fill="#fff" opacity=".85"><rect x="18" y="90" width="28" height="6" rx="3"/><rect x="52" y="90" width="28" height="6" rx="3"/><rect x="86" y="90" width="28" height="6" rx="3"/><rect x="120" y="90" width="28" height="6" rx="3"/></g>'
    '</g>'
    # cart tile (left)
    '<rect x="14" y="62" width="98" height="98" rx="24" fill="#fff" stroke="#e6defa" stroke-width="2"/>'
    '<path d="M36 90 h9 l8 28 h30 l8 -20 H50" stroke="#6d3fe0" stroke-width="5"/>'
    '<circle cx="59" cy="132" r="5.5" fill="#6d3fe0"/><circle cx="84" cy="132" r="5.5" fill="#6d3fe0"/>'
    # sparkles
    '<g fill="#8a68e8"><circle cx="300" cy="40" r="4"/><circle cx="418" cy="200" r="3.5"/><circle cx="60" cy="30" r="3"/></g>'
    '<g fill="#e0b862"><circle cx="314" cy="22" r="3"/><circle cx="26" cy="190" r="3.5"/></g>'
    '<g fill="#f2a98a"><rect x="404" y="226" width="7" height="7" rx="2" transform="rotate(25 407 229)"/><circle cx="150" cy="22" r="3"/></g>'
    '</svg>'
)

CTA_ART_SVG = (
    '<svg viewBox="0 0 220 120" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="6" y="8" width="208" height="104" rx="16" fill="#fff" stroke="#e6defa" stroke-width="2"/>'
    '<text x="22" y="30" font-family="Arial" font-size="10" fill="#8a85a3">Break-even retention lift</text>'
    '<g fill="#cfc2f5"><rect x="26" y="70" width="18" height="30" rx="4"/><rect x="52" y="58" width="18" height="42" rx="4"/><rect x="78" y="64" width="18" height="36" rx="4"/></g>'
    '<g fill="#6d3fe0"><rect x="104" y="44" width="18" height="56" rx="4"/><rect x="130" y="52" width="18" height="48" rx="4"/></g>'
    '<path d="M24 62 L62 48 L96 56 L130 34 L178 26" stroke="#2fb7a6" stroke-width="3"/>'
    '<circle cx="178" cy="26" r="5" fill="#2fb7a6"/>'
    '<rect x="158" y="62" width="44" height="22" rx="11" fill="#ece7fd"/>'
    '<text x="180" y="77" text-anchor="middle" font-family="Arial" font-size="10" font-weight="700" fill="#6d3fe0">ROI</text>'
    '</svg>'
)


def feature(icon_svg, bg, title, sub):
    return (f'<div class="feat"><span class="feat-ic" style="background:{bg}">{icon_svg}</span>'
            f'<span class="feat-tx"><b>{title}</b><small>{sub}</small></span></div>')


def nav_uri(inner, color):
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='{color}' "
           f"stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>{inner}</svg>")
    return 'url("data:image/svg+xml;utf8,' + svg.replace('#', '%23') + '")'

NAV_ICONS = [
    "<path d='M4 20V10M10 20V4M16 20v-8M22 20H2'/>",
    "<circle cx='9' cy='8' r='3.5'/><path d='M2.5 20c0-4 3-6 6.5-6s6.5 2 6.5 6'/><path d='M17 5a3 3 0 0 1 0 6M19 14c2 .6 3 2.5 3 5'/>",
    "<path d='M2 6h12v10H2zM14 10h4l3 3v3h-7'/><circle cx='6' cy='18.5' r='1.8'/><circle cx='17' cy='18.5' r='1.8'/>",
    "<rect x='5' y='3' width='14' height='18' rx='2'/><path d='M8 7h8M8 12h2M12 12h2M8 16h2M12 16h2'/>",
    "<path d='M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2.2h12.4a1.5 1.5 0 0 0 1.3-2.2L14 9V3'/>",
]
NAV_CSS = ''.join(
    f'[data-testid="stSidebar"] [role="radiogroup"]>label:nth-of-type({i})::before{{background-image:{nav_uri(ic,"#8a85a3")}}}'
    f'[data-testid="stSidebar"] [role="radiogroup"]>label:nth-of-type({i}):has(input:checked)::before{{background-image:{nav_uri(ic,"#6d3fe0")}}}'
    for i, ic in enumerate(NAV_ICONS, start=1)
)

BASE_CSS = '''
<style>
:root{--purple:#6d3fe0;--purple-dark:#5a2fc4;--lav:#ece7fd;--lav2:#e4dcfa;--ink:#1b1730;--muted:#5b5675;--line:#ece7f7}
.stApp{background:linear-gradient(135deg,#e3dbfa 0%,#f2effd 42%,#ddd3f7 100%);background-attachment:fixed;color:var(--ink)}
[data-testid="stHeader"]{background:transparent}
.block-container,[data-testid="stMainBlockContainer"]{padding-top:3.6rem;padding-bottom:2rem;max-width:1440px}
h1,h2,h3{letter-spacing:-.035em;color:var(--ink)}
h3{font-size:1.4rem!important;font-weight:650!important;margin-top:.4rem}
[data-testid="stSidebar"]{background:#fff;border-right:0;border-radius:0 30px 30px 0;box-shadow:6px 0 32px #6d3fe014}
[data-testid="stSidebar"] .block-container{padding-top:2rem}
[data-testid="stSidebarUserContent"]{padding-top:1.4rem}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{font-size:10px;letter-spacing:1.6px;text-transform:uppercase;color:#8a85a3;font-weight:700}
[data-testid="stSidebar"] [role="radiogroup"]{gap:4px}
[data-testid="stSidebar"] [role="radiogroup"]>label{display:flex;align-items:center;padding:11px 14px;border-radius:30px;margin:0;width:100%;box-sizing:border-box}
[data-testid="stSidebar"] [role="radiogroup"]>label>div:first-of-type{display:none}
[data-testid="stSidebar"] [role="radiogroup"]>label::before{content:"";width:20px;height:20px;flex:none;margin-right:11px;background-size:contain;background-repeat:no-repeat;background-position:center}
[data-testid="stSidebar"] [role="radiogroup"]>label p{font-size:14px;color:#4a4566}
[data-testid="stSidebar"] [role="radiogroup"]>label:hover{background:#f5f2fe}
[data-testid="stSidebar"] [role="radiogroup"]>label:has(input:checked){background:var(--lav)}
[data-testid="stSidebar"] [role="radiogroup"]>label:has(input:checked) p{color:var(--purple);font-weight:650}
[data-testid="stCaptionContainer"]{color:#6a6585}
[data-testid="stCaptionContainer"] p{font-size:13px;line-height:1.5}

/* Colourful metric tiles, like the "top offers" cards */
[data-testid="stMetric"]{background:#fff;border:0;border-radius:22px;padding:20px 22px;box-shadow:0 8px 24px #6d3fe010;min-height:118px;box-sizing:border-box;width:100%}
[data-testid="stMetricLabel"],[data-testid="stMetricLabel"] p{color:#5b5675;font-size:.82rem}
[data-testid="stMetricValue"]{font-size:clamp(1.4rem,2vw,2rem);font-weight:700;letter-spacing:-.04em;color:var(--ink)}
[data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"],[data-testid="column"]:nth-child(1) [data-testid="stMetric"]{background:#1f1a33}
[data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] *,[data-testid="column"]:nth-child(1) [data-testid="stMetric"] *{color:#fff!important}
[data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"],[data-testid="column"]:nth-child(2) [data-testid="stMetric"]{background:#fbe4d9}
[data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"],[data-testid="column"]:nth-child(3) [data-testid="stMetric"]{background:#d6ede9}
[data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"],[data-testid="column"]:nth-child(4) [data-testid="stMetric"]{background:#f6ecdd}
[data-testid="stColumn"],[data-testid="column"]{min-width:0}

[data-testid="stPlotlyChart"],[data-testid="stDataFrame"]{background:#fff;border:1px solid var(--line);border-radius:22px;overflow:hidden;box-shadow:0 8px 24px #6d3fe00d;padding:6px}
[data-testid="stVerticalBlockBorderWrapper"]>div{border-radius:20px}
[data-baseweb="tab-list"]{gap:8px;background:var(--lav);border-radius:30px;padding:5px;margin-bottom:22px}
button[data-baseweb="tab"]{padding:10px 20px;border-radius:26px;height:44px}
button[data-baseweb="tab"][aria-selected="true"]{background:white;color:var(--purple);box-shadow:0 2px 6px #6d3fe018}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:var(--purple);border:0;border-radius:30px;min-height:46px;font-weight:650}
.stButton>button,.stDownloadButton>button{border-radius:30px;border:1px solid #d9cff7;color:var(--purple);background:#fff;font-weight:600;padding:.5rem 1.3rem}
.stDownloadButton>button:hover,.stButton>button:hover{border-color:var(--purple);color:var(--purple-dark);background:#f7f4ff}
[data-testid="stFileUploaderDropzone"]{border:1px dashed #bcaaf0;border-radius:18px;background:#f4f0fe;padding:28px}
[data-testid="stAlert"]{border-radius:16px}
[data-baseweb="tag"]{background:var(--purple)!important;border-radius:20px!important}
[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="base-input"]{border-radius:14px!important}
[role="slider"]{background:var(--purple)!important}

/* Brand, top bar */
.brand{display:flex;align-items:center;gap:10px;font-weight:750;font-size:22px;letter-spacing:-.7px;margin-bottom:22px;color:var(--ink)}
.brand svg{flex:none}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;margin:0 0 14px}
.searchpill{flex:1;max-width:520px;display:flex;align-items:center;gap:10px;background:#ffffffb8;border-radius:30px;padding:12px 18px;font-size:13px;color:#8a85a3;box-shadow:0 4px 18px #6d3fe00d;pointer-events:none}
.top-icons{display:flex;align-items:center;gap:18px;margin-right:150px}
.cartwrap{position:relative;display:inline-flex}
.cartwrap i{position:absolute;top:-6px;right:-8px;width:9px;height:9px;border-radius:50%;background:var(--purple);border:2px solid #f3effd}
.avatar{width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#8a68e8,#bba8f1);color:#fff;font-weight:700;display:inline-flex;align-items:center;justify-content:center;font-size:15px;border:2px solid #fff}

/* Hero card */
.hero{display:flex;align-items:center;justify-content:space-between;gap:24px;background:linear-gradient(110deg,#f6f2ff 0%,#e9e0fc 58%,#ddd0f9 100%);border-radius:28px;padding:34px 40px;margin:6px 0 16px;position:relative;overflow:hidden;box-shadow:0 12px 36px #6d3fe014;border:1px solid #fff}
.hero-copy{flex:1;min-width:0}
.eyebrow{color:var(--purple);font-size:11px;letter-spacing:2px;font-weight:700;text-transform:uppercase}
.hero h1{color:var(--ink)!important;font-size:clamp(2rem,3.4vw,2.9rem)!important;font-weight:720!important;line-height:1.12!important;margin:10px 0 12px;padding:0;max-width:640px}
.hero h1 span{color:var(--purple)}
.hero p{color:var(--muted);max-width:520px;line-height:1.6;margin:0;font-size:14px}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:22px}
.chip{font-size:11px;letter-spacing:.5px;padding:7px 14px;background:#fff;border:1px solid #d9cff7;border-radius:30px;color:var(--purple);font-weight:650}
.chip:first-child{background:var(--purple);border-color:var(--purple);color:#fff}
.hero-art{flex:none;width:420px;height:262px}

/* Feature strip */
.featstrip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;background:#ffffffc4;border-radius:26px;padding:16px 20px;margin:0 0 22px;box-shadow:0 6px 22px #6d3fe00d}
.feat{display:flex;align-items:center;gap:12px;min-width:0}
.feat-ic{width:40px;height:40px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;flex:none}
.feat-tx{display:flex;flex-direction:column;min-width:0}
.feat-tx b{font-size:13px;color:var(--ink);font-weight:650}
.feat-tx small{font-size:11px;color:#7b7696}

/* Misc blocks */
.empty{border:1px dashed #cfc2f5;background:#f9f7ff;border-radius:18px;padding:48px 26px;text-align:center;color:#6a6585;min-height:235px}
.empty strong{display:block;color:#2b2447;font-size:19px;margin:14px 0 9px}
.section-label{font-size:11px;font-weight:750;letter-spacing:1.5px;color:var(--purple);text-transform:uppercase;margin:4px 0 10px}
.cta{display:flex;align-items:center;justify-content:space-between;gap:24px;background:linear-gradient(110deg,#f1ebfe,#dfd3fa);border-radius:26px;padding:26px 34px;margin:30px 0 0;border:1px solid #fff;box-shadow:0 10px 30px #6d3fe010}
.cta-copy{flex:1;min-width:0}
.cta-copy b{display:block;font-size:24px;letter-spacing:-.03em;color:var(--ink);font-weight:700}
.cta-copy span{display:block;font-size:13px;color:var(--muted);margin:6px 0 14px;max-width:460px;line-height:1.55}
.cta-pill{display:inline-block;background:#fff;color:var(--purple);border:1px solid #d9cff7;border-radius:30px;padding:7px 16px;font-size:12px;font-weight:650}
.cta-art{flex:none;width:230px;height:125px}
.footer{border-top:1px solid #d9d0f2;padding-top:18px;margin-top:30px;font-size:11px;color:#6a6585;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}

@media(max-width:1100px){.featstrip{grid-template-columns:repeat(2,minmax(0,1fr))}.hero-art{width:320px;height:200px}.top-icons{margin-right:0}}
@media(max-width:768px){.block-container,[data-testid="stMainBlockContainer"]{padding:1.5rem 1rem}.hero{padding:24px 22px;flex-direction:column;align-items:flex-start}.hero-art,.cta-art{display:none}.featstrip{grid-template-columns:1fr}.searchpill{display:none}.cta{padding:22px}[data-testid="stMetric"]{padding:15px;min-height:100px}[data-testid="stMetricValue"]{font-size:1.6rem}button[data-baseweb="tab"]{padding:8px 12px;font-size:12px}}
'''
st.markdown(BASE_CSS + NAV_CSS + '</style>', unsafe_allow_html=True)

st.markdown(
    '<div class="topbar"><div class="searchpill">' + IC_SEARCH + 'Search products, sellers or states</div>'
    '<div class="top-icons">' + IC_BELL + '<span class="cartwrap">' + IC_CART + '<i></i></span><span class="avatar">V</span></div></div>'
    '<div class="hero"><div class="hero-copy"><div class="eyebrow">Commerce intelligence</div>'
    '<h1>Every order. A <span>clearer picture.</span></h1>'
    '<p>Explore sales, understand retention and test the economics of your next customer intervention.</p>'
    '<div class="chips"><span class="chip">OLIST DATASET</span><span class="chip">HISTORICAL ANALYSIS</span><span class="chip">BRL</span></div></div>'
    '<div class="hero-art">' + HERO_ART_SVG + '</div></div>'
    '<div class="featstrip">'
    + feature(IC_ORDERS, '#d9f1ee', 'Orders &amp; carts', 'Delivered orders, in BRL')
    + feature(IC_CHURN, '#fde5d8', 'Churn watch', 'Inactive 90+ days')
    + feature(IC_CAUSAL, '#fbefc9', 'Causal impact', 'Vouchers vs. churn')
    + feature(IC_FAIR, '#e6f4c9', 'Fair predictions', 'Regional &amp; price audits')
    + '</div>', unsafe_allow_html=True)
try:
    orders, items = load_data()
except Exception as exc:
    st.error('Could not load the repository dataset. Keep data/archive (4).zip in its original location.')
    st.exception(exc)
    st.stop()

st.sidebar.markdown('<div class="brand">' + BRAND_SVG + 'RetailIQ</div>', unsafe_allow_html=True)
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
    chart(px.imshow(retention, aspect='auto', color_continuous_scale='Purples', zmin=0, zmax=1,
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

st.markdown('<div class="cta"><div class="cta-copy"><b>Test it before you spend it.</b><span>Model a retention campaign and see its break-even lift before committing budget. Open the ROI calculator from the sidebar.</span><span class="cta-pill">Retention · ROI · Fairness</span></div><div class="cta-art">' + CTA_ART_SVG + '</div></div>', unsafe_allow_html=True)
st.markdown('<div class="footer"><span>RetailIQ · Built by Visveswaran V</span><span>Olist historical data · Portfolio research</span></div>', unsafe_allow_html=True)
