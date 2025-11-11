import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
from matplotlib import rc


# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 깃허브 리눅스 기준
if platform.system() == 'Linux':
    fontname = './NanumGothic.ttf'
    font_files = fm.findSystemFonts(fontpaths=fontname)
    fm.fontManager.addfont(fontname)
    fm._load_fontmanager(try_read_cache=False)
    rc('font', family='NanumGothic')

    
st.title("기관별 예산 분석 대시보드")

# ✅ CSV 파일 경로 (같은 폴더에 있을 경우)
file_path = "________________20251104182351.csv"  # ← 여기를 네 CSV 파일명으로 바꿔줘

# CSV 불러오기
df = pd.read_csv(file_path)

# 숫자형 컬럼 전처리
num_cols = [
    "(세입)예산현액(원)", "(세입)수납액(원)", "(세입)증감액(원)",
    "(세출)예산현액(원)", "(세출)지출액(원)", "(세출)증감액(원)",
    "다음년도이월액(원)", "불용액(원)"
]

for col in num_cols:
    df[col] = df[col].str.replace(",", "").astype(int)

# 세출 집행률 계산
df["세출집행률(%)"] = (df["(세출)지출액(원)"] / df["(세출)예산현액(원)"]) * 100

# 데이터 미리보기
st.subheader("📌 데이터 미리보기")
st.dataframe(df.head())

# 기관 선택
selected_org = st.selectbox("기관을 선택하세요", sorted(df["소관명"].unique()))
filtered = df[df["소관명"] == selected_org]

st.subheader(f"📌 선택한 기관 분석: {selected_org}")
st.dataframe(filtered)

# 연도별 예산 변화 그래프
year_budget = df.groupby("회계연도")["(세출)예산현액(원)"].sum()

st.subheader("📈 연도별 총 세출 예산 추세")
fig, ax = plt.subplots()
ax.plot(year_budget.index, year_budget.values, marker='o')
ax.set_xlabel("회계연도")
ax.set_ylabel("총 세출 예산액(원)")
ax.set_title("연도별 총 세출 예산 추세")

st.pyplot(fig)
