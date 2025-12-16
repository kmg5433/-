import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
from matplotlib import rc
import seaborn as sns


# ===== 그래프 스타일 =====
sns.set(style="whitegrid")


# ===== 한글 폰트 설정 =====
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


if platform.system() == 'Linux':
    fontname = './NanumGothic.ttf'
    fm.fontManager.addfont(fontname)
    rc('font', family='NanumGothic')


# ===== 제목 / 헤더 =====
st.markdown(
    """
    <h1 style="text-align:center; font-weight:700; color:#2C3E50;">
        📊 지방재정 예산 분석 대시보드
    </h1>
    <p style="text-align:center; font-size:17px; color:#7F8C8D;">
        다양한 지표를 기반으로 기관별 예산 흐름과 재정 구조를 한눈에 파악할 수 있습니다.
    </p>
    <br>
    """,
    unsafe_allow_html=True
)


# ===== CSV 파일 자동 로드 =====
file_path = "________________20251104182351.csv"


try:
    df = pd.read_csv(file_path, encoding="utf-8")
except:
    st.error(f"❌ 데이터 파일을 불러올 수 없습니다: {file_path}")
    st.stop()


# ======================================================
# 기본 전처리
# ======================================================
df.columns = df.columns.str.strip()


def clean_numeric(col):
    return (
        col.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("-", "0", regex=False)
        .str.replace(" ", "", regex=False)
        .fillna("0")
        .astype(float)
    )


numeric_cols = [c for c in df.columns if "원" in c or "액" in c]
for col in numeric_cols:
    df[col] = clean_numeric(df[col])


df["회계연도"] = (
    df["회계연도"]
    .astype(str)
    .str.extract(r"(\d+)", expand=False)
    .fillna("0")
    .astype(int)
)


# ======================================================
# 사이드바 메뉴
# ======================================================
st.sidebar.title("📌 분석 메뉴")
analysis = st.sidebar.radio(
    "보고 싶은 분석 유형",
    [
        "회계연도별 예산 vs 지출 상관관계",
        "소관명별 평균 예산 규모 비교",
        "연도별 세입/세출 증감액 추이",
        "소관명별 불용액 분포",
        "이월액 vs 예산 관계 분석"
    ]
)


# ======================================================
# 데이터 샘플
# ======================================================
st.subheader("🔍 데이터 미리보기")
st.dataframe(df.head())


# ======================================================
# ① 회계연도별 예산 vs 지출 상관관계
# ======================================================
if analysis == "회계연도별 예산 vs 지출 상관관계":
    st.markdown("## 📈 회계연도별 예산현액과 지출액의 상관성 분석")


    corr_df = df.groupby("회계연도")[["(세출)예산현액(원)", "(세출)지출액(원)"]].sum()
    corr_value = corr_df.corr().iloc[0, 1]


    st.info(f"✔ 예산과 지출의 상관계수: **{corr_value:.4f}**")


    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(
        x=corr_df["(세출)예산현액(원)"],
        y=corr_df["(세출)지출액(원)"],
        ax=ax,
        color="#2E86C1"
    )
    ax.set_title("예산 규모와 지출의 관계")
    st.pyplot(fig)


    st.info(f"회계연도별 예산현액과 지출액을 비교해보면, 전반적으로 예산 규모가 큰 연도일수록 지출액도 높은 상관관계를 보이고 있습니다. 다만 일부 연도에서는 예산이 크게 책정되었음에도 불구하고 실제 지출은 상대적으로 적어 불용액이 발생했을 가능성이 있습니다. 이러한 연도별 차이를 보면 예산 집행의 효율성을 높이기 위해 집행 계획과 일정 관리가 필요함을 알 수 있습니다.")


