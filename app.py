import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title='Sonar Trading Academy', page_icon='📈', layout='centered', initial_sidebar_state='collapsed')
st.markdown("""<style>
:root{color-scheme:dark}
.stApp,[data-testid="stAppViewContainer"]{background:#09111e!important;color:#f0f6ff!important}
.block-container{max-width:780px;padding:1rem .85rem 5rem}
[data-testid="stHeader"]{background:#09111e!important}
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,[data-testid="stMarkdownContainer"] h4,
[data-testid="stWidgetLabel"] p,[data-testid="stMetricLabel"] p,
[data-testid="stMetricValue"], [data-testid="stCaptionContainer"] p{color:#edf4ff!important}
[data-testid="stMetric"]{background:#16263b;border:1px solid #283e55;border-radius:14px;padding:12px}
[data-testid="stMetricValue"]{font-size:1.7rem!important}
[data-testid="stRadio"] label{background:#18293f;border:1px solid #2b4056;border-radius:10px;padding:.65rem;margin:.25rem 0}
[data-testid="stRadio"] label p{color:#f5f8ff!important}
[data-testid="stSelectbox"] [data-baseweb="select"]>div{background:#18293f;border-color:#43566e;color:#fff}
[data-testid="stSelectbox"] [data-baseweb="select"] span{color:#f6f9ff}
.stButton>button{width:100%;min-height:48px;border-radius:12px;font-weight:700}
.stButton>button[kind="primary"]{background:#13c3a6;color:#06131b;border:0}
[data-testid="stAlert"] p{color:inherit!important}
[data-testid="stTabs"] button p{font-weight:750}
@media(max-width:540px){.block-container{padding:.7rem .7rem 5rem}h1{font-size:1.75rem!important}h2{font-size:1.35rem!important}
[data-testid="stHorizontalBlock"]{gap:.45rem}.stButton>button{min-height:52px}}
</style>""",unsafe_allow_html=True)

# ALL data are deliberately scripted fictional educational candles; not backtest evidence.
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

CASES.extend([
 dict(name='Rising wedge',family='Rising wedge',direction='Potential bearish reversal if support breaks',result='DOWN',seed=41,
      anchors=[(0,93),(5,96),(10,97),(15,100),(20,99),(25,102),(30,101),(35,103),(40,102),(44,103)],
      future=[(45,101),(49,97),(53,94),(56,95)],
      why='Both boundaries rise while the range narrows. The structure may show fading momentum; a break below wedge support is the important confirmation.',invalid='A sustained break above the upper boundary.'),
 dict(name='Falling wedge',family='Falling wedge',direction='Potential bullish reversal if resistance breaks',result='UP',seed=42,
      anchors=[(0,111),(5,107),(10,108),(15,104),(20,105),(25,102),(30,103),(35,100),(40,101),(44,100)],
      future=[(45,102),(49,106),(53,109),(56,108)],
      why='Both boundaries slope down and converge. Sellers may be losing momentum; a confirmed upper-boundary break helps validate a bullish interpretation.',invalid='A decisive move under the lower wedge boundary.'),
 dict(name='Head and shoulders',family='Head and shoulders',direction='Potential bearish reversal if neckline breaks',result='DOWN',seed=43,
      anchors=[(0,96),(6,102),(12,108),(18,101),(24,114),(30,102),(36,108),(40,101),(44,99)],
      future=[(45,98),(49,94),(53,91),(56,92)],
      why='A taller central peak is flanked by two lower peaks. The neckline break is the key confirmation; the shape alone is not a trade signal.',invalid='A sustained recovery above the right shoulder or renewed highs.'),
 dict(name='Inverse head and shoulders',family='Inverse head and shoulders',direction='Potential bullish reversal if neckline breaks',result='UP',seed=44,
      anchors=[(0,110),(6,104),(12,99),(18,106),(24,93),(30,105),(36,99),(40,106),(44,108)],
      future=[(45,109),(49,113),(53,116),(56,114)],
      why='The central trough is deeper than the two surrounding troughs. A confirmed neckline break supports a reversal thesis.',invalid='A sustained fall below the right shoulder or central trough.'),
 dict(name='Symmetrical triangle',family='Symmetrical triangle',direction='Direction uncertain until breakout confirms',result='RANGE',seed=45,
      anchors=[(0,94),(5,108),(10,97),(15,106),(20,99),(25,105),(30,100),(35,104),(40,101),(44,102)],
      future=[(45,103),(49,102),(53,104),(56,101)],
      why='Lower highs and higher lows compress into a tightening range. The direction is not determined by the triangle alone.',invalid='A confirmed directional breakout ends the no-trade thesis.'),
 dict(name='Higher highs and higher lows',family='Uptrend',direction='Bullish trend structure, not a guaranteed entry',result='UP',seed=46,
      anchors=[(0,90),(6,97),(11,94),(17,102),(22,99),(28,106),(33,103),(39,109),(44,107)],
      future=[(45,109),(49,112),(53,110),(56,115)],
      why='Successive swing highs and lows are rising. Trend is bullish, but chasing extended price without a plan can be risky.',invalid='The sequence of higher swing lows is broken.'),
 dict(name='Lower highs and lower lows',family='Downtrend',direction='Bearish trend structure, not a guaranteed entry',result='DOWN',seed=47,
      anchors=[(0,116),(6,109),(11,112),(17,104),(22,108),(28,100),(33,103),(39,96),(44,99)],
      future=[(45,97),(49,94),(53,95),(56,91)],
      why='Successive swing highs and lows are falling. The prevailing structure is bearish, though countertrend rallies can happen.',invalid='Price breaks above a meaningful prior lower swing high.'),
 dict(name='Support retest',family='Support retest',direction='Potential bullish bounce if support holds',result='UP',seed=48,
      anchors=[(0,103),(6,111),(12,105),(18,112),(24,105),(30,109),(36,105),(40,106),(44,105)],
      future=[(45,106),(49,109),(53,113),(56,112)],
      why='Several tests of approximately the same floor suggest support. The level can fail; watch whether buyers defend it on the next test.',invalid='A close below support followed by failed recovery.'),
])

