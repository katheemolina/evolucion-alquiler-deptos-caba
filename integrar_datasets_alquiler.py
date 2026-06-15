# -*- coding: utf-8 -*-
"""
Integración de datasets del mercado de alquiler de departamentos — CABA
Trabajo Final Integrador — Calidad y Visualización de Datos

Este script lee 7 archivos Excel del IDECBA/GCBA (datos Argenprop), una tabla
auxiliar barrio↔comuna, series de sueldo básico Administrativo A (SEC La Plata)
y construye:
  - dataset_maestro.csv      → comuna × trimestre × ambientes (+ ratios alquiler/sueldo)
  - dataset_barrios_mensual.csv → barrio × mes × ambientes (+ sueldo mensual de contexto)

Requisitos: pandas, openpyxl
Ejecución: python integrar_datasets_alquiler.py
"""

from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

# Directorio base = carpeta donde está este script (rutas relativas, sin rutas absolutas)
BASE_DIR = Path(__file__).resolve().parent

# Corte temporal del dataset maestro: los precios (Grupo A) comienzan en 2018-Q1.
# Filas anteriores solo tenían superficie agregada y elevaban el % de faltantes sin aportar al análisis.
PERIODO_INICIO_MAESTRO = "2018-Q1"

# Archivos CSV de sueldo básico Administrativo A (Empleados de Comercio — SEC La Plata)
ARCHIVO_SUELDO_TRIMESTRAL = "dataset_trimestral_administrativo_a.csv"
ARCHIVO_SUELDO_MENSUAL = "dataset_mensual_administrativo_a.csv"


# =============================================================================
# UTILIDADES GENERALES
# =============================================================================

def encontrar_archivo(prefijo: str, extension: str = ".xlsx") -> Path:
    """
    Localiza un archivo en BASE_DIR cuyo nombre comience con `prefijo`.
    Útil porque los nombres completos del GCBA son muy largos y pueden variar.
    """
    coincidencias = sorted(
        p for p in BASE_DIR.iterdir()
        if p.is_file() and p.name.startswith(prefijo) and p.suffix.lower() == extension
    )
    if not coincidencias:
        raise FileNotFoundError(
            f"No se encontró ningún archivo que comience con '{prefijo}' en {BASE_DIR}"
        )
    if len(coincidencias) > 1:
        # Si hay más de uno, tomar el primero alfabéticamente y avisar
        print(f"[AVISO] Múltiples archivos con prefijo '{prefijo}'; se usa: {coincidencias[0].name}")
    return coincidencias[0]


def quitar_acentos(texto: str) -> str:
    """Elimina diacríticos para comparar nombres de barrios de forma insensible a tildes."""
    texto_norm = unicodedata.normalize("NFKD", str(texto))
    return texto_norm.encode("ascii", "ignore").decode("ascii")


def es_valor_faltante_gcba(valor) -> bool:
    """
    Problema de calidad #1: en precios, '///' indica dato no disponible
    (muestra insuficiente de publicaciones en esa comuna/período).
  """
    if pd.isna(valor):
        return True
    return str(valor).strip() == "///"


def es_fila_nota(valor) -> bool:
    """Detecta filas de notas al pie, fuente o aclaraciones al final de las planillas."""
    if pd.isna(valor):
        return False
    texto = str(valor).strip()
    prefijos_nota = ("*", "Nota", "Fuente", "Las series", "/// Dato", "Solo se muestran")
    return any(texto.startswith(p) for p in prefijos_nota)


# Mapeo de abreviaturas de mes (Grupo B — superficie por barrio)
MESES_ABREVIADOS = {
    "Ene.": 1, "Feb.": 2, "Mar.": 3, "Abr.": 4, "May.": 5, "Jun.": 6,
    "Jul.": 7, "Ago.": 8, "Sep.": 9, "Oct.": 10, "Nov.": 11, "Dic.": 12,
}

# Mapeo de meses completos (archivo 07 — superficie promedio)
MESES_COMPLETOS = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
    "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12,
}

# Mapeo de trimestre textual → número (Grupo A — precios por comuna)
TRIMESTRE_A_NUM = {
    "1er. trim.": 1, "2do. trim.": 2, "3er. trim.": 3, "4to. trim.": 4,
}

