import pandas as pd
import matplotlib.pyplot as plt

# 1) CSV 파일 불러오기
file_path = "________________20251104182351.csv"  # 파일명만 바꿔주면 됨
df = pd.read_csv(file_path)

# 2) 숫자형 컬럼 전처리 (콤마 제거 후 int 변환)
num_cols = [
    "(세입)예산현액(원)", "(세입)수납액(원)", "(세입)증감액(원)",
    "(세출)예산현액(원)", "(세출)지출액(원)", "(세출)증감액(원)",
    "다음년도이월액(원)", "불용액(원)"
]

for col in num_cols:
    df[col] = df[col].str.replace(",", "").astype(int)

# 3) 데이터 확인
print("\n===== 데이터 기본 정보 =====")
print(df.head())
print(df.describe())

# 4) 기관별 예산 집행 효율 계산
df["세출집행률(%)"] = (df["(세출)지출액(원)"] / df["(세출)예산현액(원)"]) * 100

# 5) 기관별 평균 집행률 상위 10개
eff_top = df.groupby("소관명")["세출집행률(%)"].mean().sort_values(ascending=False).head(10)
print("\n===== 세출 집행 효율 상위 10개 기관 =====")
print(eff_top)

# 6) 연도별 총 예산 변화
year_budget = df.groupby("회계연도")["(세출)예산현액(원)"].sum()

print("\n===== 연도별 총 세출 예산 =====")
print(year_budget)

# 7) 시각화: 연도별 총 예산 변화 그래프
plt.figure(figsize=(10,5))
plt.plot(year_budget.index, year_budget.values, marker='o')
plt.title("연도별 총 세출 예산 추세")
plt.xlabel("회계연도")
plt.ylabel("총 예산액(원)")
plt.xticks(rotation=45)
plt.show()