PATTERNS=[x['family'] for x in CASES]
OUTLOOK=list(dict.fromkeys(x['direction'] for x in CASES))
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
    fig.update_layout(height=355,margin=dict(l=0,r=0,t=14,b=5),paper_bgcolor='#111c2b',plot_bgcolor='#111c2b',
                      font_color='#d8e2ed',showlegend=False,dragmode='pan',xaxis_rangeslider_visible=False,
                      xaxis=dict(title='Candles',showgrid=True,gridcolor='#22324a',zeroline=False),
                      yaxis=dict(title='Synthetic price',showgrid=True,gridcolor='#22324a',zeroline=False))
    return fig


if 'answers' not in st.session_state: st.session_state.answers={}
if 'index' not in st.session_state: st.session_state.index=0
if 'revealed' not in st.session_state: st.session_state.revealed={}

def move(delta):
    st.session_state.index=(st.session_state.index+delta)%len(CASES)

def reset():
    st.session_state.answers={}
    st.session_state.revealed={}
    st.session_state.index=0

st.markdown('### 📈 SONAR TRADING ACADEMY')
st.caption('Learn patterns • Predict the move • Reveal the result')
st.title('Learn to read the chart')
st.info('Practice uses **fictional, scripted candlesticks**. Revealed moves are teaching examples—not statistically validated forecasts or real market data.')
learn,quiz,stats=st.tabs(['📚 Learn','🧠 Quiz','🏆 Results'])
with learn:
    st.subheader('Pattern study guide')
    st.write('Study the setup, what it might signal, and what would prove the idea wrong. A pattern is a hypothesis until confirmed.')
    picked=st.selectbox('Choose a pattern to study',PATTERNS,key='study_pattern')
    item=next(x for x in CASES if x['family']==picked)
    st.plotly_chart(graph(item,False),use_container_width=True,config={'displayModeBar':False},key='study_chart')
    st.markdown('**What the pattern suggests**')
    st.write(item['direction'])
    st.markdown('**How to recognize it**')
    st.write(item['why'])
    st.markdown('**What invalidates the idea**')
    st.warning(item['invalid'])
    st.caption('Study charts are synthetic examples. Actual price patterns are often messy and ambiguous.')
    with st.expander('Trading vocabulary'):
        st.markdown('**Support:** a zone where buyers have previously defended price.  \n**Resistance:** a zone where sellers have previously limited advances.  \n**Breakout:** movement beyond a boundary; follow-through matters.  \n**Retest:** price revisits a previously important level.  \n**Invalidation:** the price behavior that weakens or contradicts your thesis.  \n**No trade:** a valid choice when signals conflict or evidence is incomplete.')
