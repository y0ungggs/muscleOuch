import pandas as pd
import numpy as np
import json
import requests
from urllib import request
import time
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import streamlit as st



client_id = '451309640'
secret_key = 'yFJK6UIU0K1QKHWEPgfkDG4p3WCN7njG'
access_token = 'ZQAAAXpkS3AD8GMRxNfUvYdC3CclnXbY-xKi1kzI51MKSAhsvYufcwBAxlJrxGKKfBH77dH0OsVpKcdyosyk4BuFgo3NUjmlaDlLFrPepA6YD_gE'
redirect_url = 'jb_fiteness'
band_key = 'AAAopGD2fd0ihMGOdEqAPTjY'
max_pages = 5

params = {
    'client_id': client_id,
    'secret_key': secret_key,
    'access_token': access_token,
    'redirect_url': redirect_url,
    'band_key': band_key,
    'locale' : 'ko_KR'
}


pd.options.display.max_colwidth = None  # 컬럼 값 생략 없이 전체 출력
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

team_members = {
    '1팀': ['서인철', '김민선', '장혜윤', '장진철'],
    '2팀': ['심재한', '고한솔', '이세형', '윤예지'],
    '3팀': ['김영수', '임상미', '장선우', '이찬솔'],
    '4팀': ['조민국', '홍보선', '안수범', '송광수', '전명훈'],
    '5팀': ['곽태경', '윤균성', '박운학', '장창수'],
    '6팀': ['최재용', '장서혁', '권수정', '한승호'],
    '7팀': ['박채은', '강다은', '조환익', '유인하'],
    '8팀': ['이수형', '문채영', '장명기', '조효진'],
    '9팀': ['윤성민', '박상연', '안채은', '정상훈']
}

# 운동 관련 키워드 리스트
target_keywords = ['걷기', '달리기', '러닝', '산책', '러닝머신', '런닝머신', '계단타기', '등산',
                   '자전거', '사이클',
                   '수영',
                   '딥스', '풀업', '근력', '스쿼트', '크로스핏', '웨이트',
                   '요가', '필라테스', '스트레칭',
                   '클라이밍']

def fetch_band_posts(client_id, secret_key, access_token, redirect_url, band_key, max_pages=50):
    """
    Band API에서 게시글 데이터를 가져와 DataFrame으로 변환하는 함수

    :param client_id: Band API 클라이언트 ID
    :param secret_key: Band API 시크릿 키
    :param access_token: 인증 토큰
    :param redirect_url: 리디렉트 URL
    :param band_key: Band 그룹 키
    :param max_pages: 최대 페이지 수 (기본값 10)

    :return: pandas DataFrame
    """
    url = 'https://openapi.band.us/v2/band/posts'

    # 초기 요청 파라미터 설정
    params = {
        'client_id': client_id,
        'secret_key': secret_key,
        'access_token': access_token,
        'redirect_url': redirect_url,
        'band_key': band_key,
        'locale': 'ko_KR'
    }

    all_posts = []  # 모든 데이터를 저장할 리스트
    page_count = 0  # 페이지 수 카운트
    cutoff_date = pd.Timestamp('2025-02-23 00:00:00', tz='Asia/Seoul')  # 기준일 (KST)

    while page_count < max_pages:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"❌ 요청 실패: {response.status_code}, {response.text}")
            break

        data = response.json().get('result_data', {})
        items = data.get('items', [])

        if not items:
            print("✅ 더 이상 가져올 게시글이 없습니다.")
            break

        for item in items:
            created_at_kst = pd.to_datetime(item['created_at'], unit='ms', utc=True).tz_convert('Asia/Seoul')

            if created_at_kst < cutoff_date:
                continue

            author_name = item['author']['name']
            team_name = next((team for team, members in team_members.items() if author_name in members), '기타')
            photo_urls = [photo.get('url') for photo in item.get('photos', [])]

            post_data = {
                'author_name': author_name,
                'team_name': team_name,
                'created_at': created_at_kst.strftime('%Y-%m-%d %H:%M:%S'),
                'created_at_ymd': created_at_kst.strftime('%Y-%m-%d'),
                'content': item['content'],
                'photo_url': photo_urls,
                'comment_count': item['comment_count'],
                'emotion_count': item['emotion_count']
            }
            all_posts.append(post_data)

        # 다음 페이지 요청을 위한 next_params 설정
        next_params = data.get('paging', {}).get('next_params', {}).get('after')
        if not next_params:
            break  # 다음 페이지가 없으면 종료

        params['after'] = next_params  # 다음 페이지 요청을 위해 after 값 업데이트
        page_count += 1

        # API 요청 간격 조절 (반복 요청 방지)
        time.sleep(1)

    df = pd.DataFrame(all_posts)
    df.insert(0, 'No', range(1, len(df) + 1))  # No 컬럼 추가
    return df


