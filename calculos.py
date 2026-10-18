"""
calculos.py
Módulo de cálculo sísmico modal espectral.
Lógica extraída de ET2_logic.py.
"""

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE CÁLCULO
# ─────────────────────────────────────────────────────────────────────────────

def periodo_fundamental_vibracion_aproximado(hi: float, m) -> float:
    """
    Calcula el periodo fundamental de vibración aproximado de un edificio.
    hi : float - Altura de entrepiso (m)
    m  : array - Masas de cada piso (t*s^2/m)
    """
    n_pisos = len(m)
    H = hi * n_pisos
    Ct = 35
    return H / Ct


def factor_C(T_modos, Tp: float = 0.4, TL: float = 2.5):
    """
    Calcula el factor de amplificación sísmica C para cada modo de vibración.
    """
    condiciones = [
        T_modos <= Tp,
        (T_modos > Tp) & (T_modos <= TL),
        T_modos > TL,
    ]
    valores_C = [
        2.5,
        2.5 * Tp / T_modos,
        2.5 * Tp * TL / (T_modos ** 2),
    ]
    return np.select(condiciones, valores_C)


def pseudo_aceleracion_espectral(Z: float, U: float, C, S: float, R: float):
    """
    Calcula la pseudo aceleración espectral Sa (m/s^2).
    """
    g = 9.81
    return g * Z * U * C * S / R


def frecuencia_estructural(T_modos):
    """
    Calcula la frecuencia circular estructural W (rad/s).
    """
    return 2 * np.pi / T_modos


def desplazamiento_espectral(Sa, W):
    """
    Calcula el desplazamiento espectral Sd (m).
    """
    return Sa / (W ** 2)


def factor_participacion_modal(Phi, m):
    """
    Calcula el factor de participación de masa modal Gamma para cada modo.
    Phi: shape (n_pisos, n_modos)
    m  : shape (n_pisos,)
    """
    M = np.diag(m)
    numerador = Phi.T @ m
    denominador = np.diag(Phi.T @ M @ Phi)
    return numerador / denominador


def aceleracion_por_piso_modal(Sa, gamma, Phi):
    """
    Calcula la aceleración por piso para cada modo Ü (m/s^2).
    Retorna shape (n_pisos, n_modos)
    """
    return Sa * gamma * Phi


def fuerza_sismica(m, U_acc):
    """
    Calcula la fuerza sísmica F para cada piso y modo (t*m/s^2).
    Retorna shape (n_pisos, n_modos)
    """
    M = np.diag(m)
    return M @ U_acc


def cortante_sismica(F):
    """
    Calcula el cortante sísmico V acumulado de arriba hacia abajo.
    Retorna shape (n_pisos, n_modos)
    """
    return np.flip(np.cumsum(np.flip(F, axis=0), axis=0), axis=0)


def cortante_suma_absolutos(V):
    """
    Cortante por suma de valores absolutos Vsum_abs para cada piso.
    Retorna shape (n_pisos,)
    """
    return np.sum(np.abs(V), axis=1)


def cortante_raiz_cuadrada(V):
    """
    Cortante por raíz cuadrada de la suma de cuadrados Vrcsc para cada piso.
    Retorna shape (n_pisos,)
    """
    return np.sqrt(np.sum(V ** 2, axis=1))


def cortante_respuesta_maxima(Vsum_abs, Vrcsc):
    """
    Cortante de respuesta máxima Vrnc_h para cada piso.
    """
    return 0.25 * Vsum_abs + 0.75 * Vrcsc


def cortante_real(Vrnc_h, R: float):
    """
    Cortante real Vreal para cada piso.
    """
    return Vrnc_h * 0.75 * R


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN MAESTRA
# ─────────────────────────────────────────────────────────────────────────────

def ejecutar_calculos(hi, m, T_modos, Phi, Z, U, S, R) -> dict:
    """
    Ejecuta todos los cálculos sísmicos modales y devuelve un diccionario
    con todos los resultados.
    """
    m = np.asarray(m, dtype=float)
    T_modos = np.asarray(T_modos, dtype=float)
    Phi = np.asarray(Phi, dtype=float)

    T_aprox  = periodo_fundamental_vibracion_aproximado(hi, m)
    C        = factor_C(T_modos)
    Sa       = pseudo_aceleracion_espectral(Z, U, C, S, R)
    W        = frecuencia_estructural(T_modos)
    Sd       = desplazamiento_espectral(Sa, W)
    gamma    = factor_participacion_modal(Phi, m)
    U_acc    = aceleracion_por_piso_modal(Sa, gamma, Phi)
    F        = fuerza_sismica(m, U_acc)
    V        = cortante_sismica(F)
    Vsum_abs = cortante_suma_absolutos(V)
    Vrcsc    = cortante_raiz_cuadrada(V)
    Vrnc_h   = cortante_respuesta_maxima(Vsum_abs, Vrcsc)
    Vreal    = cortante_real(Vrnc_h, R)

    return {
        "T_aprox":  T_aprox,
        "C":        C,
        "Sa":       Sa,
        "W":        W,
        "Sd":       Sd,
        "gamma":    gamma,
        "U_acc":    U_acc,
        "F":        F,
        "V":        V,
        "Vsum_abs": Vsum_abs,
        "Vrcsc":    Vrcsc,
        "Vrnc_h":   Vrnc_h,
        "Vreal":    Vreal,
        "n_pisos":  len(m),
        "n_modos":  len(T_modos),
    }
