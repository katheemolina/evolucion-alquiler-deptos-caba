"""
Extrae sueldo básico mensual de ADMINISTRATIVO A (empleados de comercio)
y genera datasets mensual y trimestral (Q1-Q4) desde enero 2018.
"""

import re
import warnings
from datetime import datetime
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

BASE_DIR = Path(__file__).parent
ANIO_INICIO = 2018

MESES_NOMBRE = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SEPTIEMBRE": 9,
    "SETIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12,
    "ENE": 1,
    "FEB": 2,
    "MAR": 3,
    "ABR": 4,
    "JUN": 6,
    "JUL": 7,
    "AGO": 8,
    "SEP": 9,
    "SEPT": 9,
    "OCT": 10,
    "NOV": 11,
    "DIC": 12,
}

MESES_ORD = [
    "ENERO",
    "FEBRERO",
    "MARZO",
    "ABRIL",
    "MAYO",
    "JUNIO",
    "JULIO",
    "AGOSTO",
    "SEPTIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE",
]


def normalizar_texto(texto: str) -> str:
    t = str(texto).upper().strip()
    for a, b in [("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U")]:
        t = t.replace(a, b)
    return t.replace("ADMINITRATIVO", "ADMINISTRATIVO")


def es_administrativo_a(texto: str) -> bool:
    t = normalizar_texto(texto)
    return bool(
        re.search(r"ADMINISTRATIVO\s*A\b", t)
        or re.search(r"ADMINISTRACION\s*A\b", t)
    )


def es_fin_seccion_admin(texto: str) -> bool:
    t = normalizar_texto(texto)
    if es_administrativo_a(t):
        return False
    if re.search(r"ADMINISTRATIVO\s+[B-Z]\b", t):
        return True
    if re.search(r"CAJERO|VENDEDOR|MAESTRANZA|AUXILIAR|CHOFER", t):
        return True
    return False


def limpiar_numero(val) -> float | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    if isinstance(val, (int, float)):
        v = float(val)
        return v if v > 500 else None
    s = str(val).strip()
    if not s or s.lower() == "nan":
        return None
    s = re.sub(r"[$\s]", "", s)
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    parts = s.split(".")
    if len(parts) > 2:
        s = "".join(parts[:-1]) + "." + parts[-1]
    try:
        v = float(s)
        return v if v > 500 else None
    except ValueError:
        return None


def anio_desde_nombre(nombre: str) -> int | None:
    nombre_u = nombre.upper()
    años = [int(y) for y in re.findall(r"20\d{2}", nombre_u)]
    if años:
        return años[0]
    # Años de 2 dígitos al final: "MAYO AGOSTO 21"
    m = re.search(r"\b(\d{2})\b", nombre_u)
    if m:
        return 2000 + int(m.group(1))
    return None


def anios_desde_nombre(nombre: str) -> list[int]:
    nombre_u = nombre.upper()
    años = [int(y) for y in re.findall(r"20\d{2}", nombre_u)]
    if años:
        return años
    m = re.search(r"\b(\d{2})\b", nombre_u)
    if m:
        return [2000 + int(m.group(1))]
    return []


def meses_desde_nombre(nombre: str) -> list[tuple[int, int]]:
    nombre_u = normalizar_texto(nombre)
    años = anios_desde_nombre(nombre)
    if not años:
        return []

    # Rango explícito: ENERO A MARZO, MAYO A AGOSTO, etc.
    for mes_nombre in MESES_ORD:
        patron = rf"{mes_nombre}\s+A\s+(\w+)"
        m = re.search(patron, nombre_u)
        if m:
            destino = m.group(1)
            for mes_fin_nombre, num_fin in MESES_NOMBRE.items():
                if len(mes_fin_nombre) >= 4 and destino.startswith(mes_fin_nombre[:4]):
                    ini = MESES_NOMBRE[mes_nombre]
                    if len(años) >= 2 and num_fin < ini:
                        return (
                            [(años[0], m) for m in range(ini, 13)]
                            + [(años[1], m) for m in range(1, num_fin + 1)]
                        )
                    return [(años[0], m) for m in range(ini, num_fin + 1)]

    # MAYO ... AGOSTO (sin "A" explícita)
    m = re.search(r"MAYO.*?AGOSTO", nombre_u)
    if m and años:
        return [(años[0], mes) for mes in [5, 6, 7, 8]]

    # JULIO ... OCTUBRE
    m = re.search(r"JULIO.*?OCTUBRE", nombre_u)
    if m and años:
        return [(años[0], mes) for mes in [7, 8, 9, 10]]

    # ENERO ... MARZO
    m = re.search(r"ENERO.*?MARZO", nombre_u)
    if m and años:
        return [(años[0], mes) for mes in [1, 2, 3]]

    # AGOSTO ... DICIEMBRE
    m = re.search(r"AGOSTO.*?DICIEMBRE", nombre_u)
    if m and años:
        return [(años[0], mes) for mes in [8, 9, 10, 11, 12]]

    # OCTUBRE ... DICIEMBRE
    m = re.search(r"OCTUBRE.*?DICIEMBRE", nombre_u)
    if m and años:
        return [(años[0], mes) for mes in [10, 11, 12]]

    # FEBRERO ... MARZO
    m = re.search(r"FEBRERO.*?MARZO", nombre_u)
    if m and años:
        return [(años[0], mes) for mes in [2, 3]]

    meses = []
    for mes_nombre, num in MESES_NOMBRE.items():
        if len(mes_nombre) >= 4 and re.search(rf"\b{mes_nombre}\b", nombre_u):
            meses.append(num)
    if meses:
        return [(años[0], m) for m in sorted(set(meses))]

    return []