# Alias entre nomenclaturas distintas entre archivos de superficie y tabla GCBA
# Problema de calidad #7: variaciones de nombres (ej. Montserrat vs Monserrat)
ALIAS_BARRIOS = {
    "LA PATERNAL": "PATERNAL",
    "MONTSERRAT": "MONSERRAT",
}


def corregir_encoding_barrio(nombre: str) -> str:
    """
    Problema de calidad #2: encoding roto en barrios/comunas.
    En la tabla auxiliar, 'NÚÑEZ' puede aparecer como 'NUÃ'EZ' (UTF-8 mal interpretado).
    En archivos de superficie, los caracteres acentuados pueden verse corruptos en consola
    pero conservan códigos Latin-1 válidos; unificamos casos conocidos de Núñez.
    """
    nombre = str(nombre).strip()
    # Patrón roto documentado en exploración previa
    if re.search(r"NU.{0,3}EZ", nombre.upper()) and nombre.upper() not in ("NUEVA POMPEYA",):
        return "Núñez"
    return nombre


def clave_barrio(nombre: str) -> str:
    """
    Genera una clave canónica para cruzar barrios entre fuentes.
    Problema de calidad #7: normalización (strip, corrección encoding, sin acentos, alias).
    """
    nombre = corregir_encoding_barrio(nombre)
    clave = quitar_acentos(nombre).upper()
    return ALIAS_BARRIOS.get(clave, clave)


def nombre_barrio_presentacion(nombre: str) -> str:
    """Formato legible tipo Title Case, coherente con los archivos del Grupo B."""
    nombre = corregir_encoding_barrio(nombre)
    return nombre.strip().title()


def reconstruir_encabezados_temporales(
    df_raw: pd.DataFrame,
    fila_anios: int = 1,
    fila_subperiodo: int = 2,
    col_inicio: int = 1,
) -> list[dict]:
    """
    Reconstruye metadatos temporales a partir de filas con años mergeados y
  subperíodos (trimestres o meses) repetidos debajo de cada año.

    Retorna una lista de dicts con las claves del encabezado de cada columna de datos.
    """
    años = df_raw.iloc[fila_anios, col_inicio:].ffill()
    subperiodos = df_raw.iloc[fila_subperiodo, col_inicio:]
    encabezados = []
    for año, sub in zip(años, subperiodos):
        encabezados.append({"anio": int(año) if not pd.isna(año) else None, "subperiodo": sub})
    return encabezados


def parsear_trimestre(texto_trimestre) -> tuple[str | None, bool]:
    """
    Convierte '2do. trim.*' → ('2018-Q2', provisorio=True).
    Problema de calidad #3: asterisco (*) al final = dato provisorio.
    """
    if pd.isna(texto_trimestre):
        return None, False
    texto = str(texto_trimestre).strip()
    provisorio = "*" in texto
    texto_limpio = texto.replace("*", "").strip()
    num = TRIMESTRE_A_NUM.get(texto_limpio)
    if num is None:
        return None, provisorio
    return f"Q{num}", provisorio


def parsear_mes_abreviado(texto_mes) -> tuple[int | None, bool]:
    """Convierte 'Jul.' o 'Marzo*' → (7, provisorio)."""
    if pd.isna(texto_mes):
        return None, False
    texto = str(texto_mes).strip()
    provisorio = "*" in texto
    texto_limpio = texto.replace("*", "").strip()
    mes = MESES_ABREVIADOS.get(texto_limpio)
    if mes is None:
        # Intentar con mes completo por si aparece en otras planillas
        mes = MESES_COMPLETOS.get(texto_limpio)
    return mes, provisorio


def parsear_mes_completo(texto_mes) -> tuple[int | None, bool]:
    """Convierte 'Marzo' o 'Abril*' → (3, provisorio) para el archivo 07."""
    if pd.isna(texto_mes):
        return None, False
    texto = str(texto_mes).strip()
    provisorio = "*" in texto
    texto_limpio = texto.replace("*", "").strip()
    return MESES_COMPLETOS.get(texto_limpio), provisorio


def periodo_mensual(anio: int, mes: int) -> str:
    """Formato YYYY-MM con mes de dos dígitos."""
    return f"{anio}-{mes:02d}"


