# -*- coding: utf-8 -*-
"""
Generación de visualizaciones para el TFI — Mercado de alquiler de departamentos en CABA
Calidad y Visualización de Datos.

Cada gráfico responde a una de las 3 preguntas de análisis (punto 5 del informe)
y aplica los principios de "Datos que cuentan historias" (Knaflic / GICS-UNNE):
título de acción, decluttering, color para enfocar la atención, paleta apta para
daltónicos y etiquetado directo.

Entrada : dataset_maestro.csv (en la misma carpeta)
Salida  : grafico_1_precios.png, grafico_2_oferta_precio.png,
          grafico_3_mapa_burbujas.png, grafico_4_accesibilidad.png

Ejecución: python generar_graficos_evidencia.py
Requisitos: pandas, numpy, matplotlib, seaborn
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as MplPolygon

BASE_DIR = Path(__file__).resolve().parent  # carpeta 6_visualizaciones (salida de gráficos)
REPO_DIR = BASE_DIR.parent                   # raíz del repo (donde están los datasets)
ARCHIVO_MAESTRO = REPO_DIR / "dataset_maestro.csv"
ARCHIVO_GEO = BASE_DIR / "geo" / "comunas_caba.geojson"
DPI = 300

# Paleta apta para daltónicos (Okabe-Ito / seaborn colorblind)
GRIS_CONTEXTO = "#BdBdBd"
COLOR_DEST_1 = "#0072B2"  # azul
COLOR_DEST_2 = "#D55E00"  # naranja
COLOR_REF = "#CC3311"     # rojo para umbral
COLOR_MEDIANA = "#0072B2"


def aplicar_estilo() -> None:
    """Estilo base limpio y consistente para todas las figuras (decluttering)."""
    sns.set_theme(style="white", context="notebook")
    plt.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })


def orden_periodo(periodo: str) -> int:
    """Convierte '2018-Q1' en un entero ordenable (2018*4 + 1)."""
    anio, q = str(periodo).split("-Q")
    return int(anio) * 4 + int(q)


def cargar_datos() -> pd.DataFrame:
    df = pd.read_csv(ARCHIVO_MAESTRO)
    df["orden"] = df["periodo_trim"].apply(orden_periodo)
    df["anio"] = df["periodo_trim"].str.slice(0, 4).astype(int)
    return df.sort_values("orden").reset_index(drop=True)


def guardar(fig, nombre: str) -> None:
    ruta = BASE_DIR / nombre
    fig.savefig(ruta, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {nombre}")


# =============================================================================
# GRÁFICO 1 — Pregunta 1: evolución del precio por comuna y ambientes
# Tipo: líneas (evolución temporal). Escala log porque el precio nominal
# crece de forma multiplicativa (inflación) y en lineal todo se aplastaría.
# =============================================================================

def grafico_1_precios(df: pd.DataFrame) -> None:
    ambientes_labels = {1: "1 ambiente", 2: "2 ambientes", 3: "3 ambientes"}
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.2), sharey=True)
    ticks_y = [5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]

    for ax, amb in zip(axes, (1, 2, 3)):
        sub = df[(df["ambientes"] == amb) & df["precio_promedio_pesos"].notna()]

        # Calcular el multiplicador (último / primero) por comuna para destacar
        multiplicadores = {}
        for comuna, g in sub.groupby("comuna"):
            g = g.sort_values("orden")
            if len(g) >= 2 and g["precio_promedio_pesos"].iloc[0] > 0:
                multiplicadores[comuna] = (
                    g["precio_promedio_pesos"].iloc[-1] / g["precio_promedio_pesos"].iloc[0]
                )
        top2 = sorted(multiplicadores, key=multiplicadores.get, reverse=True)[:2]

        # Banda P25–P75: rango donde se ubica la mayoría de las comunas (contexto)
        pcts = sub.groupby("orden")["precio_promedio_pesos"].quantile([0.25, 0.75]).unstack()
        ax.fill_between(pcts.index, pcts[0.25], pcts[0.75],
                        color=GRIS_CONTEXTO, alpha=0.45, zorder=1,
                        label="Rango P25–P75 (comunas)")

        # Las 2 de mayor incremento, en color (enfocar la atención)
        for comuna, color in zip(top2, (COLOR_DEST_1, COLOR_DEST_2)):
            g = sub[sub["comuna"] == comuna].sort_values("orden")
            ax.plot(g["orden"], g["precio_promedio_pesos"],
                    color=color, linewidth=2.5, zorder=3,
                    label=f"Comuna {comuna} (×{multiplicadores[comuna]:.0f})")

        ax.set_yscale("log")
        ax.set_title(ambientes_labels[amb], fontsize=12)
        ax.legend(frameon=False, fontsize=9, loc="upper left")

        # Eje X: mostrar solo años enteros
        anios = sorted(df["anio"].unique())
        ax.set_xticks([a * 4 + 1 for a in anios])
        ax.set_xticklabels(anios, rotation=45)
        ax.grid(True, axis="y", alpha=0.25)
        ax.grid(True, axis="x", alpha=0.25)

        # Marcas del eje Y visibles en los 3 paneles (escala log)
        ax.set_yticks(ticks_y)
        ax.set_ylim(5000, 1300000)
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v, _: f"${v:,.0f}".replace(",", "."))
        )
        ax.yaxis.set_minor_formatter(mticker.NullFormatter())
        ax.tick_params(axis="y", labelleft=True)

    axes[0].set_ylabel("Precio promedio de publicación ($, escala log)")

    fig.suptitle(
        "El precio nominal de alquiler se multiplicó por unas 70 veces entre 2018 y 2026 en todas las comunas",
        fontsize=15, fontweight="bold", y=1.02, x=0.02, ha="left",
    )
    fig.text(
        0.02, -0.04,
        "La banda gris muestra el rango P25–P75 de las comunas; en color, las dos de mayor incremento por tipología. "
        "Escala logarítmica: el crecimiento nominal está dominado por la inflación del período.",
        fontsize=9, color="#555555", ha="left",
    )
    fig.tight_layout()
    fig.subplots_adjust(wspace=0.18)
    guardar(fig, "grafico_1_precios.png")


# =============================================================================
# GRÁFICO 2 — Pregunta 2: relación oferta vs precio por comuna
# Tipo: dispersión (relación entre dos variables numéricas). Tamaño de burbuja
# = superficie total ofrecida (tercera variable).
# =============================================================================

def grafico_2_oferta_precio(df: pd.DataFrame) -> None:
    # Último trimestre con buena cobertura de precios, monoambiente
    sub = df[(df["ambientes"] == 1) & df["precio_promedio_pesos"].notna()]
    ultimo = sub.sort_values("orden")["periodo_trim"].iloc[-1]
    datos = sub[sub["periodo_trim"] == ultimo].copy()

    x = datos["cantidad_deptos_estimada"].to_numpy()
    y = datos["precio_promedio_pesos"].to_numpy()
    sup = datos["superficie_total_m2"].to_numpy()

    # Coeficiente de correlación de Pearson (evidencia cuantitativa de la relación)
    r = float(np.corrcoef(x, y)[0, 1])

    # Comunas a destacar: la de mayor superficie ofrecida y la de menor
    com_max = int(datos.loc[datos["superficie_total_m2"].idxmax(), "comuna"])
    com_min = int(datos.loc[datos["superficie_total_m2"].idxmin(), "comuna"])

    fig, ax = plt.subplots(figsize=(10, 7))

    sup_max = sup.max()
    def escala_tam(v):
        return v / sup_max * 1500 + 60
    tam = escala_tam(sup)

    colores = [
        COLOR_DEST_2 if c == com_max else (GRIS_CONTEXTO if c == com_min else COLOR_DEST_1)
        for c in datos["comuna"]
    ]
    ax.scatter(x, y, s=tam, color=colores, alpha=0.6, edgecolor="white",
               linewidth=1.5, zorder=2)

    # Línea de tendencia (regresión lineal simple)
    coef = np.polyfit(x, y, 1)
    xs = np.array([x.min(), x.max()])
    (linea_tend,) = ax.plot(xs, coef[0] * xs + coef[1], color="#555555", linestyle="--",
                            linewidth=1.5, zorder=1,
                            label=f"Tendencia (r = {r:.2f}, positiva moderada)")

    # Etiquetado directo de cada comuna
    for _, row in datos.iterrows():
        ax.annotate(f"C{int(row['comuna'])}",
                    (row["cantidad_deptos_estimada"], row["precio_promedio_pesos"]),
                    fontsize=9, ha="center", va="center", zorder=3, color="#16324a")

    ax.set_xlabel("Cantidad estimada de departamentos en oferta (volumen)")
    ax.set_ylabel("Precio promedio de publicación ($)")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"${v:,.0f}".replace(",", "."))
    )
    ax.grid(True, alpha=0.25)

    # Leyenda de tamaño de burbuja (decodifica la 3ra variable: superficie)
    valores_ref = [int(sup.min()), int(np.median(sup)), int(sup_max)]
    handles_tam = [
        plt.scatter([], [], s=escala_tam(v), color=GRIS_CONTEXTO, alpha=0.6,
                    edgecolor="white", label=f"{v:,.0f} m²".replace(",", "."))
        for v in valores_ref
    ]
    leg_tam = ax.legend(handles=handles_tam, title="Superficie total ofrecida",
                        frameon=False, fontsize=9, title_fontsize=9,
                        loc="lower right", labelspacing=1.4, borderpad=1.1)
    ax.add_artist(leg_tam)
    ax.legend(handles=[linea_tend], frameon=False, fontsize=9, loc="upper left")

    ax.set_title(
        f"Las comunas con más oferta tienden a ser las más caras, no las más baratas ({ultimo}, monoambientes)",
        fontsize=13.5, loc="left", pad=14,
    )
    fig.text(
        0.02, -0.04,
        f"Cada burbuja es una comuna (C1–C15); el tamaño representa la superficie total ofrecida en m². "
        f"Se destaca en naranja la comuna de mayor oferta (C{com_max}). "
        f"La tendencia es positiva moderada (r = {r:.2f}): más oferta no abarata, va de la mano de precios más altos.\n"
        f"Nota: «cantidad estimada de departamentos» es una variable derivada (superficie total ÷ "
        f"superficie promedio de la ciudad), no un conteo observado.",
        fontsize=9, color="#555555", ha="left",
    )
    fig.tight_layout()
    guardar(fig, "grafico_2_oferta_precio.png")


# =============================================================================
# GRÁFICO 4 — Pregunta 3: accesibilidad (ratio alquiler / sueldo) en el tiempo
# Tipo: líneas + línea de referencia al 30 % (umbral de asequibilidad).
# Es el gráfico-clímax de la historia.
# =============================================================================

def grafico_4_accesibilidad(df: pd.DataFrame) -> None:
    sub = df[(df["ambientes"] == 1) & df["ratio_alquiler_sueldo_pct"].notna()].copy()

    fig, ax = plt.subplots(figsize=(11, 6.5))

    # Zona "no asequible" (todo lo que supera el 30 % del sueldo)
    ax.axhspan(30, 115, color=COLOR_REF, alpha=0.06, zorder=0)

    # Banda P25–P75: rango donde se ubica la mayoría de las comunas (contexto)
    pcts = sub.groupby("orden")["ratio_alquiler_sueldo_pct"].quantile([0.25, 0.75]).unstack()
    ax.fill_between(pcts.index, pcts[0.25], pcts[0.75],
                    color=GRIS_CONTEXTO, alpha=0.5, zorder=1,
                    label="Rango P25–P75 (comunas)")

    # Línea del peor caso: comuna más cara por trimestre (ancla el pico de 108 %)
    peor = sub.groupby("orden")["ratio_alquiler_sueldo_pct"].max()
    ax.plot(peor.index, peor.values, color=COLOR_DEST_2, linewidth=1.4,
            alpha=0.8, zorder=3, label="Comuna más cara")

    # Mediana por trimestre, en color (la tendencia central)
    mediana = sub.groupby("orden")["ratio_alquiler_sueldo_pct"].median()
    ax.plot(mediana.index, mediana.values, color=COLOR_MEDIANA, linewidth=3,
            zorder=4, label="Mediana de comunas")

    # Línea de referencia: umbral de asequibilidad 30 %
    ax.axhline(30, color=COLOR_REF, linestyle="--", linewidth=2.2, zorder=2)
    ax.text(sub["orden"].min(), 31.5, "Umbral de asequibilidad (30%)",
            color=COLOR_REF, fontsize=10, fontweight="bold", va="bottom")
    ax.set_ylim(28, 115)

    # Anotar el pico histórico (2023-Q4, Comuna 14)
    pico = sub.loc[sub["ratio_alquiler_sueldo_pct"].idxmax()]
    ax.annotate(
        f"Pico: {pico['ratio_alquiler_sueldo_pct']:.0f}% del sueldo\n"
        f"(Comuna {int(pico['comuna'])}, {pico['periodo_trim']})",
        xy=(pico["orden"], pico["ratio_alquiler_sueldo_pct"]),
        xytext=(sub["orden"].min() + 4, pico["ratio_alquiler_sueldo_pct"]),
        fontsize=10, fontweight="bold", color="#16324a",
        ha="left", va="center",
        arrowprops=dict(arrowstyle="->", color="#16324a"),
    )

    anios = sorted(df["anio"].unique())
    ax.set_xticks([a * 4 + 1 for a in anios])
    ax.set_xticklabels(anios, rotation=45)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_ylabel("Alquiler de monoambiente como % del sueldo básico")
    ax.set_xlabel("")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=10, loc="lower right")

    ax.set_title(
        "El alquiler de un monoambiente nunca bajó del 30% del sueldo y en 2023 superó un sueldo entero",
        fontsize=14, loc="left", pad=14,
    )
    fig.text(
        0.02, -0.03,
        "La banda gris es el rango P25–P75 de las comunas; en azul, la mediana; en naranja, la comuna más cara. "
        "La referencia roja marca el 30% (umbral internacional de asequibilidad). Categoría salarial: Administrativo A (SEC).",
        fontsize=9, color="#555555", ha="left",
    )
    fig.tight_layout()
    guardar(fig, "grafico_4_accesibilidad.png")


# =============================================================================
# GRÁFICO 3 — Pregunta 2 (versión geográfica): mapa de comunas con burbujas
# Tipo: mapa de símbolos (bubble map). Base = polígonos de comunas de CABA;
# burbuja por comuna: tamaño = oferta estimada, color = precio promedio.
# =============================================================================

def _centroide(coords_poligono) -> tuple[float, float]:
    """Centroide (shoelace) del anillo exterior de un polígono [lon, lat]."""
    ring = np.array(coords_poligono[0])
    x, y = ring[:, 0], ring[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    cross = x * y1 - x1 * y
    area = cross.sum() / 2.0
    if abs(area) < 1e-12:
        return float(x.mean()), float(y.mean())
    cx = ((x + x1) * cross).sum() / (6.0 * area)
    cy = ((y + y1) * cross).sum() / (6.0 * area)
    return float(cx), float(cy)


def _poligono_mas_grande(geometry) -> list:
    """Devuelve el polígono de mayor área de un (Multi)Polygon."""
    if geometry["type"] == "Polygon":
        return geometry["coordinates"]
    mejor, mejor_area = None, -1.0
    for poly in geometry["coordinates"]:
        ring = np.array(poly[0])
        area = abs(np.cross(ring, np.roll(ring, -1, axis=0)).sum())
        if area > mejor_area:
            mejor, mejor_area = poly, area
    return mejor


def grafico_3_mapa_burbujas(df: pd.DataFrame) -> None:
    if not ARCHIVO_GEO.exists():
        print(f"  [SKIP] No se encontró {ARCHIVO_GEO}; se omite el mapa.")
        return

    geo = json.load(open(ARCHIVO_GEO, encoding="utf-8"))

    # Datos: último trimestre con buena cobertura, monoambiente
    sub = df[(df["ambientes"] == 1) & df["precio_promedio_pesos"].notna()]
    ultimo = sub.sort_values("orden")["periodo_trim"].iloc[-1]
    datos = sub[sub["periodo_trim"] == ultimo].set_index("comuna")

    fig, ax = plt.subplots(figsize=(11, 9))

    # Dibujar los polígonos de las comunas (mapa base, gris claro)
    parches = []
    centroides = {}
    for feat in geo["features"]:
        comuna = int(feat["properties"]["comuna"])
        poly = _poligono_mas_grande(feat["geometry"])
        centroides[comuna] = _centroide(poly)
        # Cada anillo del MultiPolygon completo (para que el dibujo sea fiel)
        geom = feat["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for p in polys:
            parches.append(MplPolygon(np.array(p[0]), closed=True))

    ax.add_collection(PatchCollection(parches, facecolor="#EDEDED",
                                      edgecolor="white", linewidth=1.2, zorder=1))

    # Burbujas: una por comuna (tamaño = oferta, color = precio)
    xs, ys, tam, col, etiquetas = [], [], [], [], []
    for comuna, (cx, cy) in centroides.items():
        if comuna in datos.index:
            xs.append(cx); ys.append(cy)
            tam.append(datos.loc[comuna, "cantidad_deptos_estimada"])
            col.append(datos.loc[comuna, "precio_promedio_pesos"])
            etiquetas.append(comuna)

    tam = np.array(tam)
    sizes = tam / tam.max() * 1700 + 80
    sc = ax.scatter(xs, ys, s=sizes, c=col, cmap="viridis",
                    alpha=0.85, edgecolor="white", linewidth=1.5, zorder=3)

    for x, y, c in zip(xs, ys, etiquetas):
        ax.annotate(f"C{c}", (x, y), fontsize=9, ha="center", va="center",
                    color="white", fontweight="bold", zorder=4)

    # Barra de color (precio) + leyenda de tamaño (oferta)
    cbar = fig.colorbar(sc, ax=ax, shrink=0.55, pad=0.02)
    cbar.set_label("Precio promedio de publicación ($)")
    cbar.ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"${v:,.0f}".replace(",", "."))
    )

    valores_ref = [int(tam.min()), int(np.median(tam)), int(tam.max())]
    handles_tam = [
        plt.scatter([], [], s=v / tam.max() * 1700 + 80, color=GRIS_CONTEXTO,
                    alpha=0.7, edgecolor="white", label=f"{v} deptos")
        for v in valores_ref
    ]
    ax.legend(handles=handles_tam, title="Oferta estimada (tamaño)",
              frameon=False, fontsize=9, title_fontsize=9, loc="upper left",
              labelspacing=1.6, borderpad=1.1)

    ax.set_aspect(1.22)  # corrige la latitud (~34.6° S)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.autoscale_view()

    ax.set_title(
        f"Las comunas del norte concentran oferta y los precios más altos ({ultimo}, monoambientes)",
        fontsize=14, loc="left", pad=14,
    )
    fig.text(
        0.02, -0.02,
        "Cada burbuja es una comuna ubicada en el mapa de CABA; el tamaño representa la oferta estimada de "
        "departamentos y el color, el precio promedio. Se usa un mapa de símbolos para mostrar la distribución "
        "geográfica de la oferta y el precio.\n"
        "Nota: «oferta estimada» es una variable derivada (superficie total ÷ superficie promedio de la ciudad).",
        fontsize=9, color="#555555", ha="left",
    )
    fig.tight_layout()
    guardar(fig, "grafico_3_mapa_burbujas.png")


def main() -> None:
    print("Generando visualizaciones del TFI...")
    aplicar_estilo()
    df = cargar_datos()
    grafico_1_precios(df)
    grafico_2_oferta_precio(df)
    grafico_3_mapa_burbujas(df)
    grafico_4_accesibilidad(df)
    print("Listo. 3 gráficos generados en", BASE_DIR)


if __name__ == "__main__":
    main()
