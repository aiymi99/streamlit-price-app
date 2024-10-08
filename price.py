import streamlit as st
import pandas as pd
from PIL import Image
import os
from datetime import datetime

# 메모 데이터를 저장하는 경로
note_file_path = "user_note.txt"

# 메모 데이터를 저장하는 함수
def save_note_data(note_content):
    with open(note_file_path, "w") as f:
        f.write(note_content)

# 메모 데이터를 불러오는 함수
def load_note_data():
    if os.path.exists(note_file_path):
        with open(note_file_path, "r") as f:
            return f.read()
    return ""

# 화면을 넓게 사용하는 wide 레이아웃 설정
st.set_page_config(layout="wide")

# 저장된 업데이트 정보를 불러오는 함수
def load_last_update(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read().strip()
    return "업데이트된 기록이 없습니다."

# 업데이트 정보를 저장하는 함수
def save_last_update(file_path, update_date):
    with open(file_path, 'w') as file:
        file.write(update_date)

# 최종 업데이트된 PNG 파일 열기
def load_latest_png():
    png_update_path = "last_png_update.txt"
    if os.path.exists(png_update_path):
        with open(png_update_path, 'r') as file:
            last_png_file = file.read().strip()
        if os.path.exists(last_png_file):
            return Image.open(last_png_file)
    return None

# 최종 업데이트된 엑셀 파일 로드
def load_latest_excel():
    excel_update_path = "last_excel_update.txt"
    if os.path.exists(excel_update_path):
        with open(excel_update_path, 'r') as file:
            last_excel_file = file.read().strip()
        if os.path.exists(last_excel_file):
            return pd.read_excel(last_excel_file)
    return None

# 파일 경로 정의
excel_update_path = "last_excel_update.txt"
png_update_path = "last_png_update.txt"

# 파일 저장 경로 확인 후 폴더 생성
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# 사이드바에 업데이트 관련 기능 추가
st.sidebar.title("파일 업데이트")
st.sidebar.subheader("엑셀 파일 업데이트")

# 엑셀 파일 업데이트 기능
excel_file = st.sidebar.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx"])
if excel_file:
    ensure_directory_exists("uploaded_files")  # 엑셀 파일 저장 경로 생성
    excel_path = f"uploaded_files/{excel_file.name}"
    with open(excel_path, "wb") as f:
        f.write(excel_file.getbuffer())
    st.sidebar.success("엑셀 파일이 성공적으로 업데이트되었습니다!")
    last_update_excel = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_last_update(excel_update_path, excel_path)  # 저장 경로 기록

# 최종 엑셀 파일 업데이트 날짜 표시
last_update_excel = load_last_update(excel_update_path)
st.sidebar.write(f"최종 엑셀 파일 업데이트: {last_update_excel}")

st.sidebar.subheader("PNG 파일 업데이트")

# PNG 파일 업데이트 기능
png_file = st.sidebar.file_uploader("PNG 파일을 업로드하세요", type=["png"])
if png_file:
    ensure_directory_exists("uploaded_images")  # 저장할 폴더가 없으면 생성
    png_path = f"uploaded_images/{png_file.name}"  # 이미지 저장 경로
    with open(png_path, "wb") as f:
        f.write(png_file.getbuffer())
    st.sidebar.success("PNG 파일이 성공적으로 업데이트되었습니다!")
    last_update_png = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_last_update(png_update_path, png_path)  # 저장 경로 기록

# 최종 PNG 파일 업데이트 날짜 표시
last_update_png = load_last_update(png_update_path)
st.sidebar.write(f"최종 PNG 파일 업데이트: {last_update_png}")

# 0.5:1.5:2 비율로 화면을 가로로 3개 영역으로 나눔
col1, col2, col3 = st.columns([0.5, 1.5, 2])

# 1. 메모할 수 있는 공간 (노란색 배경, 검은 선) - 세로 길이 현재의 50%로 축소
with col1:
    st.header("메모")

    # 기존 메모 불러오기
    user_note = load_note_data()

    # 메모 입력 및 자동 저장
    user_note = st.text_area("여기에 메모를 작성하세요:", user_note, height=200)
    save_note_data(user_note)  # 메모 내용 자동 저장

# 2. 판매 단가 조회 기능
with col2:
    st.header("판매 단가 조회")
    
    # 최종 업데이트된 엑셀 파일을 자동으로 불러옴
    df = load_latest_excel()
    
    if df is not None:
        if '품목명' in df.columns and '판매일자' in df.columns and 'cust_name' in df.columns and '단가' in df.columns:
            # '판매일자' 형식 수정 및 "00:00:00" 제거
            if df['판매일자'].dtype == 'int64' or df['판매일자'].dtype == 'float64':
                df['판매일자'] = pd.to_datetime(df['판매일자'].astype(str), format='%Y%m%d', errors='coerce')
            elif df['판매일자'].dtype == 'object':
                df['판매일자'] = pd.to_datetime(df['판매일자'], format='%Y%m%d', errors='coerce')
            df['판매일자'] = df['판매일자'].dt.strftime('%Y-%m-%d')  # "00:00:00" 제거

            # 품명을 검색
            product_input = st.text_input("품명을 입력하세요", value="")
            product_list = df['품목명'].unique().tolist()
            product_list.insert(0, "없음")  # 목록 상단에 "없음" 추가
            autocomplete_product = [p for p in product_list if product_input.lower() in p.lower()]
            
            if autocomplete_product:
                selected_product = st.selectbox("자동완성된 품목명", autocomplete_product)

                if selected_product != "없음":  # 선택된 값이 "없음"이 아닐 경우만 진행
                    # 품명으로 필터링된 결과
                    filtered_df = df[df['품목명'] == selected_product]

                    # 거래처명을 선택적 필터링 (부분 입력도 허용)
                    customer_input = st.text_input("거래처명을 입력하세요 (필수 아님)", value="")
                    if customer_input:
                        autocomplete_customer = [c for c in filtered_df['cust_name'].unique().tolist() if customer_input.lower() in c.lower()]
                        if autocomplete_customer:
                            selected_customer = st.selectbox("자동완성된 거래처명", autocomplete_customer)

                            # 거래처명으로 추가 필터링된 결과
                            final_df = filtered_df[filtered_df['cust_name'] == selected_customer]
                        else:
                            st.warning("해당 거래처명이 없습니다.")
                    else:
                        final_df = filtered_df  # 거래처명을 입력하지 않은 경우 전체 결과 표시

                    # 결과 개수 선택 (기본값 10개)
                    result_count = st.radio("결과 개수 선택", (5, 10), index=1)

                    # 선택된 품목 및 거래처명의 최근 판매 정보를 가져오기
                    final_df = final_df.sort_values(by='판매일자', ascending=False).head(result_count)

                    if not final_df.empty:
                        st.write(f"최근 {result_count}개의 판매 기록:")
                        st.write(final_df[['판매일자', 'cust_name', '단가']].reset_index(drop=True))
                    else:
                        st.warning("해당 품목의 판매 기록이 없습니다.")
            else:
                st.warning("해당 품목이 없습니다.")
        else:
            st.error("'품목명', '판매일자', 'cust_name', '단가' 열이 엑셀 파일에 존재하지 않습니다.")
    else:
        st.warning("엑셀 파일이 존재하지 않거나 업데이트되지 않았습니다.")

# 3. PNG 파일 표시 기능 (너비 750 고정, 스크롤바 없음)
with col3:
    st.header("최신 PNG 파일")
    latest_png = load_latest_png()
    if latest_png:
        st.image(latest_png, caption='최신 업데이트된 이미지', width=750)
    else:
        st.warning("PNG 파일이 없습니다. 사이드바에서 PNG 파일을 업로드하세요.")
