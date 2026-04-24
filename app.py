# ============================================================
# SHARECHAT ANALYTICS INTELLIGENCE PLATFORM
# Product Analyst Internship Project | April 2026
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import base64
import warnings
warnings.filterwarnings("ignore")

# ─── PAGE CONFIG ────────────────────────────────────────────
_logo_img = Image.open("assets/logo.png")
st.set_page_config(
    page_title="ShareChat Analytics Platform",
    page_icon=_logo_img,
    layout="wide",
    initial_sidebar_state="expanded",   # filters always visible on load
)

# ─── COLOUR TOKENS ──────────────────────────────────────────
ORANGE  = "#FF6B2C"
TEAL    = "#00BCD4"
GREEN   = "#10B981"
PURPLE  = "#8B5CF6"
GOLD    = "#FFB800"
RED     = "#EF4444"
DARK    = "#111827"
BORDER  = "#E5E7EB"
SUBTEXT = "#9CA3AF"

# Chart palette — vibrant (original scheme)
COLOR_SEQ = [ORANGE, TEAL, GREEN, PURPLE, GOLD, "#3B82F6", RED, "#EC4899", "#F59E0B", "#14B8A6"]
PLT_MAP   = {"ShareChat": ORANGE, "Moj": PURPLE, "QuickTV": GREEN}   # platform colours

