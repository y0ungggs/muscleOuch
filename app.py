import pandas as pd
import numpy as np
import json
import requests
from urllib import request
import time
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
from collections import Counter
import ast
import os

font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Pretendard-Light.ttf')
# st.write("폰트 경로:", font_path)

file_url = 'https://github.com/y0ungggs/muscleOuch/raw/main/data/%EC%A0%9C1%ED%9A%8C%20%EC%9A%B4%EB%8F%99%EC%9D%B8%EC%A6%9D%ED%9A%8C_%EA%B2%B0%EA%B3%BC(%EB%B3%80%ED%99%98).xlsx'
# 데이터 불러오기 및 전처리
df = pd.read_excel(file_url, engine='openpyxl')
df["날짜"] = pd.to_datetime(df["날짜"])
df["요일"] = df["날짜"].dt.dayofweek.map({0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"})

# -----------------------------------
# 🔹 기본 통계
user_counts = df.groupby("이름")["인증"].sum().reset_index()
mean_count = user_counts["인증"].mean()
std_count = user_counts["인증"].std()
var_count = user_counts["인증"].var()

total_certifications = len(df)
first_date = df["날짜"].min().date()
formatted_first_date = first_date.strftime("%Y-%m-%d")
last_date = df["날짜"].max().date()
formatted_last_date = last_date.strftime("%Y-%m-%d")

# -----------------------------------
# 🏅 타이틀
st.title("🏅 2025년 제1회 운동인증회 결과")

# -----------------------------------
# 📌 개요 정보
with st.expander("📍 기간 및 요약 통계 보기", expanded=True):
    col1, col2, col3 = st.columns(3)
    col1.metric("인증 시작일", formatted_first_date)
    col2.metric("인증 종료일", formatted_last_date)
    col3.metric("전체 인증 횟수", f"{total_certifications:,}회")

    col4, col5, col6 = st.columns(3)
    col4.metric("평균 인증", f"{mean_count:.2f}회")
    col5.metric("표준편차", f"{std_count:.2f}")
    col6.metric("분산", f"{var_count:.2f}")

# -----------------------------------
# 🔽 주요 분석 탭
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 요약 분석", "📅 날짜 기반 분석", "👥 사용자 중심 분석", "📈 심화 통계", "🙆‍♂️ 최종결과"])

# -----------------------------------
# 📊 탭 1: 요약 분석
with tab1:
    st.subheader("1️⃣ 팀별 누적 인증 횟수")
    team_counts = df.groupby("팀")["인증"].sum().reset_index()
    fig1 = px.bar(team_counts, x="팀", y="인증", title="팀별 누적 인증 횟수", labels={"인증": "횟수"})
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("2️⃣ 개인별 누적 인증 횟수")
    df_person = df.groupby(["팀", "이름"])["인증"].sum().reset_index().sort_values(["팀", "인증"], ascending=[True, False])
    fig2 = px.bar(df_person, x="이름", y="인증", color="팀", title="개인별 누적 인증", labels={"이름": "동호회원"})
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📋 개인별 인증 표 보기"):
        st.dataframe(df_person)

    st.subheader("3️⃣ 날짜별 팀별 누적 인증 추이")
    team_daily_counts = df.groupby(["날짜", "팀"])["인증"].sum().reset_index()
    team_daily_counts["누적인증"] = team_daily_counts.groupby("팀")["인증"].cumsum()
    
    fig3 = px.line(
        team_daily_counts,
        x="날짜",
        y="누적인증",
        color="팀",
        title="날짜별 팀별 인증 누적 횟수 추이",
        labels={"날짜": "날짜", "누적인증": "누적 인증 횟수", "팀": "팀"}
    )
    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------------
# 📅 탭 2: 날짜 기반 분석
with tab2:
    st.subheader("4️⃣ 요일별 인증 횟수")
    weekday_order = ["월", "화", "수", "목", "금", "토", "일"]
    weekday_counts = df.groupby("요일")["인증"].sum().reindex(weekday_order).reset_index()
    fig3 = px.bar(weekday_counts, x="요일", y="인증", title="요일별 인증 횟수")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("5️⃣ 월별 인증 추이")
    df["말일"] = df["날짜"].dt.to_period("M").dt.to_timestamp("M")
    monthly = df.groupby(df["말일"].dt.strftime("%-m월"))["인증"].sum().reset_index()
    fig6 = px.line(monthly, x="말일", y="인증", title="월별 인증 추이", markers=True)
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("6️⃣ 팀별 일별 인증")
    selected_team = st.selectbox("팀 선택", df["팀"].unique())
    team_df = df[df["팀"] == selected_team]
    team_daily = team_df.groupby("날짜")["인증"].sum().reset_index()
    fig4 = px.line(team_daily, x="날짜", y="인증", title=f"{selected_team} 팀의 일별 인증")
    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------
# 👥 탭 3: 사용자 중심 분석
with tab3:
    st.subheader("7️⃣ 개인 인증 순위")
    df_person["순위"] = df_person["인증"].rank(method="dense", ascending=False).astype(int)
    df_person = df_person.sort_values("순위")
    st.dataframe(df_person.style.apply(lambda row: ['background-color: #A7D2CB']*len(row) if row["인증"] >= 50 else ['']*len(row), axis=1))
    
    st.subheader("8️⃣ 전체 동호회원 누적 인증")
    df_user_daily = df.groupby(["이름", "날짜"])["인증"].sum().reset_index()
    df_user_daily["누적인증"] = df_user_daily.groupby("이름")["인증"].cumsum()
    fig7_all = px.line(df_user_daily, x="날짜", y="누적인증", color="이름", title="동호회원 누적 인증")
    fig7_all.update_yaxes(dtick=1)
    st.plotly_chart(fig7_all, use_container_width=True)

    st.subheader("9️⃣ 동호회원별 누적 인증 (선택)")
    selected_user = st.selectbox("동호회원 선택", df["이름"].unique())
    user_df = df[df["이름"] == selected_user]
    user_daily = user_df.groupby("날짜")["인증"].sum().cumsum().reset_index(name="누적인증")
    fig5 = px.line(user_daily, x="날짜", y="누적인증", title=f"{selected_user}님의 누적 인증")
    st.plotly_chart(fig5, use_container_width=True)

# -----------------------------------
# 📈 탭 4: 심화 통계
with tab4:
    st.subheader("🔟 인증 횟수 분포")
    fig8 = px.histogram(user_counts, x="인증", nbins=20, marginal="rug", title="인증 횟수 분포")
    fig8.add_vline(x=mean_count, line_dash="dash", line_color="red", annotation_text="평균")
    fig8.add_vline(x=user_counts["인증"].median(), line_dash="dot", line_color="green", annotation_text="중앙값")
    st.plotly_chart(fig8, use_container_width=True)

    st.subheader("1️⃣1️⃣ Z-score 기준 상위 동호회원")
    user_counts["z_score"] = (user_counts["인증"] - mean_count) / std_count
    top_z = user_counts.sort_values("z_score", ascending=False)
    st.dataframe(top_z.head(5)[["이름", "인증", "z_score"]])

    fig_z = px.bar(top_z.head(10), x="이름", y="z_score", color="z_score", color_continuous_scale="blues", title="Z-score 상위 10인")
    st.plotly_chart(fig_z, use_container_width=True)

    st.subheader("1️⃣2️⃣ 연속 인증일 Top 5")
    df_sorted = df.sort_values(["이름", "날짜"])
    df_sorted["이전날짜"] = df_sorted.groupby("이름")["날짜"].shift()
    df_sorted["연속일"] = df_sorted["날짜"] - df_sorted["이전날짜"]
    df_sorted["연속시작"] = df_sorted["연속일"].dt.days.ne(1)
    df_sorted["연속그룹"] = df_sorted.groupby("이름")["연속시작"].cumsum()
    연속_집계 = df_sorted.groupby(["이름", "연속그룹"]).size().reset_index(name="연속일수")
    연속_최대 = 연속_집계.groupby("이름")["연속일수"].max().reset_index().sort_values("연속일수", ascending=False).head(5)
    st.dataframe(연속_최대)

    st.subheader("1️⃣3️⃣ 팀별 Boxplot")
    user_counts = df.groupby(["팀", "이름"])["인증"].count().reset_index()
    fig_box = px.box(user_counts, x="팀", y="인증", points="all", color="팀", title="팀별 인증 분포")
    st.plotly_chart(fig_box, use_container_width=True)

    with st.expander("📋 Raw Data 보기"):
        name_filter = st.text_input("이름으로 필터링", "")
        
        if name_filter.strip():
            filtered_df = df[df["이름"].str.contains(name_filter.strip(), case=False, na=False)]
        else:
            filtered_df = df
            
        show_columns = ["날짜", "팀", "이름", "인증"]
        st.dataframe(filtered_df[show_columns])

# -----------------------------------
# 📈 탭 5: 최종 집계
with tab5:
    st.header("🎉 참여 감사 및 안내 말씀")

    # 0. 많은 참여 감사 인사
    st.info("안녕하세요. 근육통 총무 김영수 입니다!!  \n처음으로 팀전으로 진행항 운동 인증회에 참여해주신 모든 동호회원분들께 진심으로 감사드립니다!  \n동호회원분들의 꾸준한 참여가 큰 힘이 됩니다.")

    # 1. 3회 이상 인증한 사람의 수 및 안내
    certified_3plus = df.groupby("이름")["인증"].sum()
    certified_3plus_count = (certified_3plus >= 3).sum()
    st.subheader("1️⃣ 3회 이상 인증한 회원 수")
    st.write(f"총 {certified_3plus_count}명의 회원이 3회 이상 인증을 완료하셨습니다.")
    st.info("해당 인원분들께는 곧 치킨 기프티콘이 지급될 예정입니다! 그동안 열심히 운동하셨으니 즐기세요 🍗")

    # 2. 가장 많이 인증한 팀과 팀원 안내
    team_sum = df.groupby("팀")["인증"].sum().reset_index()
    top_team = team_sum.sort_values("인증", ascending=False).iloc[0]
    top_team_name = top_team["팀"]
    top_team_cert_sum = top_team["인증"]

    st.subheader("2️⃣ 가장 많이 인증한 팀 및 팀원 안내")
    st.write(f"🏆 가장 많이 인증한 팀은 **{top_team_name}**이며, 총 인증 횟수는 **{top_team_cert_sum}회** 입니다. 축하드립니다🎉🎉🎉🎉")

    # 해당 팀 소속 팀원 및 인증 횟수
    top_team_members = df[df["팀"] == top_team_name].groupby("이름")["인증"].sum().reset_index().sort_values("인증", ascending=False)
    st.write(f"**{top_team_name}** 소속 팀원 및 인증 횟수:")
    st.dataframe(top_team_members.rename(columns={"이름": "팀원 이름", "인증": "인증 횟수"}))

    st.info(
        "※ 해당 팀원분들께는 6월 13일까지 15만원 상당의 신발 구매 지원금을 드리오니, 신발을 고른 후 이메일 또는 사내 메신저로 개별 연락 바랍니다.(DT사업팀 김영수 주임)😄  \n"
        "※ 단, '박채은'회원님은 블랙리스트에 올랐으므로 5만원 상당의 운동용품 구매 지원금을 지급합니다.🤭"
    )

    # 3. 50회 이상 인증 회원 및 사다리타기 안내
    certified_50plus = certified_3plus[certified_3plus >= 50].reset_index().rename(columns={"이름": "회원명", "인증": "인증 횟수"})
    st.subheader("3️⃣ 50회 이상 인증한 회원 명단")
    if len(certified_50plus) > 0:
        st.dataframe(certified_50plus)
        st.info(
            "50회 이상 인증한 회원 중  \n이번에 우승한 7팀, 기존 블랙리스트 인원을 제외한 회원만 사다리타기를 통해  \n단 1명에게 15만원 상당의 신발 구매 지원금을 드리오니,  \n"
            "신발을 고른 후 이메일 또는 사내 메신저로 개별 연락 바랍니다.😄"
        )
        st.info(
            "대상자: 고한솔, 박운학, 윤균성, 장명기, 장서혁, 장선우, 장창수  \n"   
            "축하드립니다!!"
        )
    else:
        st.write("50회 이상 인증한 회원이 없습니다.")

    # 4. 하반기 이벤트 참여 독려
    st.subheader("4️⃣ 투 비 컨티뉴")
    st.info(
        "부족한 점을 보완하여 하반기 이벤트를 준비하겠습니다.  \n"
        "다음에도 많은 관심과 참여 부탁드립니다!  \n"
        "더욱 다양한 이벤트와 풍성한 상품으로 찾아뵙겠습니다. 건강하세요🙇‍♀️"
    )


