import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title='CAMPUS BITE v3',page_icon='🍱',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
.stApp{background:linear-gradient(145deg,#091225,#142342 70%,#111c33);color:#edf3ff}
.block-container{max-width:1200px;padding-top:1.1rem;padding-bottom:3rem}
h1,h2,h3,p,label{color:#eef3ff!important} [data-testid="stMetric"]{background:#1b2c4b;border:1px solid #385174;border-radius:15px;padding:13px}
[data-testid="stMetricLabel"]{color:#b8c8e4!important}[data-testid="stMetricValue"]{color:#fff!important}
div.stButton>button[kind="primary"]{background:#f8b54a;color:#13213c;border:0;font-weight:800}
div.stButton>button{border-radius:12px;min-height:43px;font-weight:650}
[data-testid="stVerticalBlockBorderWrapper"]{background:rgba(29,47,78,.85);border:1px solid #3d5579;border-radius:16px}
/* Explicit text contrast for Streamlit widgets and alerts */
.stApp div.stButton > button, .stApp div.stButton > button * {color:#14213d!important;}
.stApp div.stButton > button[kind="primary"] {background:#f8b54a!important;color:#14213d!important;}
.stApp div.stButton > button:disabled, .stApp div.stButton > button:disabled * {color:#657185!important;}
.stApp [data-testid="stAlert"] {background:#eaf3ff!important;border:1px solid #8fb9ef!important;}
.stApp [data-testid="stAlert"] *, .stApp [data-testid="stAlert"] p {color:#14213d!important;}
.stApp [data-baseweb="select"] *, .stApp [data-baseweb="input"] input {color:#14213d!important;}
.stApp [data-baseweb="popover"] *, [role="listbox"] * {color:#14213d!important;}
.stApp [data-testid="stMetric"] *, .stApp [data-testid="stMetric"] p {color:#eef3ff!important;}
[data-testid="stDataFrame"]{border-radius:12px} .hero{padding:24px;border-radius:20px;background:linear-gradient(110deg,#223e72,#1b2847);border:1px solid #5373a2}
.kicker{color:#ffcc76;font-weight:750;letter-spacing:.1em;font-size:12px}.sub{color:#b8c8e4!important}
</style>''',unsafe_allow_html=True)

ROUNDS=['브랜드 론칭','고객 검증','성장 투자','경쟁 위기','사업 확장']
SEGMENTS=['기숙사생','바쁜 통학생','건강 관심층']
PRODUCTS=['가성비','편의성','건강·프리미엄']
MODELS=['직접 판매','정기 구독','단체 계약']
CHANNELS=['교내 픽업','배달','제휴 매장 수령']
FIT={'기숙사생':[1.18,1.05,.89],'바쁜 통학생':[.96,1.21,.96],'건강 관심층':[.84,1.02,1.26]}
UNIT_COST={'가성비':2700,'편의성':3200,'건강·프리미엄':4000}
FEE={'교내 픽업':0,'배달':900,'제휴 매장 수령':350}
RESEARCH={
'기숙사생':['식비 부담이 크고 반복 구매 의향이 높음','주 2~3회 식사 대체 수요가 있음','가격 민감도가 높아 할인에 반응'],
'바쁜 통학생':['식사 시간이 부족해 편의성을 중시','배달과 빠른 수령을 선호','기다리는 시간이 길면 재구매가 줄어듦'],
'건강 관심층':['원재료와 영양 정보를 확인','품질이 좋다면 높은 가격도 고려','메뉴 다양성과 신뢰가 재구매에 중요']}
EVENTS=[
('🎪 개강 행사 주문','학생회가 80식 단체 주문을 제안했습니다. 단가는 기존 판매가보다 15% 낮습니다.', ['행사 주문 수락','정가 판매 유지','행사 공동 홍보 제안']),
('💬 고객 피드백','고객들이 메뉴 구성과 수령 경험에 대한 개선을 요구합니다.', ['맛·품질 개선','픽업 동선 개선','가격 할인 쿠폰']),
('📣 캠퍼스 인플루언서','학내 크리에이터가 협업을 제안했습니다. 성과는 고객 적합성에 따라 달라집니다.', ['협업 진행','동아리 제휴 추진','기존 고객 추천 이벤트']),
('⚡ 경쟁사 진입','경쟁사가 저가 도시락을 출시했습니다. 일부 고객이 가격을 비교하기 시작했습니다.', ['가격 인하 대응','품질 차별화','구독 혜택 강화']),
('🚀 새로운 판매 기회','학교 근처 기업과 동아리에서 정기 납품을 문의했습니다.', ['단체 계약 확대','정기 구독 강화','기존 고객 집중'])]
EVENT_COST=[{'행사 주문 수락':0,'정가 판매 유지':0,'행사 공동 홍보 제안':80000},
{'맛·품질 개선':180000,'픽업 동선 개선':100000,'가격 할인 쿠폰':120000},
{'협업 진행':210000,'동아리 제휴 추진':140000,'기존 고객 추천 이벤트':100000},
{'가격 인하 대응':0,'품질 차별화':200000,'구독 혜택 강화':150000},
{'단체 계약 확대':230000,'정기 구독 강화':180000,'기존 고객 집중':90000}]

def money(v):return f'{v:,.0f}원'
def clamp(v,lo,hi):return max(lo,min(hi,v))
def fresh():
 return {'round':0,'phase':'research','cash':5000000.,'satisfaction':60.,'awareness':20.,'loyalty':50.,'active':0,'subscribers':0,'history':[],'research':[],'strategy':{'segment':'기숙사생','product':'가성비','model':'직접 판매','channel':'교내 픽업','price':6500},'pending':{},'event_choice':None,'failed':False,'finished':False,'nickname':''}
if 'cb3' not in st.session_state:st.session_state.cb3=fresh()
g=st.session_state.cb3

def move(phase):g['phase']=phase;st.rerun()
def spendable():return max(0,int(g['cash']-300000))
def simulate():
 r=g['round']; p=g['pending']; s=g['strategy']; ev=g['event_choice'];
 budget=p['ads']+p['product_budget']+p['retention_budget']+p['partnership_budget']
 cost_event=EVENT_COST[r][ev]; research_cost=p.get('research_cost',0)
 fit=FIT[s['segment']][PRODUCTS.index(s['product'])]
 price=s['price']; unit=UNIT_COST[s['product']]+FEE[s['channel']]
 if s['model']=='정기 구독':unit_price=price*.92
 elif s['model']=='단체 계약':unit_price=price*.88
 else:unit_price=price
 demand=230*fit*(6500/price)**1.28
 demand*=1+min(p['ads']/400000,.8)*.38+min(g['awareness']/100,.9)*.35
 demand*=.8+g['satisfaction']/300
 if s['model']=='정기 구독':demand=demand*.90+g['subscribers']*.46
 elif s['model']=='단체 계약':demand=demand*.83+65+min(p['partnership_budget']/400000,.8)*100
 if s['channel']=='배달':demand*=1.12
 if s['channel']=='제휴 매장 수령':demand*=1.06
 if r==3:demand*=.79
 event_multiplier=1.0; extra=0; satisfaction_change=0; loyalty_change=0; awareness_change=0
 if r==0:
  if ev=='행사 주문 수락':extra=80; satisfaction_change+=1
  if ev=='행사 공동 홍보 제안':extra=35;awareness_change+=9
 if r==1:
  if ev=='맛·품질 개선':satisfaction_change+=9;loyalty_change+=5
  if ev=='픽업 동선 개선':satisfaction_change+=6;event_multiplier*=1.06
  if ev=='가격 할인 쿠폰':event_multiplier*=1.17;loyalty_change+=2
 if r==2:
  if ev=='협업 진행':event_multiplier*=1.17;awareness_change+=12
  if ev=='동아리 제휴 추진':extra+=55;loyalty_change+=2
  if ev=='기존 고객 추천 이벤트':event_multiplier*=1.13;loyalty_change+=7
 if r==3:
  if ev=='가격 인하 대응':event_multiplier*=1.19;unit_price*=.92
  if ev=='품질 차별화':event_multiplier*=1.07;satisfaction_change+=8
  if ev=='구독 혜택 강화':loyalty_change+=10;event_multiplier*=1.05
 if r==4:
  if ev=='단체 계약 확대':extra+=95
  if ev=='정기 구독 강화':loyalty_change+=9;event_multiplier*=1.10
  if ev=='기존 고객 집중':satisfaction_change+=7;loyalty_change+=8
 demand=demand*event_multiplier+extra
 demand*=1+min(p['product_budget']/400000,.8)*.13+min(p['partnership_budget']/400000,.8)*.12
 demand*=1+min(p['retention_budget']/400000,.8)*.07
 demand=round(demand)
 capacity=p['capacity']; max_affordable=max(0,int((g['cash']-300000-budget-cost_event-research_cost)//unit))
 sales=min(demand,capacity,max_affordable)
 revenue=sales*unit_price; variable=sales*unit; fixed=300000
 change=revenue-variable-fixed-budget-cost_event-research_cost
 g['cash']+=change
 satisfaction_change+=min(p['product_budget']/60000,9)-max(0,(price-7000)/900)
 if sales<demand*.8:satisfaction_change-=7
 g['satisfaction']=clamp(g['satisfaction']+satisfaction_change,10,100)
 g['loyalty']=clamp(g['loyalty']+loyalty_change+min(p['retention_budget']/60000,8)-2,5,100)
 g['awareness']=clamp(g['awareness']+awareness_change+min(p['ads']/25000,15)+min(p['partnership_budget']/45000,8)-3,0,100)
 g['active']=sales
 if s['model']=='정기 구독':g['subscribers']=round(g['subscribers']*(g['loyalty']/100)*.65+sales*.38)
 else:g['subscribers']=round(g['subscribers']*.65)
 g['failed']=g['cash']<300000
 reason=[]
 reason.append(f"목표 고객과 제품의 적합도: {fit:.2f}배")
 reason.append(f"예상 주문 {demand:,}식 중 {sales:,}식 판매"+(" (생산능력·현금 제약 발생)" if sales<demand else ""))
 reason.append(f"판매 단가 {unit_price:,.0f}원 · 식당 원가/수수료 {unit:,.0f}원")
 if r==3:reason.append('경쟁사 등장으로 기본 수요가 감소했습니다.')
 if p['ads']>0:reason.append('광고비는 신규 고객 인지도를 높이지만 당월 현금을 소모합니다.')
 if p['retention_budget']>0:reason.append('고객 관리 투자는 다음 라운드 충성도에 반영됩니다.')
 row={'라운드':r+1,'단계':ROUNDS[r],'수익모델':s['model'],'판매량':sales,'예상주문':demand,'매출':round(revenue),'원가':round(variable),'투자비':budget+cost_event+research_cost,'고정비':fixed,'현금증감':round(change),'현금잔액':round(g['cash']),'만족도':round(g['satisfaction'],1),'인지도':round(g['awareness'],1),'충성도':round(g['loyalty'],1),'고객수':sales,'설명':reason,'이벤트':ev}
 g['history'].append(row)
 g['phase']='result'

def score():
 h=g['history'];cash=g['cash'];last=h[-1] if h else {}
 financial=40*clamp((cash-3000000)/4000000,0,1)
 customers=15*clamp(g['active']/500,0,1)+10*g['loyalty']/100
 sat=20*g['satisfaction']/100
 sustainable=(8 if last.get('현금증감',0)>0 else 0)+(7 if cash>600000 else 0)
 total=financial+customers+sat+sustainable
 if g['failed']:total=min(total,30)
 return [round(x,2) for x in (total,financial,customers,sat,sustainable)]

with st.container():
 st.markdown('<div class="hero"><div class="kicker">ENACTUS · BUSINESS SIMULATION</div><h1>🍱 CAMPUS BITE <span style="color:#ffc66d">v3</span></h1><p class="sub">5단계 스타트업 CEO 게임 · 고객 조사 → 전략 → 돌발 상황 → 성과 분석</p></div>',unsafe_allow_html=True)
st.write('')
left,right=st.columns([4,1])
with left:
 st.caption("최종 결과" if g["finished"] else f"STAGE {g['round']+1} / 5 · {ROUNDS[g['round']]}")
 if not g['finished']:st.progress((g['round']+{'research':.05,'plan':.28,'event':.62,'result':.88}[g['phase']])/5)
with right:
 if st.button('↻ 새 게임',use_container_width=True):st.session_state.cb3=fresh();st.rerun()
a,b,c,d=st.columns(4)
a.metric('💰 보유 현금',money(g['cash']))
b.metric('👥 최근 고객',f"{g['active']:,}명")
c.metric('⭐ 만족도',f"{g['satisfaction']:.1f}/100")
d.metric('📣 브랜드 인지도',f"{g['awareness']:.1f}/100")
st.write('')
if g['finished']:
 total,fin,cust,sat,sust=score()
 st.success('🏁 CEO 시뮬레이션 종료')
 st.title(f'최종 성적: {total:.2f} / 100점')
 m1,m2,m3,m4=st.columns(4)
 for col,label,val in zip([m1,m2,m3,m4],['재무 성과 /40','고객 성과 /25','고객 만족 /20','지속 가능성 /15'],[fin,cust,sat,sust]):col.metric(label,f'{val:.2f}')
 if g['failed']:st.error('운영자금 부족으로 사업을 지속하지 못했습니다. 최종 점수에 제한이 적용되었습니다.')
 if g['history']:
  df=pd.DataFrame(g['history']);st.subheader('📊 5단계 경영 성과')
  tab1,tab2,tab3=st.tabs(['현금 흐름','고객 및 매출','상세 실적'])
  with tab1:st.line_chart(df.set_index('단계')[['현금잔액']]);st.bar_chart(df.set_index('단계')[['현금증감']])
  with tab2:st.line_chart(df.set_index('단계')[['고객수','예상주문']]);st.bar_chart(df.set_index('단계')[['매출']])
  with tab3:st.dataframe(df.drop(columns=['설명']),use_container_width=True,hide_index=True)
  st.subheader('🧭 전략 회고')
  for row in g['history']:
   with st.expander(f"{row['라운드']}단계 · {row['단계']} — {row['현금증감']:+,}원"):
    for reason in row['설명']:st.write('• '+reason)
 st.info('모든 시장 수요와 점수는 교육용 가상 규칙입니다. 실제 사업의 성공 확률이나 수익을 예측하지 않습니다.')
 st.stop()

r=g['round']; phase=g['phase']
with st.container(border=True):
 st.subheader(f"{'🔎 시장 조사' if phase=='research' else '🧠 경영 전략 수립' if phase=='plan' else '⚡ 돌발 상황' if phase=='event' else '📋 경영 보고서'} · {ROUNDS[r]}")
 if phase=='research':
  st.write('결정하기 전에 시장 정보를 살펴보세요. 무료 브리핑은 모두에게 제공되지만, 추가 조사에는 비용이 듭니다.')
  st.info(['📌 개강 시즌입니다. 학내 간편식 수요가 증가하고 있습니다.','📌 첫 고객 피드백이 도착했습니다. 재구매를 좌우하는 요인을 찾아보세요.','📌 경쟁사와 마케팅 채널의 효과를 비교할 시점입니다.','📌 저가 경쟁사가 등장했습니다. 가격만으로 대응할지 고민하세요.','📌 성장 이후 안정적인 매출원을 확보할 기회입니다.'][r])
  segment=st.selectbox('조사할 고객 집단',SEGMENTS,index=SEGMENTS.index(g['strategy']['segment']),key=f'research_seg_{r}')
  st.markdown('**고객 인터뷰 요약**')
  for item in RESEARCH[segment]:st.write('• '+item)
  st.markdown('**추가 유료 조사**')
  research=st.radio('선택', ['추가 조사 없음 (0원)','경쟁사 가격 조사 (40,000원)','고객 심층 인터뷰 (70,000원)'],key=f'research_{r}')
  if st.button('조사 완료 · 전략 수립으로',type='primary'):
   g['pending']['research_cost']={'추가 조사 없음 (0원)':0,'경쟁사 가격 조사 (40,000원)':40000,'고객 심층 인터뷰 (70,000원)':70000}[research]
   g['pending']['research_type']=research
   move('plan')
 if phase=='plan':
  st.caption('모든 지출은 보유 현금 안에서 이루어집니다. 투자한 만큼 반드시 성공하는 것은 아닙니다.')
  if g['pending'].get('research_type')=='경쟁사 가격 조사 (40,000원)':st.info('📑 경쟁사 가격 조사: 교내 간편식은 4,900~7,900원대의 경쟁이 치열하다는 가상 조사 결과입니다.')
  if g['pending'].get('research_type')=='고객 심층 인터뷰 (70,000원)':st.info('📑 고객 인터뷰: 목표 고객과 제품 포지셔닝이 맞을수록 구매 전환이 높다는 가상 조사 결과입니다.')
  col1,col2=st.columns(2)
  with col1:
   segment=st.selectbox('🎯 목표 고객',SEGMENTS,index=SEGMENTS.index(g['strategy']['segment']),key=f'seg_{r}')
   product=st.selectbox('🍽️ 제품 콘셉트',PRODUCTS,index=PRODUCTS.index(g['strategy']['product']),key=f'prod_{r}')
   model=st.selectbox('🧾 수익모델',MODELS,index=MODELS.index(g['strategy']['model']),key=f'model_{r}')
  with col2:
   channel=st.selectbox('📦 판매 채널',CHANNELS,index=CHANNELS.index(g['strategy']['channel']),key=f'channel_{r}')
   price=st.slider('🏷️ 1식 가격',4500,9500,g['strategy']['price'],500,key=f'price_{r}')
   capacity=st.slider('🏭 월 생산 가능량',100,850,450,50,key=f'capacity_{r}')
  st.divider();st.markdown('#### 💼 투자 예산 배분')
  st.caption('투자는 한 번에 지출되며, 현금 30만 원은 월 고정비로 확보해야 합니다. 돌발 상황 대응 비용도 추가로 발생할 수 있습니다.')
  x,y=st.columns(2)
  with x:
   ads=st.slider('📣 광고 / 홍보',0,400000,100000,25000,key=f'ads_{r}')
   prod=st.slider('🧑‍🍳 제품 개선',0,400000,100000,25000,key=f'prod_budget_{r}')
  with y:
   retention=st.slider('💗 고객 유지',0,400000,50000,25000,key=f'retention_{r}')
   partnership=st.slider('🤝 제휴 / 영업',0,400000,50000,25000,key=f'partner_{r}')
  total=ads+prod+retention+partnership+g['pending'].get('research_cost',0)
  reserve=300000+math.ceil(capacity*(UNIT_COST[product]+FEE[channel]))
  st.metric('이번 단계 투자 계획',money(total))
  st.caption(f'투자 후 현금: {money(g["cash"]-total)} · 최대 생산량 전체 조달 시 필요한 원가+고정비: {money(reserve)} (실제 생산량은 수요에 맞춰 결정)')
  if total>spendable():st.error('투자금이 너무 큽니다. 월 고정비 30만 원을 남겨주세요.')
  elif g['cash']-total-reserve<0:st.warning('생산능력 전체를 가동할 자금은 부족할 수 있습니다. 실제 판매량이 제한될 수 있습니다.')
  if st.button('전략 확정 → 돌발 상황 확인',type='primary',disabled=total>spendable()):
   g['strategy']={'segment':segment,'product':product,'model':model,'channel':channel,'price':price}
   g['pending'].update({'ads':ads,'product_budget':prod,'retention_budget':retention,'partnership_budget':partnership,'capacity':capacity})
   move('event')
 if phase=='event':
  title,description,options=EVENTS[r]
  st.markdown(f'### {title}')
  st.write(description)
  ev=st.radio('CEO의 선택',options,key=f'event_{r}')
  st.caption(f'선택 비용: {money(EVENT_COST[r][ev])} · 현재 투자 계획: {money(sum(g["pending"].get(k,0) for k in ["ads","product_budget","retention_budget","partnership_budget","research_cost"]))}')
  if st.button('이 결정으로 경영 결과 확인',type='primary'):
   g['event_choice']=ev
   simulate();st.rerun()
 if phase=='result':
  row=g['history'][-1]
  x,y,z=st.columns(3)
  x.metric('이번 달 판매량',f"{row['판매량']:,}식")
  y.metric('이번 달 매출',money(row['매출']))
  z.metric('현금 증감',money(row['현금증감']))
  st.markdown('#### 📌 이번 결정의 결과')
  for reason in row['설명']:st.write('• '+reason)
  st.markdown('#### 📈 누적 실적')
  df=pd.DataFrame(g['history']);st.line_chart(df.set_index('단계')[['현금잔액']])
  if g['failed']:st.warning('운영자금이 부족합니다. 남은 라운드는 진행할 수 있지만 최종 점수는 제한됩니다.')
  if st.button('다음 단계로 →' if r<4 else '최종 성적표 확인 🏁',type='primary'):
   if r==4:g['finished']=True
   else:g['round']+=1;g['phase']='research';g['pending']={};g['event_choice']=None
   st.rerun()

with st.expander('ℹ️ 게임 규칙과 점수 계산'):
 st.write('초기 현금 500만 원. 5단계에서 시장 조사, 전략 설계, 상황 대응을 반복합니다. 가격, 목표 고객, 제품, 수익모델, 채널, 투자에 따라 가상 수요와 비용이 변합니다.')
 st.write('최종 점수 = 재무 성과 40점 + 고객 성과 25점 + 고객 만족 20점 + 지속 가능성 15점. 운영자금 부족 시 총점 최대 30점.')
 st.write('동일한 의사결정은 동일한 결과를 낳습니다. 무작위 추첨이나 숨겨진 난수는 없습니다. 점수 산식과 시장 조건은 교육용 가정입니다.')