def trimestre_desde_mes(mes: int) -> int:
    """Asigna trimestre calendario: meses 01-03→Q1, 04-06→Q2, 07-09→Q3, 10-12→Q4."""
    return (mes - 1) // 3 + 1


def periodo_trim_a_orden(periodo_trim: str) -> tuple[int, int]:
    """Convierte '2018-Q1' en tupla ordenable (anio, trimestre) para comparar períodos."""
    anio_str, trim_str = str(periodo_trim).split("-Q")
    return int(anio_str), int(trim_str)


def filtrar_maestro_desde_periodo(
    df: pd.DataFrame,
    periodo_min: str = PERIODO_INICIO_MAESTRO,
) -> pd.DataFrame:
    """
    Recorta el dataset maestro desde el primer trimestre con precios en la fuente.

    Motivo: el join outer incluía 2013-2017 solo con superficie (precio siempre NaN).
    Eso generaba ~37 % de filas sin precio que no son útiles para el análisis integrado.
    """
    corte = periodo_trim_a_orden(periodo_min)
    mascara = df["periodo_trim"].apply(lambda p: periodo_trim_a_orden(p) >= corte)
    return df[mascara].reset_index(drop=True)


# =============================================================================
# PASO 1: LEER Y TRANSFORMAR GRUPO A (PRECIOS POR COMUNA, TRIMESTRAL)
# =============================================================================

def leer_precios_comuna(archivo: Path, ambientes: int) -> pd.DataFrame:
    """
    Lee un archivo de precio promedio por comuna y lo transforma a formato long.

    Columnas resultantes:
      comuna, periodo, ambientes, precio_promedio_pesos, provisorio
    """
    # Leer planilla completa sin encabezado automático (estructura fija del GCBA)
    df_raw = pd.read_excel(archivo, sheet_name=0, header=None)

    # Reconstruir encabezados temporales (años en fila 1, trimestres en fila 2)
    encabezados = reconstruir_encabezados_temporales(df_raw)

    registros = []
    # Datos desde fila 3; primera columna = comuna
    for idx in range(3, len(df_raw)):
        comuna_val = df_raw.iloc[idx, 0]
        if es_fila_nota(comuna_val):
            break
        if pd.isna(comuna_val):
            continue
        # Excluir fila agregada "Total" — solo comunas 1 a 15
        try:
            comuna = int(comuna_val)
        except (ValueError, TypeError):
            continue
        if comuna < 1 or comuna > 15:
            continue

        # Recorrer cada columna de período
        for col_offset, meta in enumerate(encabezados):
            col_idx = col_offset + 1
            valor = df_raw.iloc[idx, col_idx]
            sufijo_q, prov_col = parsear_trimestre(meta["subperiodo"])
            if meta["anio"] is None or sufijo_q is None:
                continue
            periodo = f"{meta['anio']}-{sufijo_q}"

            # Problema de calidad #1: '///' → NaN
            if es_valor_faltante_gcba(valor):
                precio = np.nan
            else:
                precio = pd.to_numeric(valor, errors="coerce")

            registros.append({
                "comuna": comuna,
                "periodo": periodo,
                "ambientes": ambientes,
                "precio_promedio_pesos": precio,
                "provisorio": prov_col,
            })

    return pd.DataFrame(registros)


def cargar_grupo_precios() -> pd.DataFrame:
    """Apila los 3 archivos de precios (1, 2 y 3 ambientes)."""
    configuracion = [
        ("13_", 1),
        ("12_", 2),
        ("11_", 3),
    ]
    partes = []
    for prefijo, amb in configuracion:
        archivo = encontrar_archivo(prefijo)
        print(f"[Paso 1] Leyendo precios ({amb} ambiente/s): {archivo.name}")
        partes.append(leer_precios_comuna(archivo, amb))
    df_precios = pd.concat(partes, ignore_index=True)
    return df_precios


# =============================================================================
# PASO 2: LEER Y TRANSFORMAR GRUPO B (SUPERFICIE TOTAL POR BARRIO, MENSUAL)
# =============================================================================

