import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title='Sonar Trading Academy', page_icon='📈', layout='centered', initial_sidebar_state='collapsed')
st.markdown('''<style>
.stApp{background:#0a101a;color:#f3f6fa} .block-container{max-width:760px;padding-top:1rem;padding-bottom:3rem}
h1,h2,h3,p,label,span,div{color:inherit} div[data-testid="stMetric"]{background:#152234;border-radius:12px;padding:12px}
.stButton>button[kind="primary"]{background:#11b89a;color:#07131b;border:0;font-weight:800}
.stButton>button{width:100%;min-height:45px;border-radius:10px}
div[data-testid="stRadio"] label{background:#142133;border-radius:9px;padding:7px 10px;margin:3px 0}
[data-testid="stHeader"]{background:transparent}
</style>''', unsafe_allow_html=True)

# All entries and future candles below are manually constructed synthetic teaching cases.
# The displayed outcome is illustrative and not a probability estimate.
CASES = [
 dict(name='Ascending triangle', family='Ascending triangle', direction='Bullish breakout is plausible, but wait for confirmation', result='UP', seed=15,
      anchors=[(0,90),(5,94),(10,91),(15,97),(20,93),(25,98),(30,95),(35,99),(40,97),(44,99)],
      future=[(45,100),(48,104),(52,107),(56,105)],
      why='Resistance is repeatedly tested near the same high while swing lows rise. A convincing close above resistance with participation supports a bullish breakout; a fall through the rising support weakens the setup.',
      invalid='A sustained breakdown beneath the rising support, or a failed breakout back into the triangle.'),
 dict(name='Descending triangle', family='Descending triangle', direction='Bearish breakdown is plausible, but wait for confirmation', result='DOWN', seed=18,
      anchors=[(0,110),(5,106),(10,109),(15,104),(20,107),(25,103),(30,105),(35,102),(40,103),(44,102)],
      future=[(45,101),(49,97),(53,95),(56,96)],
      why='Support is tested near a similar low while swing highs descend. A close below support may signal downside continuation, but breakdowns can fail.',
      invalid='A sustained move above the descending resistance or quick recovery above broken support.'),
 dict(name='Double bottom', family='Double bottom', direction='Potential bullish reversal if neckline breaks', result='UP', seed=21,
      anchors=[(0,110),(7,102),(12,96),(18,103),(24,107),(30,99),(35,96.5),(40,104),(44,108)],
      future=[(45,109),(49,114),(53,116),(56,114)],
      why='Price visits a similar low twice with a bounce in between. The stronger reversal clue is a confirmed break over the intervening swing high (neckline).',
      invalid='A decisive break beneath both bottom lows.'),
 dict(name='Double top', family='Double top', direction='Potential bearish reversal if neckline breaks', result='DOWN', seed=31,
      anchors=[(0,94),(6,102),(12,109),(18,103),(25,99),(31,106),(36,109.5),(40,102),(44,98)],
      future=[(45,97),(49,93),(53,90),(56,92)],
      why='Two highs near the same resistance with an intervening pullback can create a double top. A close below the intervening low improves confirmation.',
      invalid='A convincing breakout above the pair of highs.'),
 dict(name='Bull flag', family='Bull flag', direction='Possible upward continuation after breakout', result='UP', seed=8,
      anchors=[(0,90),(7,94),(14,108),(20,114),(25,110),(30,112),(35,108),(40,110),(44,107.5)],
      future=[(45,111),(48,115),(52,119),(56,118)],
      why='A steep advance is followed by a smaller downward/slanted consolidation. An upside break of the flag is a possible continuation trigger.',
      invalid='Price loses the flag support and fails to reclaim it.'),
 dict(name='Bear flag', family='Bear flag', direction='Possible downward continuation after breakdown', result='DOWN', seed=14,
      anchors=[(0,118),(8,112),(15,99),(20,94),(25,98),(30,96),(35,100),(40,98),(44,101)],
      future=[(45,97),(49,92),(53,88),(56,90)],
      why='A steep decline is followed by a modest upward consolidation. A breakdown below that flag can suggest downside continuation.',
      invalid='A sustained breakout above the flag resistance.'),
 dict(name='Range / no breakout', family='Sideways range', direction='No trade until price breaks and confirms a direction', result='RANGE', seed=10,
      anchors=[(0,103),(5,108),(10,100),(15,107),(20,101),(25,108),(30,100),(35,107),(40,101),(44,105)],
      future=[(45,102),(49,106),(53,101),(56,105)],
      why='Several bounces between similar support and resistance levels show indecision. Predicting a directional breakout before it happens is a weak signal.',
      invalid='A confirmed breakout with follow-through above resistance or below support.'),
 dict(name='False breakout', family='False breakout / bull trap', direction='Breakout has failed; downside risk has increased', result='DOWN', seed=16,
      anchors=[(0,98),(5,102),(10,99),(15,103),(20,99),(25,103),(30,100),(35,104),(39,107),(42,103),(44,99)],
      future=[(45,98),(49,94),(53,92),(56,95)],
      why='Price briefly pushes over repeated resistance, then falls back below it. A failed break can trap breakout buyers, but it does not guarantee a decline.',
      invalid='A sustained reclaim of the broken resistance with follow-through.'),
]
PATTERNS=[x['family'] for x in CASES]
OUTLOOK=['Bullish breakout is plausible, but wait for confirmation', 'Bearish breakdown is plausible, but wait for confirmation',
         'Potential bullish reversal if neckline breaks','Potential bearish reversal if neckline breaks',
         'Possible upward continuation after breakout','Possible downward continuation after breakdown',
         'No trade until price breaks and confirms a direction', 'Breakout has failed; downside risk has increased']