with quiz:
    answered=len(st.session_state.answers)
    all_three=sum(1 for score in st.session_state.answers.values() if all(score.values()))
    c1,c2,c3=st.columns(3)
    c1.metric('Cases',len(CASES))
    c2.metric('Completed',answered)
    c3.metric('3/3 correct',all_three)
    st.progress(answered/len(CASES))
    idx=st.session_state.index
    case=CASES[idx]
    revealed=st.session_state.revealed.get(idx,False)
    st.subheader(f'Case {idx+1} of {len(CASES)}')
    st.caption('Read the structure before making a choice. Pattern names are hidden until reveal.')
    st.plotly_chart(graph(case,revealed),use_container_width=True,config={'displayModeBar':False},key=f'quiz_chart_{idx}_{int(revealed)}')
    if not revealed:
        pattern=st.selectbox('1. Which pattern is this?',PATTERNS,index=None,placeholder='Choose a pattern',key=f'pattern_{idx}')
        outlook=st.selectbox('2. What does that pattern suggest?',OUTLOOK,index=None,placeholder='Choose an interpretation',key=f'outlook_{idx}')
        direction=st.radio('3. What would you expect next?',['UP','DOWN','RANGE / NO TRADE'],index=None,key=f'direction_{idx}')
        confidence=st.slider('Your confidence (opinion, not a measured probability)',0,100,50,5,key=f'confidence_{idx}')
        if st.button('🔍 Lock answers & reveal next candles',type='primary',key=f'reveal_{idx}'):
            if pattern is None or outlook is None or direction is None:
                st.warning('Answer all three questions before revealing the chart.')
            else:
                guess={'UP':'UP','DOWN':'DOWN','RANGE / NO TRADE':'RANGE'}[direction]
                st.session_state.answers[idx]={'pattern':pattern==case['family'],'outlook':outlook==case['direction'],'move':guess==case['result']}
                st.session_state.revealed[idx]=True
                st.rerun()
    else:
        score=st.session_state.answers.get(idx,{})
        st.success(f"You scored {sum(score.values())}/3 on this example")
        st.write(f"**Pattern:** {case['family']}")
        st.write(f"**Interpretation:** {case['direction']}")
        st.write(f"**Scripted next move:** {case['result']}")
        st.markdown('**Why this setup matters**')
        st.write(case['why'])
        st.markdown('**What could invalidate it**')
        st.warning(case['invalid'])
        st.caption('This outcome was written into the lesson. It does not demonstrate how often the same setup succeeds in live markets.')
    left,right=st.columns(2)
    with left: st.button('← Previous',on_click=move,args=(-1,),key='prev')
    with right: st.button('Next →',type='primary',on_click=move,args=(1,),key='next')
with stats:
    st.subheader('Your quiz results')
    n=len(st.session_state.answers)
    st.metric('Quizzes completed',f'{n} / {len(CASES)}')
    if n:
        total=sum(sum(s.values()) for s in st.session_state.answers.values())
        st.metric('Question accuracy',f'{total}/{3*n} ({100*total/(3*n):.0f}%)')
        for ix,score in sorted(st.session_state.answers.items()):
            st.write(f"Case {ix+1}: {sum(score.values())}/3 — {CASES[ix]['name']}")
    else:
        st.info('Complete your first quiz to see scores here.')
    st.caption('Progress is stored only in this browser session and may reset when the app restarts.')
    if st.button('Reset all quiz progress'):
        reset()
        st.rerun()