def leer_superficie_barrio(archivo: Path, ambientes: int) -> pd.DataFrame:
    """
    Lee superficie total (m²) publicada en alquiler por barrio → formato long.

    Columnas resultantes:
      barrio, periodo, ambientes, superficie_total_m2
    """
    df_raw = pd.read_excel(archivo, sheet_name=0, header=None)
    encabezados = reconstruir_encabezados_temporales(df_raw)

    registros = []
    for idx in range(3, len(df_raw)):
        barrio_val = df_raw.iloc[idx, 0]
        if es_fila_nota(barrio_val):
            break
        if pd.isna(barrio_val):
            continue
        barrio_str = str(barrio_val).strip()
        if barrio_str == "Total":
            continue

        barrio = nombre_barrio_presentacion(barrio_str)

        for col_offset, meta in enumerate(encabezados):
            col_idx = col_offset + 1
            valor = df_raw.iloc[idx, col_idx]
            mes, _ = parsear_mes_abreviado(meta["subperiodo"])
            if meta["anio"] is None or mes is None:
                continue
            periodo = periodo_mensual(meta["anio"], mes)
            superficie = pd.to_numeric(valor, errors="coerce")

            registros.append({
                "barrio": barrio,
                "periodo": periodo,
                "ambientes": ambientes,
                "superficie_total_m2": superficie,
            })

    return pd.DataFrame(registros)


def cargar_grupo_superficie() -> pd.DataFrame:
    """Apila los 3 archivos de superficie total por barrio."""
    configuracion = [
        ("04_", 1),
        ("02_", 2),
        ("03_", 3),
    ]
    partes = []
    for prefijo, amb in configuracion:
        archivo = encontrar_archivo(prefijo)
        print(f"[Paso 2] Leyendo superficie por barrio ({amb} ambiente/s): {archivo.name}")
        partes.append(leer_superficie_barrio(archivo, amb))
    return pd.concat(partes, ignore_index=True)


# =============================================================================
# PASO 3: LEER SUPERFICIE PROMEDIO (CIUDAD, MENSUAL)
# =============================================================================

def leer_superficie_promedio(archivo: Path) -> pd.DataFrame:
    """
    Lee el archivo 07 (ya casi en formato tabular) y lo pasa a long.

    Columnas resultantes:
      periodo, ambientes, superficie_promedio_m2, provisorio
    """
    df_raw = pd.read_excel(archivo, sheet_name=0, header=None)

    anio_actual = None
    registros = []

    # Datos desde fila 3; col0=año (con forward-fill implícito), col1=mes, cols 2-4=ambientes
    for idx in range(3, len(df_raw)):
        fila0 = df_raw.iloc[idx, 0]
        fila1 = df_raw.iloc[idx, 1]

        if es_fila_nota(fila0) or es_fila_nota(fila1):
            break

        if not pd.isna(fila0):
            try:
                anio_actual = int(fila0)
            except (ValueError, TypeError):
                pass

        if anio_actual is None or pd.isna(fila1):
            continue

        mes, provisorio = parsear_mes_completo(fila1)
        if mes is None:
            continue

        periodo = periodo_mensual(anio_actual, mes)

        for amb in (1, 2, 3):
            valor = df_raw.iloc[idx, amb + 1]  # columnas 2, 3, 4
            registros.append({
                "periodo": periodo,
                "ambientes": amb,
                "superficie_promedio_m2": pd.to_numeric(valor, errors="coerce"),
                "provisorio": provisorio,
            })

    return pd.DataFrame(registros)


# =============================================================================
# PASO 4: LEER Y LIMPIAR TABLA BARRIOS ↔ COMUNAS
# =============================================================================

def leer_barrios_comunas(archivo: Path) -> tuple[pd.DataFrame, list[str]]:
    """
    Lee la tabla de equivalencia y devuelve el DataFrame limpio más la lista de
    barrios del Grupo B que no encontraron match (problema de calidad documentado).
    """
    df = pd.read_excel(archivo, sheet_name=0)
    df = df.rename(columns={df.columns[0]: "barrio_raw", df.columns[1]: "comuna"})
    df["barrio_raw"] = df["barrio_raw"].astype(str)

    # Problema de calidad #2: corregir NUÃ'EZ → Núñez y normalizar
    df["barrio"] = df["barrio_raw"].apply(
        lambda x: nombre_barrio_presentacion(corregir_encoding_barrio(x))
    )
    df["clave_barrio"] = df["barrio_raw"].apply(clave_barrio)
    df["comuna"] = pd.to_numeric(df["comuna"], errors="coerce").astype("Int64")

    return df[["barrio", "clave_barrio", "comuna"]]