# ─── GLOBAL CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{ font-family:'Inter',sans-serif; }
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
/* kill every element that adds top whitespace */
header, [data-testid="stHeader"], [data-testid="stToolbar"] {
    height: 0 !important; min-height: 0 !important;
    padding: 0 !important; margin: 0 !important; overflow: hidden !important;
}
.main .block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stMain"] > div:first-child {
    padding-top: 0 !important; margin-top: 0 !important;
}
/* also target the app view wrapper */
[data-testid="stAppViewContainer"] > section.main { padding-top: 0 !important; }
/* sidebar expand/collapse button — always visible */
[data-testid="collapsedControl"] {
    display: flex !important; visibility: visible !important;
    background: #FF6B2C !important; border-radius: 0 6px 6px 0;
}
[data-testid="collapsedControl"] svg { fill: white !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{ background:#fff !important; border-right:1px solid #E5E7EB; }
section[data-testid="stSidebar"]>div{ background:#fff !important; }
[data-testid="stSidebar"] *{ color:#111827 !important; }

/* filter chip tags */
[data-testid="stSidebar"] [data-baseweb="tag"]{
    background:#FF6B2C !important; border-color:#FF6B2C !important; border-radius:3px !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span{ color:#fff !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] button{ color:rgba(255,255,255,.75) !important; }

/* widget labels */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{
    font-size:10px !important; font-weight:700 !important;
    letter-spacing:1.5px !important; text-transform:uppercase !important; color:#6B7280 !important;
}

/* ── MAIN CONTAINER ── */
.main .block-container{ padding:0 !important; max-width:100% !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{
    background:#fff !important; border-bottom:1px solid #E5E7EB; gap:0 !important; padding:0 !important;
}
.stTabs [data-baseweb="tab"]{
    background:none !important; border:none !important;
    border-bottom:2px solid transparent !important; border-radius:0 !important;
    padding:14px 22px !important; font-size:10px !important; font-weight:700 !important;
    letter-spacing:1.5px !important; text-transform:uppercase !important;
    color:#9CA3AF !important; margin:0 !important;
}
.stTabs [aria-selected="true"]{
    border-bottom:2px solid #FF6B2C !important; color:#FF6B2C !important;
}
.stTabs [data-baseweb="tab-panel"]{ padding:28px 32px !important; }

/* ── KPI CARDS ── */
.kpi-card{ background:#fff; border:1px solid #E5E7EB; padding:22px 24px; }
.kpi-lbl{ font-size:10px; font-weight:700; color:#9CA3AF; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:12px; }
.kpi-val{ font-size:30px; font-weight:800; color:#111827; line-height:1; }
.kpi-pos{ font-size:11px; color:#10B981; margin-top:8px; font-weight:600; }
.kpi-neg{ font-size:11px; color:#EF4444; margin-top:8px; font-weight:600; }
.kpi-dsc{ font-size:10px; color:#D1D5DB; margin-top:4px; }

/* ── SECTION HEADERS ── */
.sec-hdr{
    font-size:10px; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; color:#374151;
    border-bottom:1px solid #E5E7EB;
    padding-bottom:8px; margin:28px 0 14px 0;
}

/* ── INSIGHT BOX ── */
.ins-box{ background:#FFF8F5; border-left:3px solid #FF6B2C; padding:14px 18px; margin:16px 0; }
.ins-ttl{ font-size:10px; font-weight:700; color:#FF6B2C; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px; }
.ins-txt{ font-size:13px; color:#374151; line-height:1.65; }

/* ── DASHBOARD HEADER ── */
.dash-hdr{
    display:flex; align-items:center; gap:14px;
    padding:18px 32px 14px 32px;
    border-bottom:1px solid #E5E7EB; background:#fff;
}
.dash-ttl{ font-size:14px; font-weight:800; letter-spacing:3px; color:#6B7280; text-transform:uppercase; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ────────────────────────────────────────────────

def rgba(hex_c: str, a: float) -> str:
    h = hex_c.lstrip("#")
    r,g,b = int(h[:2],16), int(h[2:4],16), int(h[4:],16)
    return f"rgba({r},{g},{b},{a})"


@st.cache_data
def _logo_b64() -> str:
    with open("assets/logo.png","rb") as f:
        return base64.b64encode(f.read()).decode()


def kpi(label, value, delta="", pos=True, desc=""):
    dh = ""
    if delta:
        c   = GREEN if pos else RED
        arr = "↑" if pos else "↓"
        dh  = f'<div style="font-size:11px;color:{c};margin-top:8px;font-weight:600;">{arr} {delta}</div>'
    dsc = f'<div class="kpi-dsc">{desc}</div>' if desc else ""
    return f'<div class="kpi-card"><div class="kpi-lbl">{label}</div><div class="kpi-val">{value}</div>{dh}{dsc}</div>'


def sec(title):
    st.markdown(f'<div class="sec-hdr">{title}</div>', unsafe_allow_html=True)


def ins(text, title="Key Insight"):
    st.markdown(f'<div class="ins-box"><div class="ins-ttl">{title}</div><div class="ins-txt">{text}</div></div>',
                unsafe_allow_html=True)


def base_layout(fig, height=360, dual=False):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#374151", size=11),
        height=height,
        margin=dict(l=4, r=4, t=12, b=4),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
                    font=dict(size=11, color="#6B7280"), orientation="h",
                    yanchor="bottom", y=1.01, xanchor="left", x=0),
        xaxis=dict(showgrid=False, linecolor=BORDER,
                   tickfont=dict(size=10, color=SUBTEXT), tickcolor=BORDER),
        yaxis=dict(gridcolor="#F3F4F6", linecolor="rgba(0,0,0,0)",
                   tickfont=dict(size=10, color=SUBTEXT)),
    )
    if dual:
        fig.update_layout(
            yaxis2=dict(gridcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)",
                        tickfont=dict(size=10, color=SUBTEXT), showgrid=False)
        )
    return fig


# ─── DATA GENERATION ────────────────────────────────────────

@st.cache_data
def gen_monthly():
    np.random.seed(42)
    months = pd.date_range("2025-04-01", periods=13, freq="MS")
    sc0, mj0, qt0 = 95e6, 72e6, 38e6
    sc_r0, mj_r0, qt_r0 = 45.2, 28.5, 6.3
    rows = []
    for i, m in enumerate(months):
        n = np.random.uniform(.98,1.02)
        sc_mau=sc0*(1.022**i)*n; mj_mau=mj0*(1.025**i)*n; qt_mau=qt0*(1.06**i)*n
        sc_rev=sc_r0*(1.024**i)*np.random.uniform(.97,1.04)
        mj_rev=mj_r0*(1.027**i)*np.random.uniform(.97,1.04)
        qt_rev=qt_r0*(1.07**i)*np.random.uniform(.97,1.04)
        rows.append({
            "month":m, "month_label":m.strftime("%b %Y"),
            "sc_mau":int(sc_mau),"moj_mau":int(mj_mau),"qtv_mau":int(qt_mau),
            "total_mau":int(sc_mau+mj_mau+qt_mau),
            "sc_rev":round(sc_rev,1),"moj_rev":round(mj_rev,1),"qtv_rev":round(qt_rev,1),
            "total_rev":round(sc_rev+mj_rev+qt_rev,1),
            "dau_ratio":round(np.random.uniform(.43,.52),3),
            "new_users_m":round(np.random.uniform(9,15),1),
            "avg_session_min":round(np.random.uniform(16,22),1),
        })
    return pd.DataFrame(rows)


@st.cache_data
def gen_users():
    np.random.seed(42); N=10_000
    LANGS=["Hindi","Telugu","Tamil","Bengali","Marathi","Gujarati","Kannada",
           "Malayalam","Punjabi","Odia","Bhojpuri","Assamese","Rajasthani","Haryanvi","Urdu"]
    LP=[.38,.12,.10,.09,.07,.05,.04,.04,.03,.02,.02,.01,.01,.01,.01]
    RMAP={"Hindi":"North","Telugu":"South","Tamil":"South","Bengali":"East",
          "Marathi":"West","Gujarati":"West","Kannada":"South","Malayalam":"South",
          "Punjabi":"North","Odia":"East","Bhojpuri":"North","Assamese":"East",
          "Rajasthani":"North","Haryanvi":"North","Urdu":"North"}
    langs=np.random.choice(LANGS,N,p=LP)
    plats=np.random.choice(["ShareChat","Moj","QuickTV"],N,p=[.45,.38,.17])
    ages=np.random.choice(["18-24","25-34","35-44","45-54","55+"],N,p=[.32,.28,.22,.12,.06])
    signup=pd.to_datetime("2024-04-01")+pd.to_timedelta(np.random.randint(0,365,N),unit="D")
    return pd.DataFrame({
        "user_id":range(1,N+1),"platform":plats,"language":langs,
        "region":[RMAP[l] for l in langs],"age_group":ages,
        "gender":np.random.choice(["Male","Female","Other"],N,p=[.58,.39,.03]),
        "device":np.random.choice(["Android Budget","Android Mid","Android Premium","iOS"],N,p=[.45,.30,.15,.10]),
        "signup_date":signup,
        "is_premium":np.random.choice([True,False],N,p=[.08,.92]),
        "monthly_sessions":np.random.randint(5,120,N),
        "avg_session_min":np.random.uniform(8,35,N).round(1),
        "videos_per_session":np.random.randint(5,50,N),
        "ltv_inr":np.random.lognormal(7,1.2,N).round(0),
    })


@st.cache_data
def gen_content():
    np.random.seed(42); N=5_000
    CT=["Short Video","Image Post","Text Post","Reel","Drama Episode","Live Stream"]
    CTP=[.38,.24,.15,.12,.06,.05]
    CATS=["Entertainment","Comedy","News & Affairs","Devotional","Music","Fashion","Food","Sports","Education","Lifestyle"]
    CATP=[.28,.20,.13,.10,.09,.07,.05,.04,.02,.02]
    LANGS=["Hindi","Telugu","Tamil","Bengali","Marathi","Gujarati","Kannada","Malayalam","Punjabi","Others"]
    LGP=[.38,.12,.10,.09,.07,.05,.04,.04,.03,.08]
    ct=np.random.choice(CT,N,p=CTP); cat=np.random.choice(CATS,N,p=CATP); lg=np.random.choice(LANGS,N,p=LGP)
    BV={"Short Video":50000,"Reel":45000,"Drama Episode":35000,"Live Stream":20000,"Image Post":15000,"Text Post":8000}
    BE={"Short Video":.08,"Reel":.10,"Drama Episode":.12,"Live Stream":.07,"Image Post":.05,"Text Post":.04}
    views=[int(BV[c]*np.random.lognormal(0,1.5)) for c in ct]
    er=[BE[c]*np.random.uniform(.5,2.0) for c in ct]
    df=pd.DataFrame({
        "content_id":range(1,N+1),"content_type":ct,"category":cat,"language":lg,
        "platform":np.random.choice(["ShareChat","Moj","QuickTV"],N,p=[.45,.38,.17]),
        "upload_date":pd.to_datetime("2025-04-01")+pd.to_timedelta(np.random.randint(0,365,N),"D"),
        "views":views,
        "likes":[int(v*e*np.random.uniform(.30,.50)) for v,e in zip(views,er)],
        "shares":[int(v*e*np.random.uniform(.10,.20)) for v,e in zip(views,er)],
        "comments":[int(v*e*np.random.uniform(.05,.15)) for v,e in zip(views,er)],
        "engagement_rate":[round(e,4) for e in er],
        "watch_time_avg_sec":np.where(pd.Series(ct).isin(["Short Video","Reel"]),
            np.random.uniform(15,60,N),
            np.where(pd.Series(ct)=="Drama Episode",np.random.uniform(600,1800,N),
                     np.random.uniform(10,30,N))).round(0),
    })
    df["total_engagement"]=df["likes"]+df["shares"]+df["comments"]
    return df


@st.cache_data
def gen_retention():
    np.random.seed(42)
    cohorts=pd.date_range("2025-04-01",periods=12,freq="MS")
    base=[1.0,.48,.35,.28,.23,.20,.18,.16,.15,.14,.13,.12]
    data={}
    for i,c in enumerate(cohorts):
        avail=12-i; row={}
        for m in range(12):
            if m<avail:
                noise=np.random.uniform(.93,1.07)
                row[f"M{m:02d}"]=round(min(base[m]*noise,base[max(m-1,0)]),3) if m>0 else 1.0
            else:
                row[f"M{m:02d}"]=np.nan
        data[c.strftime("%b %Y")]=row
    return pd.DataFrame(data).T


@st.cache_data
def gen_dau():
    np.random.seed(42)
    dates=pd.date_range("2026-01-14",periods=90,freq="D")
    df=pd.DataFrame({"date":dates})
    df["dow"]=df["date"].dt.dayofweek
    for i,row in df.iterrows():
        wb=1.13 if row["dow"]>=5 else 1.0; tr=1+(i/90)*0.08; n=np.random.uniform(.97,1.03)
        df.at[i,"sc_dau"]=int(42e6*wb*tr*n); df.at[i,"moj_dau"]=int(34e6*wb*tr*n); df.at[i,"qtv_dau"]=int(27e6*wb*tr*n*1.1)
    df["total_dau"]=df["sc_dau"]+df["moj_dau"]+df["qtv_dau"]
    return df


@st.cache_data
def gen_revenue_daily():
    np.random.seed(42)
    dates=pd.date_range("2026-01-14",periods=90,freq="D")
    fmts=["In-Feed Video","Banner","Interstitial","Rewarded Video","Native Story"]
    shares=[.45,.18,.20,.12,.05]
    rows=[]
    for d in dates:
        base=2.8*(1.15 if d.dayofweek>=5 else 1.0)*np.random.uniform(.92,1.10)
        for f,sh in zip(fmts,shares):
            rows.append({"date":d,"ad_format":f,"revenue_cr":round(base*sh,3),
                         "impressions_m":round(base*sh*np.random.uniform(8,12),2),
                         "ecpm":round(np.random.uniform(55,115),1)})
    return pd.DataFrame(rows)


@st.cache_data
def gen_language():
    np.random.seed(42)
    LANGS=["Hindi","Telugu","Tamil","Bengali","Marathi","Gujarati","Kannada",
           "Malayalam","Punjabi","Odia","Bhojpuri","Assamese","Rajasthani","Haryanvi","Urdu"]
    SHARES=[.38,.12,.10,.09,.07,.05,.04,.04,.03,.02,.02,.01,.01,.01,.01]
    return pd.DataFrame({
        "language":LANGS,
        "mau_m":[s*200 for s in SHARES],
        "engagement_rate":np.random.uniform(.06,.15,15).round(4),
        "creator_k":np.random.uniform(5,150,15).round(1),
        "revenue_cr":np.random.uniform(2,90,15).round(1),
        "avg_session_min":np.random.uniform(14,25,15).round(1),
        "content_per_user":np.random.uniform(25,65,15).round(0),
    })


# ─── PAGE: OVERVIEW ─────────────────────────────────────────

def page_overview(monthly, revenue_det):
    latest=monthly.iloc[-1]; first=monthly.iloc[0]
    yoy=(latest["total_rev"]/first["total_rev"]-1)*100; arr=latest["total_rev"]*12

    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.markdown(kpi("Monthly Monetizable Users",f"{latest['total_mau']/1e6:.0f}M","28% YoY",True,"Network total"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Annualised Revenue",f"₹{arr:.0f} Cr",f"+{yoy:.1f}% YoY",True,"Combined ARR"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("DAU / MAU Ratio",f"{latest['dau_ratio']*100:.1f}%","+3.2 pp YoY",True,"Daily stickiness"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Avg Session",f"{latest['avg_session_min']:.1f} min","+1.8 min YoY",True,"Per active user/day"), unsafe_allow_html=True)
    with c5: st.markdown(kpi("New Users (Month)",f"{latest['new_users_m']:.1f}M","+12% MoM",True,"Across all platforms"), unsafe_allow_html=True)

    # ── Dual-axis: Revenue bars + DAU/MAU line
    sec("Monthly Revenue Trend")
    fig=make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(x=monthly["month_label"],y=monthly["total_rev"],
                         name="Revenue (₹ Cr)",marker_color=ORANGE,marker_line_width=0),secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly["month_label"],y=monthly["dau_ratio"]*100,
                             name="DAU/MAU %",mode="lines",
                             line=dict(color=SUBTEXT,width=2,dash="dot"),marker=dict(size=4)),secondary_y=True)
    fig=base_layout(fig,320,dual=True)
    fig.update_layout(hovermode="x unified",barmode="group",legend=dict(orientation="h",y=1.05,x=0))
    fig.update_yaxes(title_text="Revenue (₹ Cr)", secondary_y=False,
                     title=dict(font=dict(size=10, color=SUBTEXT)))
    fig.update_yaxes(title_text="DAU/MAU %", secondary_y=True,
                     title=dict(font=dict(size=10, color=SUBTEXT)))
    st.plotly_chart(fig,use_container_width=True)

    col1,col2=st.columns([3,2])
    with col1:
        sec("Monthly Active Users by Platform (Millions)")
        mau_long=monthly.melt(id_vars=["month_label"],value_vars=["sc_mau","moj_mau","qtv_mau"],
                              var_name="platform",value_name="mau")
        mau_long["platform"]=mau_long["platform"].map({"sc_mau":"ShareChat","moj_mau":"Moj","qtv_mau":"QuickTV"})
        mau_long["mau_m"]=mau_long["mau"]/1e6
        fig2=px.bar(mau_long,x="month_label",y="mau_m",color="platform",
                    color_discrete_map=PLT_MAP,
                    barmode="group",labels={"mau_m":"MAU (M)","month_label":"","platform":"Platform"})
        fig2.update_traces(marker_line_width=0)
        fig2=base_layout(fig2,300)
        st.plotly_chart(fig2,use_container_width=True)

    with col2:
        sec("Revenue by Platform")
        pie=pd.DataFrame({
            "Platform":["ShareChat","Moj","QuickTV"],
            "Rev":[latest["sc_rev"],latest["moj_rev"],latest["qtv_rev"]],
        })
        fig3=px.pie(pie,values="Rev",names="Platform",hole=.62,
                    color_discrete_map=PLT_MAP)
        fig3.update_traces(textposition="outside",textfont_size=11,
                           hovertemplate="<b>%{label}</b><br>₹%{value:.1f} Cr<br>%{percent}")
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
            height=300,margin=dict(l=0,r=0,t=30,b=10),
            legend=dict(font=dict(size=11),orientation="h",y=-0.12,x=0.5,xanchor="center"),
            annotations=[dict(text=f"₹{latest['total_rev']:.0f}Cr",x=.5,y=.5,
                              font=dict(size=16,color=DARK,family="Inter"),showarrow=False)]
        )
        st.plotly_chart(fig3,use_container_width=True)

    qtv_g=(monthly["qtv_mau"].iloc[-1]/monthly["qtv_mau"].iloc[0]-1)*100
    ins(f"QuickTV grew <b>+{qtv_g:.0f}%</b> in 12 months — the fastest-growing platform. "
        f"ShareChat holds the largest revenue share at ₹{latest['sc_rev']:.0f} Cr/month. "
        f"Combined network is on course to exceed ₹{arr+200:.0f} Cr ARR in FY26-27.")


# ─── PAGE: USER ANALYTICS ───────────────────────────────────

def page_users(users):
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(kpi("Total Users (Sample)",f"{len(users):,}",desc="Synthetic profiles"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Premium Users",f"{users['is_premium'].mean()*100:.1f}%","+1.2 pp MoM",True,"Paid subscribers"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Avg Sessions / Month",f"{users['monthly_sessions'].mean():.0f}",desc="Per active user"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Median LTV",f"₹{users['ltv_inr'].median():,.0f}",desc="User lifetime value"), unsafe_allow_html=True)

    col1,col2,col3=st.columns(3)
    with col1:
        sec("Age Group Distribution")
        ao=["18-24","25-34","35-44","45-54","55+"]
        ac=users["age_group"].value_counts().reindex(ao).reset_index()
        ac.columns=["Age","Count"]
        fig=px.bar(ac,x="Age",y="Count",color_discrete_sequence=[ORANGE])
        fig.update_traces(marker_line_width=0)
        fig=base_layout(fig,280)
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        sec("Gender Split")
        gc=users["gender"].value_counts().reset_index(); gc.columns=["Gender","Count"]
        fig=px.pie(gc,values="Count",names="Gender",hole=.60,
                   color_discrete_sequence=[ORANGE,TEAL,GREEN])
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                          height=280,margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig,use_container_width=True)

    with col3:
        sec("Device Type")
        dc=users["device"].value_counts().reset_index(); dc.columns=["Device","Count"]
        fig=px.pie(dc,values="Count",names="Device",hole=.60,
                   color_discrete_sequence=COLOR_SEQ)
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                          height=280,margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig,use_container_width=True)

    col4,col5=st.columns([3,2])
    with col4:
        sec("Users by Language (15 Regional Languages)")
        lc=users["language"].value_counts().reset_index(); lc.columns=["Language","Users"]
        lc["Pct"]=(lc["Users"]/len(users)*100).round(1)
        fig=px.bar(lc,x="Users",y="Language",orientation="h",
                   color_discrete_sequence=[ORANGE],text="Pct")
        fig.update_traces(texttemplate="%{text:.1f}%",textposition="outside",marker_line_width=0)
        fig.update_layout(yaxis={"categoryorder":"total ascending"})
        fig=base_layout(fig,420)
        st.plotly_chart(fig,use_container_width=True)

    with col5:
        sec("Users by Region")
        rc=users["region"].value_counts().reset_index(); rc.columns=["Region","Users"]
        fig=px.pie(rc,values="Users",names="Region",hole=.55,
                   color_discrete_sequence=COLOR_SEQ)
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                          height=420,margin=dict(l=0,r=0,t=20,b=10))
        st.plotly_chart(fig,use_container_width=True)

    col6,col7=st.columns(2)
    with col6:
        sec("Session Duration by Platform")
        fig=px.box(users,x="platform",y="avg_session_min",color="platform",
                   color_discrete_map=PLT_MAP,
                   labels={"avg_session_min":"Session (min)","platform":""})
        fig.update_traces(showlegend=False)
        fig=base_layout(fig,280)
        st.plotly_chart(fig,use_container_width=True)

    with col7:
        sec("Avg Monthly Sessions by Platform")
        ps=users.groupby("platform")["monthly_sessions"].mean().reset_index()
        ps.columns=["Platform","Sessions"]
        fig=px.bar(ps,x="Platform",y="Sessions",color="Platform",text="Sessions",
                   color_discrete_map=PLT_MAP)
        fig.update_traces(texttemplate="%{text:.1f}",textposition="outside",
                          showlegend=False,marker_line_width=0)
        fig=base_layout(fig,280)
        st.plotly_chart(fig,use_container_width=True)


# ─── PAGE: CONTENT PERFORMANCE ──────────────────────────────

def page_content(content):
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(kpi("Content Items",f"{len(content):,}",desc="In analytical sample"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Avg Views / Post",f"{content['views'].mean():,.0f}","+12% MoM",True,"All formats"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Avg Engagement Rate",f"{content['engagement_rate'].mean()*100:.2f}%","+0.8 pp QoQ",True,"L+S+C / Views"), unsafe_allow_html=True)
    with c4:
        top_cat=content.groupby("category")["views"].sum().idxmax()
        st.markdown(kpi("Top Category",top_cat,desc="By total views"), unsafe_allow_html=True)

    col1,col2=st.columns(2)
    with col1:
        sec("Average Views by Content Type")
        cv=content.groupby("content_type")["views"].mean().sort_values().reset_index()
        fig=px.bar(cv,x="views",y="content_type",orientation="h",
                   color_discrete_sequence=[ORANGE],text="views")
        fig.update_traces(texttemplate="%{x:,.0f}",textposition="outside",marker_line_width=0)
        fig=base_layout(fig,300)
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        sec("Engagement Rate by Content Type")
        er=content.groupby("content_type")["engagement_rate"].mean().sort_values(ascending=False).reset_index()
        er["er_pct"]=er["engagement_rate"]*100
        fig=px.bar(er,x="content_type",y="er_pct",color_discrete_sequence=[ORANGE],text="er_pct")
        fig.update_traces(texttemplate="%{text:.2f}%",textposition="outside",marker_line_width=0)
        fig=base_layout(fig,300)
        fig.update_layout(yaxis_title="Engagement Rate (%)")
        st.plotly_chart(fig,use_container_width=True)

    col3,col4=st.columns([3,2])
    with col3:
        sec("Category Market Map — Views vs Engagement (bubble = # posts)")
        cat_agg=content.groupby("category").agg(
            total_views=("views","sum"),avg_er=("engagement_rate","mean"),count=("content_id","count")
        ).reset_index()
        cat_agg["views_m"]=(cat_agg["total_views"]/1e6).round(2)
        fig=px.scatter(cat_agg,x="views_m",y="avg_er",size="count",color="category",
                       text="category",size_max=36,color_discrete_sequence=COLOR_SEQ,
                       labels={"views_m":"Total Views (M)","avg_er":"Avg Engagement Rate"})
        fig.update_traces(textposition="top center",textfont_size=9,marker_opacity=.85)
        fig.update_layout(yaxis_tickformat=".1%")
        fig=base_layout(fig,380)
        st.plotly_chart(fig,use_container_width=True)

    with col4:
        sec("Content Share by Language")
        lc=content["language"].value_counts().reset_index(); lc.columns=["Language","Count"]
        fig=px.pie(lc,values="Count",names="Language",hole=.45,
                   color_discrete_sequence=COLOR_SEQ)
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                          height=380,margin=dict(l=0,r=0,t=20,b=10),legend=dict(font=dict(size=10)))
        st.plotly_chart(fig,use_container_width=True)

    sec("Top 10 Content Items by Views")
    top10=content.nlargest(10,"views")[["content_type","category","language","platform","views","likes","shares","engagement_rate"]].copy()
    top10.index=range(1,11)
    top10["views"]=top10["views"].apply(lambda x:f"{x:,.0f}")
    top10["likes"]=top10["likes"].apply(lambda x:f"{x:,.0f}")
    top10["shares"]=top10["shares"].apply(lambda x:f"{x:,.0f}")
    top10["engagement_rate"]=top10["engagement_rate"].apply(lambda x:f"{x*100:.2f}%")
    st.dataframe(top10,use_container_width=True)

    drama_er=content[content["content_type"]=="Drama Episode"]["engagement_rate"].mean()*100
    reel_er=content[content["content_type"]=="Reel"]["engagement_rate"].mean()*100
    hindi_share=content[content["language"]=="Hindi"]["views"].sum()/content["views"].sum()*100
    ins(f"Drama Episodes lead engagement at <b>{drama_er:.2f}%</b>, outperforming Reels ({reel_er:.2f}%). "
        f"Hindi content drives <b>{hindi_share:.0f}%</b> of total views — validating ShareChat's regional-first strategy.")


# ─── PAGE: MONETIZATION ─────────────────────────────────────

def page_monetization(monthly, revenue_det):
    latest=monthly.iloc[-1]
    avg_ecpm=revenue_det["ecpm"].mean(); total_imp=revenue_det["impressions_m"].sum()

    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(kpi("Monthly Revenue",f"₹{latest['total_rev']:.1f} Cr","+28% YoY",True,"All platforms"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Avg eCPM",f"₹{avg_ecpm:.1f}","+18% QoQ",True,"Effective CPM"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Total Impressions (90d)",f"{total_imp:.0f}M","+15% QoQ",True,"Last 90 days"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Ad Fill Rate","86.3%","+2.3 pp QoQ",True,"Demand / inventory"), unsafe_allow_html=True)

    sec("Revenue Trend — 12 Months by Platform (₹ Crore)")
    fig=go.Figure()
    for plat,col,clr in [("ShareChat","sc_rev",ORANGE),("Moj","moj_rev",PURPLE),("QuickTV","qtv_rev",GREEN)]:
        fig.add_trace(go.Bar(x=monthly["month_label"],y=monthly[col],name=plat,
                             marker_color=clr,marker_line_width=0))
    fig.add_trace(go.Scatter(x=monthly["month_label"],y=monthly["total_rev"],name="Total",
                             mode="lines",line=dict(color=GOLD,width=2,dash="dot"),marker=dict(size=4)))
    fig=base_layout(fig,320)
    fig.update_layout(barmode="stack",hovermode="x unified")
    st.plotly_chart(fig,use_container_width=True)

    col1,col2=st.columns(2)
    with col1:
        sec("Revenue by Ad Format (90 Days)")
        af=revenue_det.groupby("ad_format")["revenue_cr"].sum().sort_values().reset_index()
        fig=px.bar(af,x="revenue_cr",y="ad_format",orientation="h",
                   color_discrete_sequence=[ORANGE],text="revenue_cr")
        fig.update_traces(texttemplate="₹%{x:.1f}",textposition="outside",marker_line_width=0)
        fig=base_layout(fig,300)
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        sec("eCPM Trend by Ad Format — 7-Day Rolling Average")
        de=revenue_det.groupby(["date","ad_format"])["ecpm"].mean().reset_index()
        pivot=de.pivot(index="date",columns="ad_format",values="ecpm").rolling(7).mean()
        long=pivot.reset_index().melt(id_vars="date")
        fig=px.line(long.dropna(),x="date",y="value",color="ad_format",
                    color_discrete_sequence=COLOR_SEQ,
                    labels={"value":"eCPM (₹)","ad_format":"Format","date":""})
        fig=base_layout(fig,300)
        st.plotly_chart(fig,use_container_width=True)

    col3,col4=st.columns([2,1])
    with col3:
        sec("QoQ Revenue Waterfall")
        q=monthly.tail(6)
        q1=q.head(3)["total_rev"].sum(); q2=q.tail(3)["total_rev"].sum()
        sc_d=q.tail(3)["sc_rev"].sum()-q.head(3)["sc_rev"].sum()
        mj_d=q.tail(3)["moj_rev"].sum()-q.head(3)["moj_rev"].sum()
        qt_d=q.tail(3)["qtv_rev"].sum()-q.head(3)["qtv_rev"].sum()
        fig=go.Figure(go.Waterfall(
            orientation="v",measure=["absolute","relative","relative","relative","total"],
            x=["Q3 FY26","ShareChat","Moj","QuickTV","Q4 FY26"],
            text=[f"₹{q1:.1f}",f"+₹{sc_d:.1f}",f"+₹{mj_d:.1f}",f"+₹{qt_d:.1f}",f"₹{q2:.1f}"],
            textposition="outside",y=[q1,sc_d,mj_d,qt_d,0],
            connector={"line":{"color":BORDER}},
            increasing={"marker":{"color":GREEN}},
            totals={"marker":{"color":ORANGE}},
        ))
        fig=base_layout(fig,300)
        st.plotly_chart(fig,use_container_width=True)

    with col4:
        sec("ARPU by Platform")
        arpu=pd.DataFrame({
            "Platform":["ShareChat","Moj","QuickTV"],
            "MAU (M)":[latest["sc_mau"]/1e6,latest["moj_mau"]/1e6,latest["qtv_mau"]/1e6],
            "Revenue (₹ Cr)":[latest["sc_rev"],latest["moj_rev"],latest["qtv_rev"]],
        })
        arpu["ARPU (₹)"]=( arpu["Revenue (₹ Cr)"]*1e7/(arpu["MAU (M)"]*1e6) ).round(3)
        fig=px.bar(arpu,x="Platform",y="ARPU (₹)",color="Platform",text="ARPU (₹)",
                   color_discrete_map=PLT_MAP)
        fig.update_traces(texttemplate="₹%{text:.3f}",textposition="outside",
                          showlegend=False,marker_line_width=0)
        fig=base_layout(fig,300)
        st.plotly_chart(fig,use_container_width=True)


# ─── PAGE: RETENTION ────────────────────────────────────────

def page_retention(retention, daily_dau, monthly):
    m1=retention["M01"].mean(); m3=retention["M03"].dropna().mean()
    m6=retention["M06"].dropna().mean(); dau_mau=monthly["dau_ratio"].mean()

    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(kpi("M1 Retention (Avg)",f"{m1*100:.1f}%","+2.1 pp QoQ",True,"30-day cohort"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("M3 Retention (Avg)",f"{m3*100:.1f}%","+1.8 pp QoQ",True,"90-day cohort"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("M6 Retention (Avg)",f"{m6*100:.1f}%","+0.9 pp QoQ",True,"180-day cohort"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Avg DAU / MAU",f"{dau_mau*100:.1f}%","+3.2 pp YoY",True,"Network stickiness"), unsafe_allow_html=True)

    sec("Monthly Cohort Retention Heatmap (%)")
    ret_pct=retention.copy()*100
    z=ret_pct.values.tolist()
    txt=[[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in ret_pct.values]
    fig=go.Figure(go.Heatmap(
        z=z,x=ret_pct.columns.tolist(),y=ret_pct.index.tolist(),
        text=txt,texttemplate="%{text}",textfont=dict(size=10),
        colorscale=[[0,"#FFF5F2"],[.3,"#FFCDB5"],[.65,ORANGE],[1.0,PURPLE]],
        zmin=0,zmax=100,hoverongaps=False,showscale=True,
        colorbar=dict(title=dict(text="Ret %", font=dict(size=10))),
    ))
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                      height=410,margin=dict(l=4,r=4,t=8,b=4),font=dict(family="Inter"),
                      xaxis=dict(title=dict(text="Months Since Acquisition", font=dict(size=10, color=SUBTEXT))),
                      yaxis=dict(title=dict(text="Acquisition Cohort", font=dict(size=10, color=SUBTEXT))))
    st.plotly_chart(fig,use_container_width=True)

    col1,col2=st.columns([2,1])
    with col1:
        sec("Daily Active Users — Last 90 Days (Millions)")
        dl=daily_dau.melt(id_vars=["date"],value_vars=["sc_dau","moj_dau","qtv_dau"],var_name="plat",value_name="dau")
        dl["plat"]=dl["plat"].map({"sc_dau":"ShareChat","moj_dau":"Moj","qtv_dau":"QuickTV"})
        dl["dau_m"]=dl["dau"]/1e6
        fig=px.area(dl,x="date",y="dau_m",color="plat",
                    color_discrete_map=PLT_MAP,
                    labels={"dau_m":"DAU (M)","date":"","plat":"Platform"})
        fig=base_layout(fig,300)
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        sec("DAU/MAU — 12-Month Trend")
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=monthly["month_label"],y=monthly["dau_ratio"]*100,
                                 fill="tozeroy",mode="lines+markers",
                                 line=dict(color=ORANGE,width=2),
                                 fillcolor=rgba(ORANGE,.10),marker=dict(size=4,color=ORANGE),name="DAU/MAU %"))
        fig.add_hline(y=40,line_dash="dash",line_color=SUBTEXT,
                      annotation_text="Industry ~40%",annotation_position="bottom right",
                      annotation_font=dict(size=10,color=SUBTEXT))
        fig=base_layout(fig,300)
        fig.update_layout(yaxis_title="DAU/MAU (%)",yaxis_range=[30,65])
        st.plotly_chart(fig,use_container_width=True)

    sec("Average Retention Curve — All Cohorts")
    avg_ret=retention.mean()
    cols_a=[c for c in avg_ret.index if not np.isnan(avg_ret[c])]
    curve=pd.DataFrame({"Month":[int(c[1:]) for c in cols_a],"Retention":[avg_ret[c]*100 for c in cols_a]})
    fig=px.line(curve,x="Month",y="Retention",markers=True,
                labels={"Retention":"Retention Rate (%)","Month":"Months Since Signup"},
                color_discrete_sequence=[ORANGE])
    fig.update_traces(line_width=2.5,marker_size=8)
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                      height=260,margin=dict(l=4,r=4,t=8,b=4),font=dict(family="Inter"),
                      yaxis=dict(gridcolor="#F3F4F6",ticksuffix="%"),xaxis=dict(showgrid=False))
    fig.add_hrect(y0=0,y1=15,fillcolor=rgba(RED,.06),line_width=0,
                  annotation_text="Churn Zone",annotation_position="top left",
                  annotation_font=dict(size=10,color=RED))
    fig.add_hrect(y0=40,y1=65,fillcolor=rgba(GREEN,.08),line_width=0,
                  annotation_text="Strong Retention",annotation_position="top left",
                  annotation_font=dict(size=10,color=GREEN))
    st.plotly_chart(fig,use_container_width=True)

    ins(f"M1 retention of <b>{m1*100:.1f}%</b> significantly outperforms the social media benchmark of ~30-35%. "
        f"The {dau_mau*100:.1f}% DAU/MAU ratio — well above the 40% industry average — confirms regional language "
        f"content creates a strong daily habit loop. A 5 pp improvement in M3 retention adds ~₹120 Cr in annual incremental revenue.")


# ─── PAGE: LANGUAGE ANALYTICS ───────────────────────────────

def page_language(lang):
    top_lang=lang.loc[lang["mau_m"].idxmax(),"language"]
    top_er=lang.loc[lang["engagement_rate"].idxmax(),"language"]

    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(kpi("Languages Supported","15",desc="Regional languages"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Highest MAU Language",top_lang,desc="Monthly active users"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Best Engagement",top_er,desc="Highest engagement rate"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Total Creator Base",f"{lang['creator_k'].sum():.0f}K+",desc="Active creators"), unsafe_allow_html=True)

    col1,col2=st.columns(2)
    with col1:
        sec("MAU by Language (Millions)")
        df_s=lang.sort_values("mau_m")
        fig=px.bar(df_s,x="mau_m",y="language",orientation="h",
                   color_discrete_sequence=[ORANGE],text="mau_m")
        fig.update_traces(texttemplate="%{x:.1f}M",textposition="outside",marker_line_width=0)
        fig=base_layout(fig,460)
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        sec("Engagement Rate by Language")
        df_e=lang.sort_values("engagement_rate")
        df_e=df_e.copy(); df_e["er_pct"]=df_e["engagement_rate"]*100
        fig=px.bar(df_e,x="er_pct",y="language",orientation="h",
                   color_discrete_sequence=[ORANGE],text="er_pct")
        fig.update_traces(texttemplate="%{x:.1f}%",textposition="outside",marker_line_width=0)
        fig=base_layout(fig,460)
        st.plotly_chart(fig,use_container_width=True)

    col3,col4=st.columns([2,1])
    with col3:
        sec("Language Market Map — MAU vs Engagement (bubble = Revenue)")
        fig=px.scatter(lang,x="mau_m",y="engagement_rate",size="revenue_cr",color="language",
                       text="language",size_max=40,
                       color_discrete_sequence=COLOR_SEQ+[TEAL,GOLD,PURPLE,GREEN,ORANGE,SUBTEXT,"#3B82F6","#EC4899","#F59E0B"],
                       labels={"mau_m":"MAU (M)","engagement_rate":"Engagement Rate","revenue_cr":"Revenue (₹ Cr)"})
        fig.update_traces(textposition="top center",textfont_size=9,marker_opacity=.85)
        fig.update_layout(yaxis_tickformat=".1%")
        fig=base_layout(fig,400)
        st.plotly_chart(fig,use_container_width=True)

    with col4:
        sec("Revenue by Language (Top 8)")
        top8=lang.nlargest(8,"revenue_cr").sort_values("revenue_cr")
        fig=px.bar(top8,x="revenue_cr",y="language",orientation="h",
                   color_discrete_sequence=[ORANGE],text="revenue_cr")
        fig.update_traces(texttemplate="₹%{x:.0f}Cr",textposition="outside",marker_line_width=0)
        fig=base_layout(fig,400)
        st.plotly_chart(fig,use_container_width=True)

    sec("Full Language Metrics Table")
    disp=lang.copy()
    disp["MAU"]=disp["mau_m"].apply(lambda x:f"{x:.1f}M")
    disp["Engagement Rate"]=disp["engagement_rate"].apply(lambda x:f"{x*100:.2f}%")
    disp["Revenue"]=disp["revenue_cr"].apply(lambda x:f"₹{x:.1f} Cr")
    disp["Creators"]=disp["creator_k"].apply(lambda x:f"{x:.1f}K")
    disp["Avg Session"]=disp["avg_session_min"].apply(lambda x:f"{x:.1f} min")
    disp["Content/User"]=disp["content_per_user"].apply(lambda x:f"{x:.0f}")
    show=disp[["language","MAU","Engagement Rate","Revenue","Creators","Avg Session","Content/User"]]
    show=show.rename(columns={"language":"Language"}).sort_values("MAU",ascending=False)
    st.dataframe(show,use_container_width=True,hide_index=True)


# ─── MAIN ───────────────────────────────────────────────────

def main():
    # ── Load data
    monthly     = gen_monthly()
    users       = gen_users()
    content     = gen_content()
    retention   = gen_retention()
    daily_dau   = gen_dau()
    revenue_det = gen_revenue_daily()
    lang        = gen_language()

    # ── Sidebar — Filters
    with st.sidebar:
        # st.image("assets/logo.png", width=48)
        st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#6B7280;">Filters</div>', unsafe_allow_html=True)
        st.divider()

        platform_filter = st.multiselect(
            "Platform",
            ["ShareChat","Moj","QuickTV"],
            default=["ShareChat","Moj","QuickTV"],
        )
        language_filter = st.multiselect(
            "Language",
            ["Hindi","Telugu","Tamil","Bengali","Marathi","Gujarati","Kannada",
             "Malayalam","Punjabi","Odia","Bhojpuri","Assamese","Rajasthani","Haryanvi","Urdu"],
            default=["Hindi","Telugu","Tamil","Bengali","Marathi","Gujarati","Kannada",
                     "Malayalam","Punjabi","Odia","Bhojpuri","Assamese","Rajasthani","Haryanvi","Urdu"],
        )
        region_filter = st.multiselect(
            "Region",
            ["North","South","East","West"],
            default=["North","South","East","West"],
        )
        content_type_filter = st.multiselect(
            "Content Type",
            ["Short Video","Image Post","Text Post","Reel","Drama Episode","Live Stream"],
            default=["Short Video","Image Post","Text Post","Reel","Drama Episode","Live Stream"],
        )

        st.divider()
        latest=monthly.iloc[-1]
        st.markdown(f"""
        <div style="font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#9CA3AF;margin-bottom:12px;">Live Snapshot</div>
        <div style="margin-bottom:8px;">
          <div style="font-size:10px;color:#9CA3AF;text-transform:uppercase;letter-spacing:1px;">Total MMU</div>
          <div style="font-size:22px;font-weight:800;color:#111827;">{latest['total_mau']/1e6:.0f}M</div>
        </div>
        <div style="margin-bottom:8px;">
          <div style="font-size:10px;color:#9CA3AF;text-transform:uppercase;letter-spacing:1px;">Monthly Revenue</div>
          <div style="font-size:22px;font-weight:800;color:#111827;">₹{latest['total_rev']:.0f} Cr</div>
        </div>
        <div>
          <div style="font-size:10px;color:#9CA3AF;text-transform:uppercase;letter-spacing:1px;">DAU/MAU</div>
          <div style="font-size:22px;font-weight:800;color:#FF6B2C;">{latest['dau_ratio']*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Apply filters to datasets
    b64 = _logo_b64()
    filtered_users   = users[users["platform"].isin(platform_filter)
                             & users["language"].isin(language_filter)
                             & users["region"].isin(region_filter)] if platform_filter and language_filter and region_filter else users
    filtered_content = content[content["platform"].isin(platform_filter)
                               & content["content_type"].isin(content_type_filter)] if platform_filter and content_type_filter else content

    # ── Dashboard header
    st.markdown(f"""
    <div class="dash-hdr">
      <img src="data:image/png;base64,{b64}" style="width:38px;height:38px;border-radius:8px;flex-shrink:0;">
      <span class="dash-ttl">ShareChat &nbsp;·&nbsp; Analytics Intelligence Platform</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Tab navigation
    tabs = st.tabs(["OVERVIEW","USER ANALYTICS","CONTENT","MONETIZATION","RETENTION","LANGUAGE"])

    with tabs[0]: page_overview(monthly, revenue_det)
    with tabs[1]: page_users(filtered_users)
    with tabs[2]: page_content(filtered_content)
    with tabs[3]: page_monetization(monthly, revenue_det)
    with tabs[4]: page_retention(retention, daily_dau, monthly)
    with tabs[5]: page_language(lang)


if __name__ == "__main__":
    main()
