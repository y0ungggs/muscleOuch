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
df = pd.read_excel(file_url, engine='openpyxl')


st.title("🏅 2025년 제1회 운동인증회 분석")

# --- 데이터 전처리 예시 ---
# 날짜 컬럼 datetime 변환
df["날짜"] = pd.to_datetime(df["날짜"])
df["요일"] = df["날짜"].dt.dayofweek.map(
    {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}
)

# 팀명과 이름 컬럼은 상황에 맞게 이름 바꾸기
# 예: df.rename(columns={"팀명_컬럼명": "팀명", "이름_컬럼명": "이름"}, inplace=True)

total_certifications = len(df)
first_date = df["작성일"].min().date()
last_date = df["작성일"].max().date()
st.markdown(f"**2025년 제1회 운동 인증회 전체 인증 횟수: {first_date} ~ {last_date} : {total_certifications:,}회**")


# --------------------------------------------------
# 1. 팀별 누적 인증 횟수 그래프
st.subheader("1. 팀별 누적 인증 횟수")
team_counts = df.groupby("팀")["인증"].sum().reset_index()
fig1 = px.bar(team_counts, x="팀", y="인증", title="팀별 누적 인증 횟수", labels={"인증": "횟수"})
st.plotly_chart(fig1)

# --------------------------------------------------
# 2. 개인별 누적 인증 횟수 그래프 (팀명 순서대로)
st.subheader("2. 개인별 누적 인증 횟수")
df_person = df.groupby(["팀", "이름"])["인증"].sum().reset_index()
df_person = df_person.sort_values(["팀", "인증"], ascending=[True, False])
fig2 = px.bar(df_person, x="이름", y="인증", color="팀",
              title="개인별 누적 인증 횟수", 
              labels={"이름": "사용자", "인증": "누적 인증 횟수"})
st.plotly_chart(fig2)

# --------------------------------------------------
# 3. 개인별 누적 인증 횟수 표 (팀명 순서대로)
st.subheader("3. 개인별 누적 인증 횟수 표")
st.dataframe(df_person)

# --------------------------------------------------
# 4. 개인별 인증 순위
st.subheader("4. 개인별 인증 순위")
df_person["순위"] = df_person["인증"].rank(method="dense", ascending=False).astype(int)
df_person = df_person.sort_values("순위")

def highlight_top_50(row):
    if row["인증"] >= 50:
        return ['background-color: #fff9c4']*len(row)
    else:
        return ['']*len(row)

st.dataframe(df_person.style.apply(highlight_top_50, axis=1))

# --------------------------------------------------
# 5. 요일별 인증 횟수
st.subheader("5. 요일별 인증 횟수")
weekday_order = ["월", "화", "수", "목", "금", "토", "일"]
weekday_counts = df.groupby("요일")["인증"].sum().reindex(weekday_order).reset_index()
fig3 = px.bar(weekday_counts, x="요일", y="인증", title="요일별 인증 횟수")
st.plotly_chart(fig3)

# --------------------------------------------------
# 6. 팀별 활동 내역 (팀명 필터링)
st.subheader("6. 팀별 인증 내역")
teams = df["팀"].unique()
selected_team = st.selectbox("팀 선택", teams)
team_df = df[df["팀"] == selected_team]
team_daily = team_df.groupby("날짜")["인증"].sum().reset_index()
fig4 = px.line(team_daily, x="날짜", y="인증", title=f"{selected_team} 팀의 일별 인증 횟수")
st.plotly_chart(fig4)

# --------------------------------------------------
# 7. 사용자별 활동 내역 (이름 필터링)
st.subheader("7. 사용자별 인증 내역")
users = df["이름"].unique()
selected_user = st.selectbox("사용자 선택", users)
user_df = df[df["이름"] == selected_user]
user_daily = user_df.groupby("날짜")["인증"].sum().cumsum().reset_index(name="누적인증")
fig5 = px.line(user_daily, x="날짜", y="누적인증", title=f"{selected_user}님의 누적 인증 그래프")
fig5.update_yaxes(tickformat="d")
st.plotly_chart(fig5)