def aplicar_nombres_canonicos_barrio(
    df_superficie: pd.DataFrame,
    df_equiv: pd.DataFrame,
) -> pd.DataFrame:
    """
    Unifica nombres de barrio usando la tabla de equivalencia como referencia.
    Problema de calidad #7: el mismo barrio puede figurar como 'Agronomia' en un
    archivo y 'Agronomía' en otro; la clave sin acentos permite asignar un único nombre.
    """
    mapa_canonico = df_equiv.set_index("clave_barrio")["barrio"].to_dict()
    df = df_superficie.copy()
    df["barrio"] = df["barrio"].apply(
        lambda x: mapa_canonico.get(clave_barrio(x), nombre_barrio_presentacion(x))
    )
    return df


def auditar_barrios_sin_match(
    df_superficie: pd.DataFrame,
    df_equiv: pd.DataFrame,
) -> list[str]:
    """
    Compara barrios únicos del Grupo B contra la tabla de equivalencia.
    Reporta los que no matchean tras normalización.
    """
    claves_equiv = set(df_equiv["clave_barrio"])
    barrios_unicos = df_superficie["barrio"].unique()
    sin_match = []
    for barrio in barrios_unicos:
        clave = clave_barrio(barrio)
        if clave not in claves_equiv:
            sin_match.append(barrio)
    return sorted(sin_match)


# =============================================================================
# PASO 5: CANTIDAD ESTIMADA DE DEPARTAMENTOS (VARIABLE DERIVADA)
# =============================================================================

def calcular_cantidad_estimada(
    df_superficie: pd.DataFrame,
    df_promedio: pd.DataFrame,
) -> pd.DataFrame:
    """
    Une superficie total (barrio, mensual) con superficie promedio (ciudad, mensual)
    y calcula cantidad_deptos_estimada = superficie_total_m2 / superficie_promedio_m2.

    SUPUESTO EXPLÍCITO (problema de calidad #6):
    La superficie promedio se publica solo a nivel ciudad (sin desagregación geográfica).
    Al dividir superficie de cada barrio por el promedio urbano, asumimos que la
    distribución de tamaños es homogénea entre barrios. Es una aproximación necesaria
    para estimar volumen de oferta cuando no hay conteo directo de unidades.
    """
    df_prom = df_promedio[["periodo", "ambientes", "superficie_promedio_m2"]].copy()
    df_join = df_superficie.merge(df_prom, on=["periodo", "ambientes"], how="left")
    df_join["cantidad_deptos_estimada"] = (
        df_join["superficie_total_m2"] / df_join["superficie_promedio_m2"]
    )
    return df_join


# =============================================================================
# PASO 6: CONSTRUIR DATASET MAESTRO (CRUCE COMUNA-TRIMESTRE + BARRIO-MES)
# =============================================================================

def preparar_superficie_con_comuna_y_trimestre(
    df_barrios_mensual: pd.DataFrame,
    df_equiv: pd.DataFrame,
) -> pd.DataFrame:
    """
    Agrega comuna a cada barrio y deriva columnas de agregación trimestral.

    Problema de calidad #4: precios están por comuna, superficie por barrio
    → resolvemos con join barrio→comuna y luego sumamos a nivel comuna.

    Problema de calidad #5: precios trimestrales, superficie mensual
    → derivamos periodo_trim (YYYY-QN) desde el mes para alinear granularidades.
    """
    mapa_comuna = df_equiv.set_index("clave_barrio")["comuna"].to_dict()
    df = df_barrios_mensual.copy()
    df["clave_barrio"] = df["barrio"].apply(clave_barrio)
    df["comuna"] = df["clave_barrio"].map(mapa_comuna)

    # Extraer año y mes del periodo YYYY-MM
    partes = df["periodo"].str.split("-", expand=True)
    df["anio"] = partes[0].astype(int)
    df["mes"] = partes[1].astype(int)
    df["trimestre"] = df["mes"].apply(trimestre_desde_mes)
    df["periodo_trim"] = df["anio"].astype(str) + "-Q" + df["trimestre"].astype(str)

    return df