def candles(case):
    rng=np.random.default_rng(case['seed'])
    anchors=case['anchors']
    x=np.arange(45)
    mid=np.interp(x,[p[0] for p in anchors],[p[1] for p in anchors])
    mid=mid+rng.normal(0,.32,len(x))
    op=np.r_[mid[0]-.3,mid[:-1]] + rng.normal(0,.24,len(mid))
    cl=mid+rng.normal(0,.2,len(mid))
    hi=np.maximum(op,cl)+rng.uniform(.3,.9,len(mid))
    lo=np.minimum(op,cl)-rng.uniform(.3,.9,len(mid))
    future_x=np.arange(45,57)
    future_mid=np.interp(future_x,[p[0] for p in case['future']],[p[1] for p in case['future']])+rng.normal(0,.22,12)
    fop=np.r_[cl[-1], future_mid[:-1]]+rng.normal(0,.20,12)
    fcl=future_mid+rng.normal(0,.18,12)
    fhi=np.maximum(fop,fcl)+rng.uniform(.25,.7,12)
    flo=np.minimum(fop,fcl)-rng.uniform(.25,.7,12)
    return pd.DataFrame({'x':np.arange(57),'open':np.r_[op,fop], 'high':np.r_[hi,fhi], 'low':np.r_[lo,flo], 'close':np.r_[cl,fcl]})

def graph(case,reveal=False):
    df=candles(case)
    chart=df if reveal else df.iloc[:45]
    fig=go.Figure(data=go.Candlestick(x=chart.x,open=chart.open,high=chart.high,low=chart.low,close=chart.close,
          increasing_line_color='#13d7a7',decreasing_line_color='#f07583',name='Practice'))
    if reveal:
        fig.add_vline(x=44.5,line_width=2,line_dash='dash',line_color='#ffcb62')
        fig.add_annotation(x=45,y=float(df.high.max())+1,text='REVEAL →',showarrow=False,font=dict(color='#ffcb62',size=12))
    fig.update_layout(height=320,margin=dict(l=0,r=0,t=14,b=5),paper_bgcolor='#111c2b',plot_bgcolor='#111c2b',
                      font_color='#d8e2ed',showlegend=False,dragmode='pan',xaxis_rangeslider_visible=False,
                      xaxis=dict(title='Illustrative candles',showgrid=True,gridcolor='#22324a',zeroline=False),
                      yaxis=dict(title='Synthetic price',showgrid=True,gridcolor='#22324a',zeroline=False))
    return fig