# --------------------------------------------------
# 8. 워드클라우드 (예: 인증내용이 담긴 '내용' 컬럼이 있다고 가정)
# st.subheader("8. 워드클라우드")
# if "내용" in df.columns:
#     text = " ".join(df["내용"].dropna().astype(str))
#     wordcloud = WordCloud(font_path="fonts/Pretendard-Light.ttf", background_color="white", width=800, height=400).generate(text)
#     plt.figure(figsize=(10,5))
#     plt.imshow(wordcloud, interpolation='bilinear')
#     plt.axis("off")
#     st.pyplot(plt)
# else:
#     st.write("워드클라우드용 텍스트 데이터가 없습니다.")

# --------------------------------------------------
# 9. 추가 분석 제안: 월별 인증 추이
st.subheader("9. 월별 인증 추이")
df["말일"] = df["날짜"].dt.to_period("M").dt.to_timestamp("M")
monthly = df.groupby(df["말일"].dt.strftime("%-m월"))["인증"].sum().reset_index()
fig6 = px.line(monthly, x="말일", y="인증", title="월별 인증 추이", markers=True)
st.plotly_chart(fig6)

# --------------------------------------------------
# 10. 연속 운동일 Top 5
st.subheader("10. 연속 운동 기록 상위 5명")
df_sorted = df.sort_values(["이름", "날짜"])
df_sorted["이전날짜"] = df_sorted.groupby("이름")["날짜"].shift()
df_sorted["연속일"] = df_sorted["날짜"] - df_sorted["이전날짜"]
df_sorted["연속시작"] = df_sorted["연속일"].dt.days.ne(1)
df_sorted["연속그룹"] = df_sorted.groupby("이름")["연속시작"].cumsum()
연속_집계 = df_sorted.groupby(["이름", "연속그룹"]).size().reset_index(name="연속일수")
연속_최대 = 연속_집계.groupby("이름")["연속일수"].max().reset_index()
연속_최대 = 연속_최대.sort_values("연속일수", ascending=False).head(5)
st.dataframe(연속_최대)



















# client_id = '451309640'
# secret_key = 'yFJK6UIU0K1QKHWEPgfkDG4p3WCN7njG'
# access_token = 'ZQAAAXpkS3AD8GMRxNfUvYdC3CclnXbY-xKi1kzI51MKSAhsvYufcwBAxlJrxGKKfBH77dH0OsVpKcdyosyk4BuFgo3NUjmlaDlLFrPepA6YD_gE'
# redirect_url = 'jb_fiteness'
# band_key = 'AAAopGD2fd0ihMGOdEqAPTjY'
# max_pages = 80

# params = {
#     'client_id': client_id,
#     'secret_key': secret_key,
#     'access_token': access_token,
#     'redirect_url': redirect_url,
#     'band_key': band_key,
#     'locale' : 'ko_KR'
# }


# pd.options.display.max_colwidth = None  # 컬럼 값 생략 없이 전체 출력
# # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# team_members = {
#     '1팀': ['서인철', '김민선', '장혜윤', '장진철'],
#     '2팀': ['심재한', '고한솔', '이세형', '윤예지'],
#     '3팀': ['김영수', '임상미', '장선우', '이찬솔'],
#     '4팀': ['조민국', '홍보선', '안수범', '송광수', '전명훈'],
#     '5팀': ['곽태경', '윤균성', '박운학', '장창수'],
#     '6팀': ['최재용', '장서혁', '권수정', '한승호'],
#     '7팀': ['박채은', '강다은', '조환익', '유인하'],
#     '8팀': ['이수형', '문채영', '장명기', '조효진'],
#     '9팀': ['윤성민', '박상연', '안채은', '정상훈']
# }

# # 운동 관련 키워드 리스트
# target_keywords = ['걷기', '달리기', '러닝', '산책', '러닝머신', '런닝머신', '계단타기', '등산',
#                    '자전거', '사이클',
#                    '수영',
#                    '딥스', '풀업', '근력', '스쿼트', '크로스핏', '웨이트',
#                    '요가', '필라테스', '스트레칭',
#                    '클라이밍']

# def fetch_band_posts(client_id, secret_key, access_token, redirect_url, band_key, max_pages=50):
#     """
#     Band API에서 게시글 데이터를 가져와 DataFrame으로 변환하는 함수