def agregar_superficie_a_comuna_trimestre(df: pd.DataFrame) -> pd.DataFrame:
    """
    Suma superficie total y cantidad estimada de deptos por comuna × trimestre × ambientes.
    """
    agg = (
        df.groupby(["comuna", "periodo_trim", "ambientes"], as_index=False)
        .agg(
            superficie_total_m2=("superficie_total_m2", "sum"),
            cantidad_deptos_estimada=("cantidad_deptos_estimada", "sum"),
        )
    )
    return agg


def construir_dataset_maestro(
    df_precios: pd.DataFrame,
    df_superficie_comuna: pd.DataFrame,
) -> pd.DataFrame:
    """
    Join final por comuna, periodo_trim y ambientes.
    Si no hay match, se conservan filas con NaN (no se eliminan).
    """
    df_precios = df_precios.rename(columns={"periodo": "periodo_trim"})
    maestro = df_precios.merge(
        df_superficie_comuna,
        on=["comuna", "periodo_trim", "ambientes"],
        how="outer",
    )
    # Orden lógico de columnas para el entregable
    columnas = [
        "comuna",
        "periodo_trim",
        "ambientes",
        "precio_promedio_pesos",
        "provisorio",
        "superficie_total_m2",
        "cantidad_deptos_estimada",
    ]
    return maestro[columnas].sort_values(["comuna", "periodo_trim", "ambientes"]).reset_index(drop=True)


# =============================================================================
# PASO 7: INTEGRAR SUELDOS ADMINISTRATIVO A (EMPLEADOS DE COMERCIO)
# =============================================================================

def leer_sueldos_trimestral(archivo: Path) -> pd.DataFrame:
    """
    Lee el dataset trimestral de sueldo básico Administrativo A (SEC La Plata).

    Fuente documentada en DOCUMENTACION_DATASETS.md.
    Se usa para alinear con el maestro de alquileres (misma granularidad trimestral).
    """
    df = pd.read_csv(archivo)
    df["periodo_trim"] = df["anio"].astype(str) + "-" + df["trimestre"].astype(str)
    df = df.rename(columns={
        "basico_promedio": "sueldo_basico_admin_a",
        "n_meses": "n_meses_sueldo",
    })
    return df[["periodo_trim", "sueldo_basico_admin_a", "n_meses_sueldo"]]


def leer_sueldos_mensual(archivo: Path) -> pd.DataFrame:
    """
    Lee el dataset mensual de sueldo básico Administrativo A.

    Permite enriquecer el dataset barrios mensual con contexto salarial mes a mes.
    """
    df = pd.read_csv(archivo)
    df["periodo"] = (
        df["anio"].astype(str) + "-" + df["mes"].astype(int).astype(str).str.zfill(2)
    )
    df = df.rename(columns={
        "basico": "sueldo_basico_admin_a",
        "interpolado": "sueldo_interpolado",
    })
    return df[["periodo", "sueldo_basico_admin_a", "sueldo_interpolado"]]