def parse_meses_celda(val, anio_default: int | None) -> list[tuple[int, int]]:
    if isinstance(val, (pd.Timestamp, datetime)):
        return [(val.year, val.month)]

    if val is None or (isinstance(val, float) and pd.isna(val)):
        return []

    s = normalizar_texto(str(val))
    if "MES" in s and "ANO" not in s and "AÑO" not in s.replace("N", ""):
        pass

    # Mes simple: ENERO, Julio, abril
    for nombre, num in MESES_NOMBRE.items():
        if len(nombre) >= 3 and s == nombre:
            return [(anio_default, num)] if anio_default else []

    # Rangos: junio-julio-22, sept-oct/22, nov-dic-22
    nums = []
    for nombre, num in MESES_NOMBRE.items():
        if len(nombre) >= 3 and nombre in s:
            nums.append(num)
    año = anio_default
    ym = re.search(r"(\d{2})\b", s)
    if ym:
        año = 2000 + int(ym.group(1))
    if len(nums) >= 2:
        a, b = min(nums), max(nums)
        return [(año, m) for m in range(a, b + 1)] if año else []
    if len(nums) == 1 and año:
        return [(año, nums[0])]

    return []


def buscar_columna_basico(row) -> int:
    for j, val in enumerate(row):
        if pd.notna(val) and "BASICO" in normalizar_texto(str(val)):
            return j
    return 2


def hoja_tiene_admin(df: pd.DataFrame) -> bool:
    texto = normalizar_texto(" ".join(str(x) for x in df.values.flatten() if pd.notna(x)))
    return "ADMINISTRATIV" in texto or "ADMINITRATIV" in texto


def extraer_fila_horizontal_admin_a(row, header_row, anio: int, archivo: str) -> list[dict]:
    registros = []
    headers = [normalizar_texto(str(x)) if pd.notna(x) else "" for x in header_row.values]
    mes_por_col = {}
    for j, h in enumerate(headers):
        for nombre_mes, num in MESES_NOMBRE.items():
            if len(nombre_mes) >= 4 and nombre_mes in h and "BASICO" in h:
                mes_por_col[j] = num
    for col, mes in mes_por_col.items():
        basico = limpiar_numero(row.iloc[col])
        if basico:
            registros.append({"anio": anio, "mes": mes, "basico": basico, "archivo": archivo})
    return registros


def expandir_por_nombre_archivo(regs: list[dict], archivo: str) -> list[dict]:
    """Completa meses del nombre del archivo si falta alguno y el básico es único."""
    meses_archivo = meses_desde_nombre(archivo)
    if not meses_archivo or not regs:
        return regs

    basicos = {r["basico"] for r in regs}
    if len(basicos) != 1:
        return regs

    b = next(iter(basicos))
    pares_regs = {(r["anio"], r["mes"]) for r in regs}
    out = list(regs)
    for anio, mes in meses_archivo:
        if (anio, mes) not in pares_regs:
            out.append({"anio": anio, "mes": mes, "basico": b, "archivo": archivo})
    return out


