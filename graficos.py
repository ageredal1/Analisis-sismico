"""
graficos.py
Módulo para la generación de gráficos sísmicos con matplotlib.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")   # backend sin ventana (requerido en Streamlit)
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# Paleta de colores consistente para los 3 modos
COLORES = ["#4361ee", "#f72585", "#4cc9f0"]
MARCADORES = ["o", "s", "^"]

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _etiquetas_pisos(n):
    return [f"Piso {i+1}" for i in range(n)]


def _estilo_base(ax, titulo, xlabel, ylabel):
    ax.set_title(titulo, fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.45, color="#cccccc")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 1 – Fuerza sísmica y Cortante en la base (por modo)
# ─────────────────────────────────────────────────────────────────────────────

def grafico_fuerza_cortante(F, V, n_pisos, n_modos):
    """
    Devuelve una figura matplotlib con 2 subplots:
      [0] Fuerza sísmica por piso para cada modo (Piso 1 abajo, último piso arriba)
      [1] Cortante sísmico por piso para cada modo (Piso 1 abajo, último piso arriba)
    """
    pisos = _etiquetas_pisos(n_pisos)
    y = list(range(1, n_pisos + 1))          # Eje Y: 1 (piso 1 abajo) hasta n (piso n arriba)

    fig, axs = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle("Fuerza Sísmica y Cortante en la Base",
                 fontsize=14, fontweight="bold", y=0.98)

    for j in range(n_modos):
        axs[0].plot(F[:, j], y, marker=MARCADORES[j],
                    color=COLORES[j], linewidth=2, label=f"Modo {j+1}")
        axs[1].plot(V[:, j], y, marker=MARCADORES[j],
                    color=COLORES[j], linewidth=2, label=f"Modo {j+1}")

    for ax, titulo, xlabel in zip(
        axs,
        ["Fuerza Sísmica por Piso", "Cortante Sísmico por Piso"],
        ["Fuerza sísmica (t)", "Cortante (t)"],
    ):
        _estilo_base(ax, titulo, xlabel, "Pisos")
        ax.set_yticks(y)
        ax.set_yticklabels(pisos, fontsize=8)
        ax.legend(fontsize=8, loc="best")
        ax.axvline(0, color="#888888", linewidth=0.8, linestyle=":")

    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 2 – Cortantes de combinación (2×2)
# ─────────────────────────────────────────────────────────────────────────────

def grafico_cortantes_combinacion(Vsum_abs, Vrcsc, Vrnc_h, Vreal, n_pisos):
    """
    Devuelve una figura matplotlib 2×2 con:
      Vsum_abs  |  Vrcsc
      Vrnc_h    |  Vreal
      (Piso 1 abajo, último piso arriba)
    """
    pisos = _etiquetas_pisos(n_pisos)
    y = list(range(1, n_pisos + 1))          # Eje Y: 1 (piso 1 abajo) hasta n (piso n arriba)

    datos = [
        (Vsum_abs, "Vsum_abs – Suma de Absolutos",  "#4361ee"),
        (Vrcsc,    "Vrcsc – Raíz Cuadrática",       "#f72585"),
        (Vrnc_h,   "Vrnc_h – Respuesta Máxima",     "#7209b7"),
        (Vreal,    "Vreal – Cortante Real",          "#f77f00"),
    ]

    fig, axs = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("Cortantes de Combinación Modal", fontsize=14,
                 fontweight="bold", y=0.98)

    for ax, (vals, titulo, color) in zip(axs.flat, datos):
        ax.plot(vals, y, marker="o", color=color, linewidth=2.2, markersize=5)
        ax.fill_betweenx(y, 0, vals, alpha=0.12, color=color)
        _estilo_base(ax, titulo, "Cortante (t)", "Pisos")
        ax.set_yticks(y)
        ax.set_yticklabels(pisos, fontsize=8)
        ax.axvline(0, color="#888888", linewidth=0.8, linestyle=":")

    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICO INDIVIDUAL – para cada Vx (usado en sección lateral)
# ─────────────────────────────────────────────────────────────────────────────

def grafico_cortante_individual(valores, titulo, color, n_pisos):
    """
    Devuelve una figura con un solo gráfico horizontal de cortante.
    Piso 1 en la parte inferior, último piso arriba.
    """
    pisos = _etiquetas_pisos(n_pisos)
    y = list(range(1, n_pisos + 1))          # Eje Y: 1 (piso 1 abajo) hasta n (piso n arriba)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(valores, y, marker="o", color=color, linewidth=2.2, markersize=6)
    ax.fill_betweenx(y, 0, valores, alpha=0.15, color=color)
    _estilo_base(ax, titulo, "Cortante (t)", "Pisos")
    ax.set_yticks(y)
    ax.set_yticklabels(pisos, fontsize=8)
    ax.axvline(0, color="#888888", linewidth=0.8, linestyle=":")
    fig.tight_layout()
    return fig