if 'index' not in st.session_state: st.session_state.index=0
if 'answers' not in st.session_state: st.session_state.answers={}
if 'submitted' not in st.session_state: st.session_state.submitted=False
if 'pattern' not in st.session_state: st.session_state.pattern=PATTERNS[0]
if 'outlook' not in st.session_state: st.session_state.outlook=OUTLOOK[0]
if 'nextmove' not in st.session_state: st.session_state.nextmove='UP'

def move(delta):
    st.session_state.index=(st.session_state.index+delta)%len(CASES)
    st.session_state.submitted=False
    st.session_state.pattern=PATTERNS[0]
    st.session_state.outlook=OUTLOOK[0]
    st.session_state.nextmove='UP'

st.markdown('### 📈 SONAR TRADING ACADEMY')
st.caption('PATTERN RECOGNITION LAB • Mobile edition')
st.title('Read the chart. Predict the move.')
st.info('Educational **synthetic** charts, not live market data. Every outcome shown is scripted for teaching, not proof of prediction accuracy.')
answered=len(st.session_state.answers)
correct=sum(1 for v in st.session_state.answers.values() if v['pattern'] and v['outlook'] and v['move'])
a,b,c=st.columns(3)
a.metric('Cases',len(CASES));b.metric('Completed',answered);c.metric('All 3 correct',correct)
st.progress(answered/len(CASES))
idx=st.session_state.index
case=CASES[idx]
st.markdown(f'#### Case {idx+1} of {len(CASES)}')
# Do not show the pattern name in advance
st.plotly_chart(graph(case,st.session_state.submitted),use_container_width=True,config={'displayModeBar':False})

if not st.session_state.submitted:
    st.selectbox('1. Identify the chart pattern',PATTERNS,key='pattern')
    st.selectbox('2. What does this pattern suggest?',OUTLOOK,key='outlook')
    st.radio('3. What would you lean toward next?',['UP','DOWN','RANGE / NO TRADE'],key='nextmove',horizontal=True)
    conf=st.slider('Your confidence (not a measured probability)',0,100,50,5)
    if st.button('🔍 Lock answers & reveal next candles',type='primary'):
        mv={'UP':'UP','DOWN':'DOWN','RANGE / NO TRADE':'RANGE'}[st.session_state.nextmove]
        score={'pattern':st.session_state.pattern==case['family'],
               'outlook':st.session_state.outlook==case['direction'], 'move':mv==case['result']}
        st.session_state.answers[idx]=score
        st.session_state.submitted=True
        st.rerun()
else:
    score=st.session_state.answers[idx]
    st.markdown('### What the example shows')
    st.write(f"**Pattern:** {case['family']}")
    st.write(f"**Most defensible interpretation:** {case['direction']}")
    st.write(f"**Illustrative next candles:** {case['result']}")
    st.write(f"**You scored:** {sum(score.values())}/3 on this example")
    st.write('**How to read it:** '+case['why'])
    st.write('**What would invalidate the idea:** '+case['invalid'])
    st.warning('The revealed candles were designed for this lesson. In actual trading, identical-looking setups may rise, fall or stall. A correct chart read is not a guarantee of the next price move.')

x,y=st.columns(2)
with x: st.button('← Previous',on_click=move,args=(-1,))
with y: st.button('Next →',type='primary',on_click=move,args=(1,))

with st.expander('📚 Pattern cheat sheet'):
    for item in CASES:
        st.markdown(f"**{item['family']}** — {item['direction']}. {item['why']}")
with st.expander('ℹ️ How to practice safely'):
    st.write('Identify pattern → describe the conditional setup → set an invalidation level → wait for confirmation → decide whether to trade or skip. Pattern labels are descriptive shortcuts, not independent signals with dependable probabilities. Include spread, fees and Kalshi contract settlement mechanics before considering any real trades.')