def extraer_excel(path: Path) -> list[dict]:
    archivo = path.name
    anio_archivo = anio_desde_nombre(archivo)
    registros = []

    try:
        xl = pd.ExcelFile(path)
    except Exception as e:
        print(f"  [skip] {archivo}: {e}")
        return []

    for sheet in xl.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet, header=None)
        if df.empty or not hoja_tiene_admin(df):
            continue

        en_seccion_a = False
        col_basico = 2
        anio_seccion = anio_archivo
        header_horizontal = None
        ultimo_basico = None

        for i in range(len(df)):
            row = df.iloc[i]
            fila_txt = " ".join(str(x) for x in row.values if pd.notna(x))

            if es_administrativo_a(fila_txt):
                en_seccion_a = True
                col_basico = buscar_columna_basico(row) or 2
                años_fila = [int(y) for y in re.findall(r"20\d{2}", fila_txt)]
                if años_fila:
                    anio_seccion = años_fila[0]
                header_horizontal = None
                continue

            if en_seccion_a and es_fin_seccion_admin(fila_txt):
                en_seccion_a = False
                header_horizontal = None
                continue

            if not en_seccion_a:
                t = normalizar_texto(fila_txt)
                if "ADMINISTRATIVO" in t and "BASICO" in t and "ENERO" in t:
                    header_horizontal = row
                elif header_horizontal is not None:
                    c0 = str(row.iloc[0]).strip().strip('"').upper()
                    if c0 == "A":
                        registros.extend(
                            extraer_fila_horizontal_admin_a(
                                row, header_horizontal, anio_archivo or 2019, archivo
                            )
                        )
                        header_horizontal = None
                continue

            if pd.notna(row.iloc[0]) and "MES" in normalizar_texto(str(row.iloc[0])):
                años_h = [int(y) for y in re.findall(r"20\d{2}", str(row.iloc[0]))]
                if años_h:
                    anio_seccion = años_h[0]
                col_basico = buscar_columna_basico(row) or col_basico
                continue

            meses_celda = parse_meses_celda(row.iloc[0], anio_seccion or anio_archivo)
            if meses_celda:
                basico = limpiar_numero(row.iloc[col_basico])
                if basico and ultimo_basico and basico > ultimo_basico * 1.18:
                    # Celda con total (básico + no remunerativos) en lugar del básico
                    basico = ultimo_basico
                if basico:
                    ultimo_basico = basico
                    for anio, mes in meses_celda:
                        registros.append(
                            {"anio": anio, "mes": mes, "basico": basico, "archivo": archivo}
                        )
                elif ultimo_basico and meses_celda:
                    for anio, mes in meses_celda:
                        registros.append(
                            {
                                "anio": anio,
                                "mes": mes,
                                "basico": ultimo_basico,
                                "archivo": archivo,
                            }
                        )
                continue

        # Formato antiguo: bloque ADMINISTRATIVO + fila "A"
        en_admin_block = False
        for i in range(len(df)):
            row = df.iloc[i]
            fila_txt = " ".join(str(x) for x in row.values if pd.notna(x))
            t = normalizar_texto(fila_txt)
            if t.strip() == "ADMINISTRATIVO" or (
                "ADMINISTRATIVO" in t and "BASICO" not in t and len(t) < 25
            ):
                en_admin_block = True
                continue
            if en_admin_block:
                c0 = str(row.iloc[0]).strip().strip('"').upper()
                if c0 == "A":
                    basico = next(
                        (limpiar_numero(row.iloc[j]) for j in range(1, len(row)) if limpiar_numero(row.iloc[j])),
                        None,
                    )
                    meses_archivo = meses_desde_nombre(archivo)
                    if basico and meses_archivo:
                        for anio, mes in meses_archivo:
                            registros.append(
                                {"anio": anio, "mes": mes, "basico": basico, "archivo": archivo}
                            )
                    en_admin_block = False
                elif c0 in "BCDEF" or "ADMINIST" in t:
                    en_admin_block = False

    registros = expandir_por_nombre_archivo(registros, archivo)
    return registros