def calcular_indicadores_alquiler_sueldo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores de asequibilidad: alquiler vs. sueldo básico de comercio.

    Variables derivadas (supuesto explícito):
      - ratio_alquiler_sueldo_pct: % del sueldo básico que representa el alquiler publicado.
      - meses_sueldo_para_alquiler: cuántos sueldos básicos equivalen al alquiler del período.

    El sueldo es un PROXY sectorial (Administrativo A, SEC La Plata), no el ingreso real
    de cada inquilino ni desagregado por comuna. Sirve para comparar evolución relativa
    y accesibilidad aproximada entre comunas (numerador variable, denominador común).
    """
    df = df.copy()
    sueldo = df["sueldo_basico_admin_a"]
    precio = df["precio_promedio_pesos"]

    df["ratio_alquiler_sueldo_pct"] = np.where(
        sueldo.notna() & precio.notna() & (sueldo > 0),
        (precio / sueldo) * 100,
        np.nan,
    )
    df["meses_sueldo_para_alquiler"] = np.where(
        sueldo.notna() & precio.notna() & (sueldo > 0),
        precio / sueldo,
        np.nan,
    )
    return df


def integrar_sueldos_en_maestro(
    df_maestro: pd.DataFrame,
    df_sueldos_trim: pd.DataFrame,
) -> pd.DataFrame:
    """
    Join del maestro con sueldos trimestrales por periodo_trim.
    Join left: se conservan filas de alquiler aunque falte sueldo (NaN + reporte).
    """
    df = df_maestro.merge(df_sueldos_trim, on="periodo_trim", how="left")
    df = calcular_indicadores_alquiler_sueldo(df)
    columnas = [
        "comuna",
        "periodo_trim",
        "ambientes",
        "precio_promedio_pesos",
        "provisorio",
        "sueldo_basico_admin_a",
        "n_meses_sueldo",
        "ratio_alquiler_sueldo_pct",
        "meses_sueldo_para_alquiler",
        "superficie_total_m2",
        "cantidad_deptos_estimada",
    ]
    return df[columnas]


def integrar_sueldos_en_barrios_mensual(
    df_barrios: pd.DataFrame,
    df_sueldos_mensual: pd.DataFrame,
) -> pd.DataFrame:
    """
    Agrega sueldo mensual al dataset barrios para análisis de contexto y series duales.
    No calcula ratio de alquiler aquí porque este dataset no incluye precios por barrio.
    """
    return df_barrios.merge(df_sueldos_mensual, on="periodo", how="left")


# =============================================================================
# PASO 8: EXPORTAR Y REPORTAR CALIDAD
# =============================================================================

def reportar_calidad(
    df_maestro: pd.DataFrame,
    df_barrios_mensual: pd.DataFrame,
    barrios_sin_match: list[str],
) -> None:
    """Imprime métricas de calidad para documentar en el informe académico."""
    sep = "=" * 70
    print(f"\n{sep}")
    print("REPORTE DE CALIDAD - DATASET MAESTRO ALQUILER CABA")
    print(sep)

    print(f"\nShape del dataset maestro: {df_maestro.shape}")
    print(f"Shape del dataset barrios mensual: {df_barrios_mensual.shape}")

    print("\n--- % de valores faltantes (NaN) por columna - dataset maestro ---")
    for col in df_maestro.columns:
        pct = df_maestro[col].isna().mean() * 100
        print(f"  {col}: {pct:.2f}%")

    if "periodo_trim" in df_maestro.columns:
        periodos = df_maestro["periodo_trim"].dropna().unique()
        print(f"\nRango temporal (trimestral): {min(periodos)} a {max(periodos)}")

    print(f"\nComunas únicas: {df_maestro['comuna'].nunique()}")

    sin_precio = df_maestro["precio_promedio_pesos"].isna().sum()
    total = len(df_maestro)
    print(
        f"\nCombinaciones sin precio (NaN, origen '///' o sin match): "
        f"{sin_precio} de {total} ({100 * sin_precio / total:.2f}%)"
    )

    filas_sin_superficie = df_maestro["superficie_total_m2"].isna().sum()
    print(
        f"Combinaciones sin superficie agregada: "
        f"{filas_sin_superficie} de {total} ({100 * filas_sin_superficie / total:.2f}%)"
    )

    if "sueldo_basico_admin_a" in df_maestro.columns:
        sin_sueldo = df_maestro["sueldo_basico_admin_a"].isna().sum()
        print(
            f"\nCombinaciones sin sueldo de referencia: "
            f"{sin_sueldo} de {total} ({100 * sin_sueldo / total:.2f}%)"
        )
        mono = df_maestro[df_maestro["ambientes"] == 1]["ratio_alquiler_sueldo_pct"].dropna()
        if len(mono) > 0:
            print(
                f"Ratio alquiler/sueldo (monoambiente): "
                f"mediana={mono.median():.1f}%, media={mono.mean():.1f}%, "
                f"max={mono.max():.1f}%"
            )

    if "sueldo_basico_admin_a" in df_barrios_mensual.columns:
        interp = df_barrios_mensual["sueldo_interpolado"].fillna(False).astype(bool).sum()
        print(
            f"\nRegistros barrios mensual con sueldo interpolado: "
            f"{interp} ({100 * interp / len(df_barrios_mensual):.1f}%)"
        )

    print("\n--- Barrios del Grupo B sin match en tabla de equivalencia ---")
    if barrios_sin_match:
        for b in barrios_sin_match:
            print(f"  - {b}")
    else:
        print("  (ninguno - todos los barrios fueron mapeados tras normalizacion)")

    print(f"\n{sep}\n")


def main() -> None:
    """Orquesta los 7 pasos de integración de principio a fin."""

    print("Inicio de integracion - Mercado de alquiler CABA")
    print(f"Directorio de trabajo: {BASE_DIR}\n")

    # --- PASO 1 ---
    print("# === PASO 1: Precios por comuna (Grupo A) ===")
    df_precios = cargar_grupo_precios()
    print(f"  Registros precios: {len(df_precios)}")

    # --- PASO 2 ---
    print("\n# === PASO 2: Superficie total por barrio (Grupo B) ===")
    df_superficie = cargar_grupo_superficie()
    print(f"  Registros superficie barrio: {len(df_superficie)}")

    # --- PASO 3 ---
    print("\n# === PASO 3: Superficie promedio ciudad ===")
    archivo_prom = encontrar_archivo("07_")
    df_promedio = leer_superficie_promedio(archivo_prom)
    print(f"  Registros superficie promedio: {len(df_promedio)}")

    # --- PASO 4 ---
    print("\n# === PASO 4: Tabla barrios <-> comunas ===")
    archivo_equiv = encontrar_archivo("barrios_comunas")
    df_equiv = leer_barrios_comunas(archivo_equiv)

    # Unificar nombres de barrio antes de auditar y cruzar
    df_superficie = aplicar_nombres_canonicos_barrio(df_superficie, df_equiv)
    barrios_sin_match = auditar_barrios_sin_match(df_superficie, df_equiv)
    print(f"  Barrios en tabla equivalencia: {len(df_equiv)}")
    print(f"  Barrios sin match: {len(barrios_sin_match)}")

    # --- PASO 5 ---
    print("\n# === PASO 5: Cantidad estimada de departamentos ===")
    df_barrios_mensual = calcular_cantidad_estimada(df_superficie, df_promedio)
    print(f"  Registros barrios mensual (con estimación): {len(df_barrios_mensual)}")

    # --- PASO 6 ---
    print("\n# === PASO 6: Dataset maestro (comuna x trimestre) ===")
    df_con_comuna = preparar_superficie_con_comuna_y_trimestre(df_barrios_mensual, df_equiv)
    df_superficie_comuna = agregar_superficie_a_comuna_trimestre(df_con_comuna)
    df_maestro = construir_dataset_maestro(df_precios, df_superficie_comuna)
    registros_antes = len(df_maestro)
    df_maestro = filtrar_maestro_desde_periodo(df_maestro, PERIODO_INICIO_MAESTRO)
    print(f"  Registros maestro (total join): {registros_antes}")
    print(f"  Registros maestro (desde {PERIODO_INICIO_MAESTRO}): {len(df_maestro)}")

    # --- PASO 7 ---
    print("\n# === PASO 7: Sueldos Administrativo A (Empleados de Comercio) ===")
    archivo_sueldo_trim = BASE_DIR / ARCHIVO_SUELDO_TRIMESTRAL
    archivo_sueldo_mensual = BASE_DIR / ARCHIVO_SUELDO_MENSUAL
    df_sueldos_trim = leer_sueldos_trimestral(archivo_sueldo_trim)
    df_sueldos_mensual = leer_sueldos_mensual(archivo_sueldo_mensual)
    print(f"  Trimestres de sueldo: {len(df_sueldos_trim)}")
    print(f"  Meses de sueldo: {len(df_sueldos_mensual)}")

    df_maestro = integrar_sueldos_en_maestro(df_maestro, df_sueldos_trim)
    df_barrios_mensual = integrar_sueldos_en_barrios_mensual(df_barrios_mensual, df_sueldos_mensual)
    print(f"  Maestro con indicadores alquiler/sueldo: {len(df_maestro)} filas")

    # --- PASO 8 ---
    print("\n# === PASO 8: Exportacion y reporte ===")
    salida_maestro = BASE_DIR / "dataset_maestro.csv"
    salida_barrios = BASE_DIR / "dataset_barrios_mensual.csv"

    df_maestro.to_csv(salida_maestro, index=False, encoding="utf-8")
    df_barrios_mensual.to_csv(salida_barrios, index=False, encoding="utf-8")

    print(f"  Exportado: {salida_maestro.name}")
    print(f"  Exportado: {salida_barrios.name}")

    reportar_calidad(df_maestro, df_barrios_mensual, barrios_sin_match)
    print("Integración finalizada correctamente.")


if __name__ == "__main__":
    main()