#     :param client_id: Band API 클라이언트 ID
#     :param secret_key: Band API 시크릿 키
#     :param access_token: 인증 토큰
#     :param redirect_url: 리디렉트 URL
#     :param band_key: Band 그룹 키
#     :param max_pages: 최대 페이지 수 (기본값 10)

#     :return: pandas DataFrame
#     """
#     url = 'https://openapi.band.us/v2/band/posts'

#     # 초기 요청 파라미터 설정
#     params = {
#         'client_id': client_id,
#         'secret_key': secret_key,
#         'access_token': access_token,
#         'redirect_url': redirect_url,
#         'band_key': band_key,
#         'locale': 'ko_KR'
#     }

#     all_posts = []  # 모든 데이터를 저장할 리스트
#     page_count = 0  # 페이지 수 카운트
#     cutoff_date = pd.Timestamp('2025-02-23 00:00:00', tz='Asia/Seoul')  # 기준일 (KST)

#     while page_count < max_pages:
#         response = requests.get(url, params=params)

#         if response.status_code != 200:
#             print(f"❌ 요청 실패: {response.status_code}, {response.text}")
#             break

#         data = response.json().get('result_data', {})
#         items = data.get('items', [])

#         if not items:
#             print("✅ 더 이상 가져올 게시글이 없습니다.")
#             break

#         for item in items:
#             created_at_kst = pd.to_datetime(item['created_at'], unit='ms', utc=True).tz_convert('Asia/Seoul')

#             if created_at_kst < cutoff_date:
#                 continue

#             author_name = item['author']['name']
#             team_name = next((team for team, members in team_members.items() if author_name in members), '기타')
#             photo_urls = [photo.get('url') for photo in item.get('photos', [])]

#             post_data = {
#                 'author_name': author_name,
#                 'team_name': team_name,
#                 'created_at': created_at_kst.strftime('%Y-%m-%d %H:%M:%S'),
#                 'created_at_ymd': created_at_kst.strftime('%Y-%m-%d'),
#                 'content': item['content'],
#                 'photo_url': photo_urls,
#                 'comment_count': item['comment_count'],
#                 'emotion_count': item['emotion_count']
#             }
#             all_posts.append(post_data)

#         # 다음 페이지 요청을 위한 next_params 설정
#         next_params = data.get('paging', {}).get('next_params', {}).get('after')
#         if not next_params:
#             break  # 다음 페이지가 없으면 종료

#         params['after'] = next_params  # 다음 페이지 요청을 위해 after 값 업데이트
#         page_count += 1

#         # API 요청 간격 조절 (반복 요청 방지)
#         time.sleep(1)

#     df = pd.DataFrame(all_posts)
#     df.insert(0, 'No', range(1, len(df) + 1))  # No 컬럼 추가
#     return df


# df = fetch_band_posts(client_id, secret_key, access_token, redirect_url, band_key, max_pages)
# df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

# # new_column_order = ['author_name', 'content', 'comment_count', 'created_at', 'photo_url','emotion_count', 'created_at_ymd', 'team_name', 'nouns']
# # df = df[new_column_order]


# #
# # # 1. 날짜별 팀별 게시글 수 집계
# # df_grouped = df.groupby(['created_at_ymd', 'team_name']).size().reset_index(name='post_count')
# #
# # # 2. 피벗 테이블 변환 (행: 날짜, 열: 팀명, 값: 게시글 수)
# # df_pivot = df_grouped.pivot_table(index='created_at_ymd', columns='team_name', values='post_count', fill_value=0)
# #
# # # 3. 누적 합 계산
# # df_pivot_cumsum = df_pivot.cumsum(axis=0)
# #
# # # 4. 시각화
# # plt.figure(figsize=(12, 6))
# # df_pivot_cumsum.plot(marker='o', linestyle='-', figsize=(12, 6))
# # # plt.rc('font', family=font_name)
# #
# # plt.xlabel('날짜', fontsize=12)
# # plt.ylabel('누적 게시글 수', fontsize=12)
# # plt.title('팀별 누적 게시글 수 추이', fontsize=14)
# # plt.xticks(rotation=45)
# # plt.legend(title='팀명')
# # plt.grid(True)
# # plt.show()