DATOS_MANUALES = [
    {"anio": 2018, "mes": 1, "basico": 18582.20, "archivo": "01.ESCALA SALARIAL PARA ENERO, FEBRERO Y MARZO DE 2018.pdf"},
    {"anio": 2018, "mes": 2, "basico": 18886.82, "archivo": "01.ESCALA SALARIAL PARA ENERO, FEBRERO Y MARZO DE 2018.pdf"},
    {"anio": 2018, "mes": 3, "basico": 19191.44, "archivo": "01.ESCALA SALARIAL PARA ENERO, FEBRERO Y MARZO DE 2018.pdf"},
    {"anio": 2018, "mes": 4, "basico": 21110.58, "archivo": "Escala ABRIL a JULIO 2018-47.jpg"},
    {"anio": 2018, "mes": 5, "basico": 21110.58, "archivo": "Escala ABRIL a JULIO 2018-47.jpg"},
    {"anio": 2018, "mes": 6, "basico": 21110.58, "archivo": "Escala ABRIL a JULIO 2018-47.jpg"},
    {"anio": 2018, "mes": 7, "basico": 21110.58, "archivo": "Escala ABRIL a JULIO 2018-47.jpg"},
]


def consolidar_mensual(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["prio"] = df["archivo"].str.len()
    df = df.sort_values(["anio", "mes", "prio"])
    mensual = (
        df.groupby(["anio", "mes"], as_index=False)
        .agg(basico=("basico", "last"), archivo=("archivo", "last"))
        .sort_values(["anio", "mes"])
    )
    mensual["fecha"] = pd.to_datetime(dict(year=mensual["anio"], month=mensual["mes"], day=1))
    mensual["trimestre"] = "Q" + ((mensual["mes"] - 1) // 3 + 1).astype(str)
    return mensual


def interpolar_huecos(df_mensual: pd.DataFrame) -> pd.DataFrame:
    """Completa meses faltantes con interpolación lineal entre valores conocidos."""
    df = df_mensual.sort_values("fecha").set_index("fecha")
    rango = pd.date_range(df.index.min(), df.index.max(), freq="MS")
    df = df.reindex(rango)

    df["interpolado"] = df["basico"].isna()
    df["basico"] = df["basico"].interpolate(method="linear").round(2)

    df["anio"] = df.index.year
    df["mes"] = df.index.month
    df["trimestre"] = "Q" + ((df["mes"] - 1) // 3 + 1).astype(str)
    df.loc[df["interpolado"], "archivo"] = "(interpolado)"

    return df.reset_index(names="fecha")


def main():
    todos = []

    for path in sorted(BASE_DIR.iterdir()):
        if path.suffix.lower() not in (".xls", ".xlsx"):
            continue
        if path.name.startswith("_") or path.name.startswith("dataset"):
            continue
        regs = extraer_excel(path)
        if regs:
            print(f"OK {path.name}: {len(regs)} registros")
        todos.extend(regs)

    todos.extend(DATOS_MANUALES)

    df = pd.DataFrame(todos)
    df = df[(df["anio"] > ANIO_INICIO) | ((df["anio"] == ANIO_INICIO) & (df["mes"] >= 1))].copy()
    df_mensual = consolidar_mensual(df)
    n_antes = len(df_mensual)
    df_mensual = interpolar_huecos(df_mensual)
    n_interp = int(df_mensual["interpolado"].sum())

    df_trimestral = (
        df_mensual.groupby(["anio", "trimestre"], as_index=False)
        .agg(
            basico_promedio=("basico", "mean"),
            meses_incluidos=("mes", lambda x: sorted(x.tolist())),
            n_meses=("mes", "count"),
        )
        .sort_values(["anio", "trimestre"])
    )
    df_trimestral["basico_promedio"] = df_trimestral["basico_promedio"].round(2)

    out_mensual = BASE_DIR / "dataset_mensual_administrativo_a.csv"
    out_trimestral = BASE_DIR / "dataset_trimestral_administrativo_a.csv"

    df_mensual[
        ["anio", "mes", "fecha", "trimestre", "basico", "interpolado", "archivo"]
    ].to_csv(out_mensual, index=False, encoding="utf-8-sig")
    df_trimestral.to_csv(out_trimestral, index=False, encoding="utf-8-sig")

    print(f"\n=== RESUMEN ===")
    print(f"Mensual: {len(df_mensual)} filas ({n_antes} reales + {n_interp} interpolados) -> {out_mensual.name}")
    print(f"Trimestral: {len(df_trimestral)} filas -> {out_trimestral.name}")
    print(f"Rango: {df_mensual['fecha'].min().date()} a {df_mensual['fecha'].max().date()}")

    if n_interp:
        print(f"\nMeses interpolados ({n_interp}):")
        interp = df_mensual[df_mensual["interpolado"]]
        for _, row in interp.iterrows():
            print(f"  - {row['fecha'].strftime('%Y-%m')}: ${row['basico']:,.2f}")


if __name__ == "__main__":
    main()
