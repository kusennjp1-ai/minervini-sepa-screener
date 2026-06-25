"""
Mark Minervini SEPA Screener — Professional Trading Dashboard
一流デザイナー版: Glassmorphism UI + Market 360 Gauge + VCP Sparklines
全米国株対応 (ETF除外) | データソース: Yahoo Finance & GitHub US Stock List
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests

# ==================== ページ設定 ====================
st.set_page_config(
    page_title="SEPA Screener | Minervini",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== プロフェッショナルCSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    * { font-family: 'Inter', sans-serif; }
    .stApp { background: #0A0B0F; }

    .glass-card {
        background: rgba(20, 22, 30, 0.8);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
    }
    .gauge-container {
        position: relative;
        width: 200px;
        height: 100px;
        margin: 0 auto;
        overflow: hidden;
    }
    .gauge-bg {
        width: 200px;
        height: 100px;
        border-radius: 100px 100px 0 0;
        background: conic-gradient(from 180deg, #00C853 0deg, #FFD600 90deg, #FF1744 180deg);
        mask: radial-gradient(circle at 50% 100%, transparent 60%, black 61%);
        -webkit-mask: radial-gradient(circle at 50% 100%, transparent 60%, black 61%);
    }
    .gauge-needle {
        position: absolute;
        bottom: 0; left: 50%;
        width: 3px; height: 45px;
        background: white;
        transform-origin: bottom center;
        border-radius: 2px;
        box-shadow: 0 0 10px rgba(255,255,255,0.5);
        transition: transform 1s ease;
    }
    .gauge-score {
        position: absolute;
        bottom: -8px; left: 50%;
        transform: translateX(-50%);
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem; font-weight: 700; color: white;
    }
    .ticker-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        font-weight: 600; letter-spacing: 0.5px; font-size: 1.1rem;
    }
    .vcp-meter {
        height: 4px; background: rgba(255,255,255,0.08);
        border-radius: 2px; overflow: hidden; margin: 0.5rem 0;
    }
    .vcp-fill {
        height: 100%; border-radius: 2px;
        transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-pill {
        display: inline-block; padding: 0.2rem 0.6rem;
        border-radius: 12px; font-size: 0.75rem; font-weight: 500;
    }
    .pill-success { background: rgba(0,200,83,0.12); color: #00E676; }
    .pill-warning { background: rgba(255,214,0,0.12); color: #FFD600; }
    .pill-danger { background: rgba(255,23,68,0.12); color: #FF1744; }
    .pill-neutral { background: rgba(255,255,255,0.06); color: #8892A4; }

    [data-testid="stSidebar"] {
        background: rgba(10,11,15,0.95);
        border-right: 1px solid rgba(255,255,255,0.04);
    }
    .stButton > button {
        background: linear-gradient(135deg, #1A1F2E, #252B3D) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important; color: #E0E0E0 !important;
        font-weight: 500 !important; letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important; padding: 0.6rem 1.2rem !important;
    }
    .stButton > button:hover {
        border-color: rgba(255,255,255,0.2) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
        transform: translateY(-1px);
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, #D4AF37, #C5A028) !important;
        color: #0A0B0F !important; font-weight: 600 !important; border: none !important;
    }
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ==================== キャッシュ ====================
@st.cache_data(ttl=3600)
def download_data(ticker, period='2y'):
    try:
        return yf.download(ticker, period=period, progress=False)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=86400)
def get_sp500_list():
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        return pd.read_html(url)[0]['Symbol'].str.replace('.', '-', regex=False).tolist()
    except:
        return ['AAPL','MSFT','AMZN','NVDA','GOOGL','META','TSLA','AVGO','COST','NFLX',
                'AMD','ADBE','CRM','QCOM','TXN','INTU','AMAT','MU','ADI','LRCX',
                'INTC','PYPL','BKNG','ISRG','REGN','VRTX','GILD','AMGN','PANW','SNPS']

@st.cache_data(ttl=86400)
def get_nasdaq100_list():
    return ['AAPL','MSFT','AMZN','NVDA','GOOGL','META','TSLA','AVGO','COST','NFLX',
            'AMD','ADBE','CRM','QCOM','TXN','INTU','AMAT','MU','ADI','LRCX',
            'INTC','PYPL','BKNG','ISRG','REGN','VRTX','GILD','AMGN','PANW','SNPS',
            'CDNS','KLAC','ASML','MELI','CSX','MAR','ORLY','CTAS','DXCM','ROST',
            'ODFL','IDXX','MNST','KDP','PAYX','PCAR','WDAY','ADSK','TEAM','CRWD',
            'MRVL','DDOG','ZS','FTNT','MDB','SPLK']

@st.cache_data(ttl=86400)
def get_all_us_stocks():
    """
    GitHub上の全米国株リストを取得し、ETF・優先証券等を簡易除外する
    リスト提供: https://github.com/rreichel3/US-Stock-Symbols
    """
    try:
        url = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/all/all_tickers.txt"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        all_tickers = resp.text.strip().split('\n')
        # フィルタ: ドット(優先株等)を含まない、4文字以上（ETFの多くは3文字以下のため）
        # ただし有名ETF(SPY,QQQ等)は3文字なので、それらは明示的に除外する
        etf_exclude_list = {'SPY', 'QQQ', 'IWM', 'DIA', 'XLF', 'XLE', 'XLK', 'XLV', 'XLY', 'XLP',
                           'XLI', 'XLB', 'XLU', 'XLC', 'XME', 'XRT', 'XHB', 'XOP', 'XBI', 'XSD'}
        filtered = []
        for t in all_tickers:
            t = t.strip().upper()
            if not t: continue
            if '.' in t: continue          # 優先株等
            if len(t) < 4:                 # 3文字以下のシンボル
                if t in etf_exclude_list:  # 有名ETFだけ除去
                    continue
                # それ以外の3文字は個別株の可能性があるので残す（ただしETFも多いので注意）
                # ここでは全て許可（後で API の quoteType で厳密に除外する方が正確だが時間がかかる）
            filtered.append(t)
        return list(dict.fromkeys(filtered))  # 重複除去
    except Exception as e:
        st.warning(f"全米リスト取得失敗: {e}。S&P500にフォールバックします。")
        return get_sp500_list()

@st.cache_data(ttl=3600)
def get_industry(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get('sector','Unknown'), info.get('industry','Unknown')
    except:
        return 'Unknown','Unknown'

# ==================== ロジック ====================
def evaluate_market_360():
    try:
        sp500 = yf.download('^GSPC', period='1y', progress=False)
        vix = yf.download('^VIX', period='1mo', progress=False)
        if sp500.empty: return 'UPTREND_UNDER_PRESSURE', 55, {}
        details, score = {}, 0
        sp500['SMA50'] = sp500['Close'].rolling(50).mean()
        sp500['SMA150'] = sp500['Close'].rolling(150).mean()
        sp500['SMA200'] = sp500['Close'].rolling(200).mean()
        latest = sp500.iloc[-1]
        if (latest['Close'] > latest['SMA50'] > latest['SMA150'] > latest['SMA200']).all():
            score += 25; details['trend'] = 'FULL_BULL'
        elif latest['Close'] > latest['SMA200']:
            score += 15; details['trend'] = 'BULL'
        else:
            details['trend'] = 'BEAR'
        sma50_up = sp500['SMA50'].diff(5).iloc[-1] > 0 if len(sp500)>5 else False
        sma150_up = sp500['SMA150'].diff(5).iloc[-1] > 0 if len(sp500)>150 else False
        sma200_up = sp500['SMA200'].diff(5).iloc[-1] > 0 if len(sp500)>200 else False
        if sma50_up and sma150_up: score += 10
        if sma200_up: score += 5
        if not vix.empty:
            v = vix['Close'].iloc[-1]; details['vix'] = f'{v:.1f}'
            score += 10 if v<20 else (5 if v<30 else -5)
        h52 = sp500['High'].rolling(252).max().iloc[-1]
        if not pd.isna(h52):
            dd = latest['Close']/h52; details['drawdown'] = f'{dd*100:.1f}%'
            score += 10 if dd>0.9 else (5 if dd>0.8 else 0)
        score = max(0,min(100,score))
        if score >= 70: mode = 'CONFIRMED_UPTREND'
        elif score >= 50: mode = 'UPTREND_UNDER_PRESSURE'
        else: mode = 'MARKET_IN_CORRECTION'
        return mode, score, details
    except Exception as e:
        return 'ERROR', 0, {'error':str(e)}

def calc_rs(df):
    try:
        c=df['Close']
        if len(c)<252: return 0
        r1=c.iloc[-1]/c.iloc[-63]-1; r2=c.iloc[-1]/c.iloc[-126]-1
        r3=c.iloc[-1]/c.iloc[-189]-1; r4=c.iloc[-1]/c.iloc[-252]-1
        return (r1*0.4+r2*0.2+r3*0.2+r4*0.2)*100
    except: return 0

def check_tt(df):
    if len(df)<200: return False,0
    df['SMA50']=df['Close'].rolling(50).mean()
    df['SMA150']=df['Close'].rolling(150).mean()
    df['SMA200']=df['Close'].rolling(200).mean()
    r=df.iloc[-1]
    if not (r['Close']>r['SMA150']>r['SMA200']): return False,0
    if not (r['SMA150']>r['SMA200']): return False,0
    if len(df)<221: return False,0
    if df['SMA200'].iloc[-1]<=df['SMA200'].iloc[-21]: return False,0
    if not (r['SMA50']>r['SMA150'] and r['SMA50']>r['SMA200']): return False,0
    if not (r['Close']>r['SMA50']): return False,0
    l52=df['Low'].rolling(252).min().iloc[-1]; h52=df['High'].rolling(252).max().iloc[-1]
    if r['Close']<l52*1.3: return False,0
    if r['Close']<h52*0.75: return False,0
    return True, calc_rs(df)

def detect_vcp(df):
    if len(df)<60: return {'score':0,'status':'DATA_ERR','contractions':0,'vol_dry':False,'tight':False,'pivot_dist':0}
    swings=[]; ct='H'; cp=df.iloc[0]['High']
    for i in range(1,len(df)):
        row=df.iloc[i]
        if ct=='H':
            if row['High']>cp: cp=row['High']
            elif row['Low']<cp*0.95: swings.append({'t':'H','p':cp}); ct='L'; cp=row['Low']
        else:
            if row['Low']<cp: cp=row['Low']
            elif row['High']>cp*1.05: swings.append({'t':'L','p':cp}); ct='H'; cp=row['High']
    if len(swings)<4: return {'score':0,'status':'SWINGS_LOW','contractions':0,'vol_dry':False,'tight':False,'pivot_dist':0}
    declines=[]
    for i in range(len(swings)-1):
        if swings[i]['t']=='H' and swings[i+1]['t']=='L':
            declines.append((swings[i]['p']-swings[i+1]['p'])/swings[i]['p'])
    cc=sum(1 for j in range(1,len(declines)) if declines[j]<declines[j-1]*0.85)
    df['vm50']=df['Volume'].rolling(50).mean()
    rv=df['Volume'].iloc[-5:].mean(); vm=df['vm50'].iloc[-1]
    vd=rv<vm*0.7 if vm>0 else False
    rr=(df['High'].iloc[-5:]-df['Low'].iloc[-5:]).mean()
    pr=(df['High'].iloc[-20:-5]-df['Low'].iloc[-20:-5]).mean()
    tight=rr<pr*0.5 if pr>0 else False
    hs=[s for s in swings if s['t']=='H']
    pivot=hs[-1]['p'] if hs else df['Close'].iloc[-1]
    pd=(pivot-df['Close'].iloc[-1])/pivot*100
    score=min(cc,3)*20 + (20 if vd else 0) + (15 if tight else 0) + (10 if 0<=pd<=5 else 0)
    if score>=70: status='VCP_READY'
    elif score>=50: status='VCP_FORMING'
    elif score>=30: status='VCP_EARLY'
    else: status='NONE'
    return {'score':score,'status':status,'contractions':cc,'vol_dry':vd,'tight':tight,'pivot_dist':pd}

def check_fund(ticker):
    try:
        q=yf.Ticker(ticker).quarterly_financials
        if q is None or q.empty: return False,{}
        info={}
        for k in ['Diluted EPS','Basic EPS']:
            if k in q.index and len(q.loc[k])>=8:
                e=q.loc[k]; g=(e.iloc[0]-e.iloc[4])/abs(e.iloc[4])*100 if e.iloc[4]!=0 else 0
                info['eps_growth']=f'{g:.1f}%'; info['eps_ok']=g>=20; break
        if 'Total Revenue' in q.index and len(q.loc['Total Revenue'])>=8:
            r=q.loc['Total Revenue']; g=(r.iloc[0]-r.iloc[4])/abs(r.iloc[4])*100 if r.iloc[4]!=0 else 0
            info['rev_growth']=f'{g:.1f}%'; info['rev_ok']=g>=15
        return (info.get('eps_ok',False) or info.get('rev_ok',False)), info
    except: return False,{}

def make_sparkline(df):
    if len(df)<20: return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index[-30:], y=df['Close'].iloc[-30:],
        mode='lines', line=dict(color='#4A5568', width=1.2),
        fill='tozeroy', fillcolor='rgba(74,85,104,0.1)'
    ))
    fig.update_layout(
        template='plotly_dark', height=80, width=200,
        margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False
    )
    return fig

# ==================== UI ====================
st.markdown("""
<div style="display:flex; align-items:center; justify-content:space-between; padding:1rem 0;">
    <div style="display:flex; align-items:center; gap:0.75rem;">
        <span style="font-size:2rem; filter:drop-shadow(0 0 8px rgba(212,175,55,0.4));">🏛️</span>
        <div>
            <div style="font-size:1.4rem; font-weight:700; letter-spacing:-0.5px; color:#FFFFFF;">MARKET 360</div>
            <div style="font-size:0.75rem; color:#8892A4; letter-spacing:1.5px; text-transform:uppercase;">Minervini SEPA Screener</div>
        </div>
    </div>
    <div style="font-family:'JetBrains Mono',monospace; color:#4A5568; font-size:0.85rem;">
        {now}
    </div>