# # 날짜 컬럼이 없으면 생성
# if "created_at_ymd" not in df.columns:
#     df["created_at_ymd"] = pd.to_datetime(df["created_at"]).dt.date

# st.title("💪 팀별 / 개인별 운동 게시글 분석")

# df["created_at_ymd"] = pd.to_datetime(df["created_at_ymd"]).dt.date

# # 날짜 필터
# st.sidebar.header("📅 날짜 필터")
# start_date = st.date_input("시작 날짜", df["created_at_ymd"].min())
# end_date = st.date_input("종료 날짜", df["created_at_ymd"].max())
# df_filtered = df[(df["created_at_ymd"] >= start_date) & (df["created_at_ymd"] <= end_date)]


# # 팀별 누적 게시글 수
# st.subheader("📈 팀별 누적 게시글 수")
# df_grouped = df_filtered.groupby(['created_at_ymd', 'team_name']).size().reset_index(name='post_count')
# df_pivot = df_grouped.pivot_table(index='created_at_ymd', columns='team_name', values='post_count', fill_value=0)
# df_cumsum = df_pivot.cumsum()
# fig1 = px.line(df_cumsum, x=df_cumsum.index, y=df_cumsum.columns, markers=True, labels={"value": "누적 게시글 수"})
# st.plotly_chart(fig1)

# # 개인별 게시글 수
# st.subheader("🧍‍♂️ 개인별 게시글 수")
# user_counts = df_filtered['author_name'].value_counts().reset_index()
# user_counts.columns = ['사용자', '게시글 수']
# st.dataframe(user_counts)

# # 인기 게시글 TOP5
# st.subheader("🔥 인기 게시글 TOP 5")
# df_filtered["total_reaction"] = df_filtered["emotion_count"] + df_filtered["comment_count"]
# top5 = df_filtered.sort_values("total_reaction", ascending=False).head(5)[['author_name', 'content', 'emotion_count', 'comment_count', 'photo_url']]
# st.dataframe(top5)

# # 요일별 활동
# st.subheader("📆 요일별 게시글 활동")
# df_filtered["weekday"] = pd.to_datetime(df_filtered["created_at"]).dt.day_name()
# weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
# weekday_counts = df_filtered['weekday'].value_counts().reindex(weekday_order).fillna(0)
# fig2 = px.bar(weekday_counts, x=weekday_counts.index, y=weekday_counts.values, labels={"x": "요일", "y": "게시글 수"}, title="요일별 게시글 수")
# st.plotly_chart(fig2)

# # 개인 필터링 활동 내역 (예시로 첫 사용자)
# st.subheader("🙋‍♀️ 사용자별 활동 내역")
# user_list = df_filtered["author_name"].unique().tolist()
# selected_user = st.selectbox("사용자 선택", options=user_list)

# user_df = df_filtered[df_filtered["author_name"] == selected_user]
# if selected_user:
#     user_df = df_filtered[df_filtered["author_name"] == selected_user]
#     daily_counts = user_df.groupby("created_at_ymd").size().reset_index(name="post_count")
#     fig3 = px.line(daily_counts, x="created_at_ymd", y="post_count", title=f"{selected_user}님의 일별 게시글 수")
#     st.plotly_chart(fig3)
# else:
#     st.write("데이터가 없습니다.")

# # 키워드 워드클라우드
# st.subheader("☁️ 운동 키워드 워드클라우드")

# # matplotlib 한글 폰트 설정
# fontprop = font_manager.FontProperties(fname=font_path).get_name()
# plt.rcParams['font.family'] = fontprop

# keyword_list = []
# for text in df_filtered['content'].dropna():
#     words = text.split()
#     for word in words:
#         for keyword in target_keywords:
#             if keyword in word:
#                 keyword_list.append(keyword)
# if keyword_list:
#     counter = Counter(keyword_list)
#     wordcloud = WordCloud(font_path=font_path, background_color='white', width=800, height=400).generate_from_frequencies(counter)
#     fig4, ax = plt.subplots(figsize=(10, 5))
#     ax.imshow(wordcloud, interpolation='bilinear')
#     ax.axis("off")
#     st.pyplot(fig4)
# else:
#     st.write("운동 관련 키워드가 포함된 게시글이 없습니다.")