df = fetch_band_posts(client_id, secret_key, access_token, redirect_url, band_key, max_pages)
df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

# new_column_order = ['author_name', 'content', 'comment_count', 'created_at', 'photo_url','emotion_count', 'created_at_ymd', 'team_name', 'nouns']
# df = df[new_column_order]


#
# # 1. 날짜별 팀별 게시글 수 집계
# df_grouped = df.groupby(['created_at_ymd', 'team_name']).size().reset_index(name='post_count')
#
# # 2. 피벗 테이블 변환 (행: 날짜, 열: 팀명, 값: 게시글 수)
# df_pivot = df_grouped.pivot_table(index='created_at_ymd', columns='team_name', values='post_count', fill_value=0)
#
# # 3. 누적 합 계산
# df_pivot_cumsum = df_pivot.cumsum(axis=0)
#
# # 4. 시각화
# plt.figure(figsize=(12, 6))
# df_pivot_cumsum.plot(marker='o', linestyle='-', figsize=(12, 6))
# # plt.rc('font', family=font_name)
#
# plt.xlabel('날짜', fontsize=12)
# plt.ylabel('누적 게시글 수', fontsize=12)
# plt.title('팀별 누적 게시글 수 추이', fontsize=14)
# plt.xticks(rotation=45)
# plt.legend(title='팀명')
# plt.grid(True)
# plt.show()



# 날짜 컬럼이 없으면 생성
if "created_at_ymd" not in df.columns:
    df["created_at_ymd"] = pd.to_datetime(df["created_at"]).dt.date

st.title("💪 팀별 / 개인별 운동 게시글 분석")

# 날짜 필터
start_date = st.date_input("시작 날짜", df["created_at_ymd"].min())
end_date = st.date_input("종료 날짜", df["created_at_ymd"].max())
df_filtered = df[(df["created_at_ymd"] >= start_date) & (df["created_at_ymd"] <= end_date)]

# 팀별 게시글 수 누적 시계열
st.subheader("📈 팀별 누적 게시글 수")

df_grouped = df_filtered.groupby(['created_at_ymd', 'team_name']).size().reset_index(name='post_count')
df_pivot = df_grouped.pivot_table(index='created_at_ymd', columns='team_name', values='post_count', fill_value=0)
df_cumsum = df_pivot.cumsum()

fig = px.line(df_cumsum, x=df_cumsum.index, y=df_cumsum.columns, markers=True, labels={"value": "누적 게시글 수"})
st.plotly_chart(fig)

# 개인별 게시글 수
st.subheader("🧍‍♂️ 개인별 게시글 수")
user_counts = df_filtered['author_name'].value_counts().reset_index()
user_counts.columns = ['사용자', '게시글 수']
st.dataframe(user_counts)

# 감정/댓글 수 많은 게시글 상위 5개
st.subheader("🔥 인기 게시글 TOP 5")
df_filtered["total_reaction"] = df_filtered["emotion_count"] + df_filtered["comment_count"]
top5 = df_filtered.sort_values("total_reaction", ascending=False).head(5)[['author_name', 'content', 'emotion_count', 'comment_count', 'photo_url']]
st.dataframe(top5)
