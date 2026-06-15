"""Script auxiliar de perfilado para el informe (evidencia técnica)."""
import pandas as pd

df = pd.read_csv("dataset_maestro.csv")
db = pd.read_csv("dataset_barrios_mensual.csv")

print("=== MAESTRO describe precio ===")
print(df["precio_promedio_pesos"].describe())
print("\n=== MAESTRO ratio monoambiente (%) ===")
mono = df[df["ambientes"] == 1]["ratio_alquiler_sueldo_pct"].dropna()
print(mono.describe())
print("\n=== Duplicados maestro ===", df.duplicated(subset=["comuna", "periodo_trim", "ambientes"]).sum())
print("\n=== Provisorio ===")
print(df["provisorio"].value_counts(dropna=False))
print("\n=== Sueldo en maestro ===")
print("NaN sueldo:", df["sueldo_basico_admin_a"].isna().sum())
print("\n=== BARIOS ===")
print("Shape:", db.shape, "| barrios:", db["barrio"].nunique())
print("Sueldo interpolado:", db["sueldo_interpolado"].fillna(False).astype(bool).sum())