</div>
""".format(now=datetime.now().strftime('%Y/%m/%d %H:%M:%S EST')), unsafe_allow_html=True)

# Market 360 パネル
mode, score, details = evaluate_market_360()

mode_map = {
    'CONFIRMED_UPTREND': ('🟢 攻め', '#00C853', 'CONFIRMED UPTREND'),
    'UPTREND_UNDER_PRESSURE': ('🟡 慎重', '#FFD600', 'UPTREND UNDER PRESSURE'),
    'MARKET_IN_CORRECTION': ('🔴 待ち', '#FF1744', 'MARKET IN CORRECTION'),
    'ERROR': ('⚪ エラー', '#8892A4', 'ERROR')
}
mode_emoji, mode_color, mode_label = mode_map.get(mode, mode_map['ERROR'])
needle_angle = -90 + (score/100)*180

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;">
        <div style="font-size:0.75rem; color:#8892A4; letter-spacing:1px; margin-bottom:0.5rem;">MARKET SCORE</div>
        <div class="gauge-container">
            <div class="gauge-bg"></div>
            <div class="gauge-needle" style="transform:rotate({needle_angle}deg);"></div>
            <div class="gauge-score">{score}</div>
        </div>
        <div style="color:{mode_color}; font-weight:600; margin-top:0.5rem;">{mode_emoji} {mode_label}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c21, c22, c23 = st.columns(3)
    with c21:
        st.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:0.65rem; color:#8892A4; letter-spacing:1px;">VIX</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:1.5rem; font-weight:600; color:#E0E0E0;">{details.get('vix','N/A')}</div>
            <div class="metric-pill {'pill-success' if float(details.get('vix',20)) < 20 else 'pill-warning' if float(details.get('vix',20)) < 30 else 'pill-danger'}">{'LOW' if float(details.get('vix',20))<20 else 'MID' if float(details.get('vix',20))<30 else 'HIGH'}</div>
        </div>
        """, unsafe_allow_html=True)
    with c22:
        st.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:0.65rem; color:#8892A4; letter-spacing:1px;">TREND</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:1.5rem; font-weight:600; color:#E0E0E0;">{details.get('trend','N/A')}</div>
            <div class="metric-pill {'pill-success' if details.get('trend')=='FULL_BULL' else 'pill-warning' if details.get('trend')=='BULL' else 'pill-danger'}">{details.get('trend','N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    with c23:
        st.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:0.65rem; color:#8892A4; letter-spacing:1px;">52W DIST</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:1.5rem; font-weight:600; color:#E0E0E0;">{details.get('drawdown','N/A')}</div>
            <div class="metric-pill pill-neutral">ATR</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;">
        <div style="font-size:0.75rem; color:#8892A4; letter-spacing:1px;">S&P 500</div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:2rem; font-weight:700; color:white;">$SPX</div>
        <div style="color:{mode_color}; margin-top:0.3rem;">{mode_label}</div>
    </div>
    """, unsafe_allow_html=True)

# サイドバー
with st.sidebar:
    st.markdown("### ⚙️ SCAN SETTINGS")
    uo = st.selectbox(
        "UNIVERSE",
        [
            "ALL US STOCKS (ex-ETF, ~6000)",
            "S&P 500 ALL (500)",
            "S&P 500 + Nasdaq 100 (600)",
            "NASDAQ 100 (100)",
            "CUSTOM"
        ],
        index=0
    )
    vt = st.slider("VCP THRESHOLD", 20, 80, 30, 5, format="%d/100")
    mr = st.slider("MAX RESULTS", 5, 30, 15, 5)
    
    if uo == "ALL US STOCKS (ex-ETF, ~6000)":
        with st.spinner("全米株リスト取得中..."):
            universe = get_all_us_stocks()
        st.info(f"⚡ 全米銘柄数: {len(universe)} (処理に時間がかかります)")
    elif uo == "S&P 500 ALL (500)":
        universe = get_sp500_list()
    elif uo == "S&P 500 + Nasdaq 100 (600)":
        sp500 = get_sp500_list()
        nasdaq100 = get_nasdaq100_list()
        universe = list(dict.fromkeys(sp500 + nasdaq100))
    elif uo == "NASDAQ 100 (100)":
        universe = get_nasdaq100_list()
    else:
        custom_text = st.text_area(
            "TICKERS (comma separated)",
            "AAPL, MSFT, NVDA"
        )
        universe = [s.strip().upper() for s in custom_text.split(',') if s.strip()]
    
    st.metric("TOTAL TICKERS", len(universe))
    run_btn = st.button("🚀 RUN SCREENING", use_container_width=True, type="primary")
    st.markdown("---")
    st.caption("© 2026 SEPA Screener\nMinervini Methodology")

# スクリーニング実行
if run_btn:
    with st.spinner(f"SCANNING {len(universe)} TICKERS..."):
        # RS計算
        rs_map = {}
        progress_text = st.empty()
        for i, sym in enumerate(universe):
            try:
                df = download_data(sym, '2y')
                if len(df) >= 200:
                    raw = calc_rs(df); _, ind = get_industry(sym)
                    rs_map[sym] = {'raw': raw, 'industry': ind}
            except: pass
            if (i+1) % 200 == 0:
                progress_text.text(f"RS計算中... {i+1}/{len(universe)}")
        
        progress_text.empty()

        df_rs = pd.DataFrame.from_dict(rs_map, orient='index')
        if df_rs.empty:
            st.warning("RSデータが空です。Yahoo Financeの接続を確認してください。")
            ir_map = {}
        else:
            ic = df_rs['industry'].value_counts()
            vi = ic[ic >= 2].index
            df_rs = df_rs.reset_index().rename(columns={'index': 'ticker'})
            df_rs['irs'] = 0.0
            df_rs['raw'] = pd.to_numeric(df_rs['raw'], errors='coerce').fillna(0)

            for ind in vi:
                ind_mask = df_rs['industry'] == ind
                valid_mask = ind_mask & (df_rs['raw'] != 0)
                if valid_mask.sum() > 1:
                    df_rs.loc[valid_mask, 'irs'] = df_rs.loc[valid_mask, 'raw'].rank(pct=True) * 100

            df_rs = df_rs.set_index('ticker')
            ir_map = df_rs['irs'].to_dict()

        # スクリーニング
        results = []
        for sym in rs_map.keys():  # RSが計算できた銘柄だけ対象
            r = {'ticker': sym, 'passed': False, 'df': None, 'vcp_score': 0, 'vcp_status': 'NONE',
                 'irs': 0, 'rs_raw': 0, 'vcp': {}, 'fund': {}}
            try:
                df = download_data(sym, '2y')
                if df.empty or len(df) < 200: continue
                r['df'] = df
                tt_ok, rs_raw = check_tt(df)
                if not tt_ok: continue
                r['rs_raw'] = rs_raw
                irs = ir_map.get(sym, 0); r['irs'] = irs
                if irs < 70: continue
                fok, fi = check_fund(sym)
                if not fok: continue
                r['fund'] = fi
                v = detect_vcp(df)
                r['vcp_score'] = v['score']; r['vcp_status'] = v['status']; r['vcp'] = v
                if v['score'] >= vt: r['passed'] = True; results.append(r)
            except: pass
        
        results.sort(key=lambda x: x['vcp_score'], reverse=True)
        st.session_state['results'] = results[:mr]
        st.session_state['mode'] = mode

# 結果表示
if 'results' in st.session_state and st.session_state['results']:
    st.markdown("---")
    if st.session_state['mode'] == 'MARKET_IN_CORRECTION':
        st.warning("⚠️ MARKET IN CORRECTION — 新規ポジション非推奨")
    
    st.markdown(f"### 🏆 SCREENING RESULTS ({len(st.session_state['results'])} TICKERS)")
    
    for i, r in enumerate(st.session_state['results']):
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns([1.5, 2.5, 1.5, 1.5])
            
            with c1:
                st.markdown(f"""
                <div class="ticker-badge">${r['ticker']}</div>
                <div style="margin-top:0.5rem;">
                    <span class="metric-pill {'pill-success' if r['vcp_status']=='VCP_READY' else 'pill-warning' if r['vcp_status']=='VCP_FORMING' else 'pill-neutral'}">
                        {r['vcp_status'].replace('_',' ')}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                spark = make_sparkline(r.get('df'))
                if spark: st.plotly_chart(spark, use_container_width=True)
            
            with c2:
                sc = r['vcp_score']
                bc = '#00E676' if sc >= 70 else '#FFD600' if sc >= 50 else '#FF9100'
                st.markdown(f"""
                <div style="margin:0.3rem 0;">
                    <div style="display:flex; justify-content:space-between; font-size:0.7rem; color:#8892A4;">
                        <span>VCP SCORE</span><span style="font-family:'JetBrains Mono',monospace; color:{bc};">{sc}/100</span>
                    </div>
                    <div class="vcp-meter">
                        <div class="vcp-fill" style="width:{sc}%; background:{bc};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                v = r['vcp']
                m1, m2, m3 = st.columns(3)
                m1.metric('CONTRACTIONS', v.get('contractions', 0))
                m2.metric('DRY-UP', '✅' if v.get('vol_dry') else '❌')
                m3.metric('TIGHT', '✅' if v.get('tight') else '❌')
            
            with c3:
                st.markdown(f"""
                <div style="font-size:0.7rem; color:#8892A4;">INDUSTRY RS</div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:1.8rem; font-weight:700; color:white;">{r['irs']:.0f}</div>
                <div style="font-size:0.65rem; color:#4A5568;">RAW RS: {r['rs_raw']:.1f}</div>
                """, unsafe_allow_html=True)
            
            with c4:
                fi = r['fund']
                eps = fi.get('eps_growth', 'N/A')
                rev = fi.get('rev_growth', 'N/A')
                st.metric('EPS GROWTH', eps)
                st.metric('REV GROWTH', rev)
            
            with st.expander(f"📈 {r['ticker']} DETAILED CHART"):
                df = r.get('df')
                if df is not None and len(df) > 50:
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                       vertical_spacing=0.03, row_heights=[0.7, 0.3])
                    
                    fig.add_trace(
                        go.Candlestick(
                            x=df.index[-90:], open=df['Open'].iloc[-90:],
                            high=df['High'].iloc[-90:], low=df['Low'].iloc[-90:],
                            close=df['Close'].iloc[-90:], name='',
                            increasing_line_color='#00E676', decreasing_line_color='#FF1744',
                            increasing_fillcolor='rgba(0,230,118,0.1)', decreasing_fillcolor='rgba(255,23,68,0.1)'
                        ), row=1, col=1
                    )
                    
                    for ma, color, name in [('SMA50', '#448AFF', '50'), ('SMA150', '#FFD600', '150'), ('SMA200', '#FF9100', '200')]:
                        if ma in df.columns:
                            fig.add_trace(go.Scatter(x=df.index[-90:], y=df[ma].iloc[-90:],
                                                    mode='lines', name=f'{name}SMA',
                                                    line=dict(color=color, width=1.2)), row=1, col=1)
                    
                    colors = ['#00E676' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#FF1744' 
                             for i in range(len(df)-90, len(df))]
                    fig.add_trace(go.Bar(x=df.index[-90:], y=df['Volume'].iloc[-90:],
                                        name='', marker_color=colors, opacity=0.3), row=2, col=1)
                    
                    fig.update_layout(
                        template='plotly_dark',
                        height=450,
                        xaxis_rangeslider_visible=False,
                        showlegend=False,
                        margin=dict(l=10, r=10, t=20, b=10),
                        paper_bgcolor='rgba(10,11,15,1)',
                        plot_bgcolor='rgba(10,11,15,1)',
                        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        yaxis2=dict(gridcolor='rgba(255,255,255,0.05)')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

elif run_btn:
    st.markdown("---")
    st.markdown("""
    <div class="glass-card" style="text-align:center; padding:3rem;">
        <div style="font-size:3rem;">🔍</div>
        <div style="font-size:1.2rem; font-weight:500; color:#8892A4; margin:1rem 0;">NO TICKERS FOUND</div>
        <div style="font-size:0.85rem; color:#4A5568;">条件を満たす銘柄はありません。相場の改善を待ちましょう。</div>
        <div style="font-size:0.75rem; color:#2D3143; margin-top:0.5rem; font-style:italic;">"Discipline is the bridge between goals and accomplishment."</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; font-size:0.7rem; color:#2D3143;">
    <span>SEPA Screener v2.1 — Mark Minervini Methodology | Universe: All US Stocks</span>
    <span>Data: Yahoo Finance | Not Financial Advice</span>
</div>
""", unsafe_allow_html=True)
