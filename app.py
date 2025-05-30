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
last_date = df["날짜"].max().date()

# -----------------------------------
# 🏅 타이틀
st.title("🏅 2025년 제1회 운동인증회 결과")

# -----------------------------------
# 📌 개요 정보
with st.expander("📍 기간 및 요약 통계 보기", expanded=True):
    col1, col2, col3 = st.columns(3)
    col1.metric("인증 시작일", first_date)
    col2.metric("인증 종료일", last_date)
    col3.metric("전체 인증 횟수", f"{total_certifications:,}회")

    col4, col5, col6 = st.columns(3)
    col4.metric("평균 인증", f"{mean_count:.2f}회")
    col5.metric("표준편차", f"{std_count:.2f}")
    col6.metric("분산", f"{var_count:.2f}")

# -----------------------------------
# 🔽 주요 분석 탭
tab1, tab2, tab3, tab4 = st.tabs(["📊 요약 분석", "📅 날짜 기반 분석", "👥 사용자 중심 분석", "📈 심화 통계"])

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

# -----------------------------------
# 📅 탭 2: 날짜 기반 분석
with tab2:
    st.subheader("3️⃣ 요일별 인증 횟수")
    weekday_order = ["월", "화", "수", "목", "금", "토", "일"]
    weekday_counts = df.groupby("요일")["인증"].sum().reindex(weekday_order).reset_index()
    fig3 = px.bar(weekday_counts, x="요일", y="인증", title="요일별 인증 횟수")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("4️⃣ 월별 인증 추이")
    df["말일"] = df["날짜"].dt.to_period("M").dt.to_timestamp("M")
    monthly = df.groupby(df["말일"].dt.strftime("%-m월"))["인증"].sum().reset_index()
    fig6 = px.line(monthly, x="말일", y="인증", title="월별 인증 추이", markers=True)
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("5️⃣ 팀별 일별 인증")
    selected_team = st.selectbox("팀 선택", df["팀"].unique())
    team_df = df[df["팀"] == selected_team]
    team_daily = team_df.groupby("날짜")["인증"].sum().reset_index()
    fig4 = px.line(team_daily, x="날짜", y="인증", title=f"{selected_team} 팀의 일별 인증")
    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------
# 👥 탭 3: 사용자 중심 분석
with tab3:
    st.subheader("6️⃣ 전체 동호회원 누적 인증")
    df_user_daily = df.groupby(["이름", "날짜"])["인증"].sum().reset_index()
    df_user_daily["누적인증"] = df_user_daily.groupby("이름")["인증"].cumsum()
    fig7_all = px.line(df_user_daily, x="날짜", y="누적인증", color="이름", title="동호회원 누적 인증")
    fig7_all.update_yaxes(dtick=1)
    st.plotly_chart(fig7_all, use_container_width=True)

    st.subheader("7️⃣ 동호회원별 누적 인증 (선택)")
    selected_user = st.selectbox("동호회원 선택", df["이름"].unique())
    user_df = df[df["이름"] == selected_user]
    user_daily = user_df.groupby("날짜")["인증"].sum().cumsum().reset_index(name="누적인증")
    fig5 = px.line(user_daily, x="날짜", y="누적인증", title=f"{selected_user}님의 누적 인증")
    st.plotly_chart(fig5, use_container_width=True)

# -----------------------------------
# 📈 탭 4: 심화 통계
with tab4:
    st.subheader("8️⃣ 개인 인증 순위")
    df_person["순위"] = df_person["인증"].rank(method="dense", ascending=False).astype(int)
    df_person = df_person.sort_values("순위")
    st.dataframe(df_person.style.apply(lambda row: ['background-color: #A7D2CB']*len(row) if row["인증"] >= 50 else ['']*len(row), axis=1))

    st.subheader("9️⃣ 인증 횟수 분포")
    fig8 = px.histogram(user_counts, x="인증", nbins=20, marginal="rug", title="인증 횟수 분포")
    fig8.add_vline(x=mean_count, line_dash="dash", line_color="red", annotation_text="평균")
    fig8.add_vline(x=user_counts["인증"].median(), line_dash="dot", line_color="green", annotation_text="중앙값")
    st.plotly_chart(fig8, use_container_width=True)

    st.subheader("🔟 Z-score 기준 상위 동호회원")
    user_counts["z_score"] = (user_counts["인증"] - mean_count) / std_count
    top_z = user_counts.sort_values("z_score", ascending=False)
    st.dataframe(top_z.head(5)[["이름", "인증", "z_score"]])

    fig_z = px.bar(top_z.head(10), x="이름", y="z_score", color="z_score", color_continuous_scale="blues", title="Z-score 상위 10인")
    st.plotly_chart(fig_z, use_container_width=True)

    st.subheader("1️⃣1️⃣ 연속 인증일 Top 5")
    df_sorted = df.sort_values(["이름", "날짜"])
    df_sorted["이전날짜"] = df_sorted.groupby("이름")["날짜"].shift()
    df_sorted["연속일"] = df_sorted["날짜"] - df_sorted["이전날짜"]
    df_sorted["연속시작"] = df_sorted["연속일"].dt.days.ne(1)
    df_sorted["연속그룹"] = df_sorted.groupby("이름")["연속시작"].cumsum()
    연속_집계 = df_sorted.groupby(["이름", "연속그룹"]).size().reset_index(name="연속일수")
    연속_최대 = 연속_집계.groupby("이름")["연속일수"].max().reset_index().sort_values("연속일수", ascending=False).head(5)
    st.dataframe(연속_최대)

    st.subheader("1️⃣2️⃣ 팀별 Boxplot")
    fig_box = px.box(user_counts, x="팀", y="인증", points="all", color="팀", title="팀별 인증 분포")
    st.plotly_chart(fig_box, use_container_width=True)