# ======================================================
# ② 소관명별 평균 예산 규모 비교
# ======================================================
elif analysis == "소관명별 평균 예산 규모 비교":
    st.markdown("## 🏢 소관명별 평균 예산 규모 비교")


    N = st.slider("표시할 기관 수 (Top N)", 5, 50, 20)


    mean_budget = (
        df.groupby("소관명")["(세출)예산현액(원)"]
        .mean()
        .sort_values(ascending=False)
        .head(N)
    )


    fig, ax = plt.subplots(figsize=(10, N * 0.35))
    mean_budget.sort_values().plot(kind="barh", ax=ax, color="#5DADE2")
    ax.set_title(f"소관명별 평균 예산 규모 TOP {N}")
    ax.set_xlabel("평균 예산현액 (원)")
    st.pyplot(fig)


    st.info(f"소관별 평균 예산 규모를 보면, 일부 기관은 전체 평균보다 월등히 높은 예산을 배정받아 중앙 집중적인 자금 운영 구조를 보여줍니다. 반면 예산이 상대적으로 작은 소관은 사업 수행 여력이 제한될 수 있으며, 소관 간 예산 편차가 크다는 점은 정책적 우선순위와 예산 배분 전략을 검토할 필요가 있음을 시사합니다. Top N 기관 중심으로 예산 운영의 효율성을 높이는 전략을 고려할 수 있습니다.")


# ③ 연도별 세입·세출 증감액 추이
# ======================================================
elif analysis == "연도별 세입/세출 증감액 추이":
    st.markdown("## 📉 연도별 세입 및 세출 증감액 추이")


    yearly = df.groupby("회계연도")[["(세입)증감액(원)", "(세출)증감액(원)"]].sum()


    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(yearly.index, yearly["(세입)증감액(원)"], marker="o", label="세입 증감액", color="#2ECC71")
    ax.plot(yearly.index, yearly["(세출)증감액(원)"], marker="o", label="세출 증감액", color="#E74C3C")
    ax.set_title("연도별 세입·세출 증감 추세")
    ax.set_xlabel("회계연도")
    ax.set_ylabel("금액 (원)")
    ax.legend()
    st.pyplot(fig)


    st.info(f"연도별 세입과 세출 증감액을 살펴보면, 두 지표가 대체로 유사한 추세를 보이지만 연도별로 변동 폭 차이가 존재합니다. 특히 특정 연도에는 세입이 큰 폭으로 증가했음에도 세출 증감액은 상대적으로 적어 불용액이나 이월액이 발생했을 가능성이 있습니다. 이러한 추세를 통해 재정 운용의 안정성을 평가하고, 필요한 경우 집행 속도를 조절할 근거를 마련할 수 있습니다.")


# ======================================================
# ④ 소관명별 불용액 분포 분석
# ======================================================
elif analysis == "소관명별 불용액 분포":
    st.markdown("## 🟩 소관명별 불용액(잔액) 분포 분석")


    N = st.slider("표시할 기관 수 (Top N)", 5, 50, 20)


    unused = (
        df.groupby("소관명")["불용액(원)"]
        .sum()
        .sort_values(ascending=False)
        .head(N)
    )


    fig, ax = plt.subplots(figsize=(10, N * 0.35))
    unused.sort_values().plot(kind="barh", ax=ax, color="#58D68D")
    ax.set_title(f"소관명별 불용액 TOP {N}")
    ax.set_xlabel("불용액 (원)")
    st.pyplot(fig)


    st.info(f"불용액 분포를 분석하면 일부 소관에 불용액이 집중되어 있으며, 이는 해당 기관의 예산 집행 계획이나 시기 조정에 문제가 있음을 시사합니다. 불용액 규모가 큰 소관을 중심으로 예산 집행 패턴을 분석하면, 반복적으로 발생하는 불용액을 줄이고 예산 운용 효율성을 개선할 수 있는 근거가 됩니다.")


# ======================================================
# ⑤ 이월액 vs 예산 관계 분석
# ======================================================
elif analysis == "이월액 vs 예산 관계 분석":
    st.markdown("## 🔄 다음년도 이월액과 예산 간의 관계")


   


    relation_df = df.groupby("회계연도")[["다음년도이월액(원)", "(세출)예산현액(원)"]].sum()


    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(
        x=relation_df["(세출)예산현액(원)"],
        y=relation_df["다음년도이월액(원)"],
        ax=ax,
        color="#AF7AC5"
    )
    ax.set_title("예산 규모와 이월액의 회귀 분석")
    ax.set_xlabel("예산현액 (원)")
    ax.set_ylabel("다음년도 이월액 (원)")
    st.pyplot(fig)


    st.info(f"예산이 큰 소관일수록 다음년도 이월액도 상대적으로 큰 경향을 보임. 예산 대비 이월액 비율이 높은 소관은 계획 대비 집행 속도가 느린 것으로 해석 가능함. 이를 통해, 예산 규모와 집행 속도, 이월액 관리 전략을 조정할 수 있음.")



