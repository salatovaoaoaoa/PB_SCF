import numpy as np
import math
import scipy.integrate as integrate
import pandas as pd

from math import sqrt, pi
from numpy import exp
from scipy.optimize import brentq

def find_IEP(pK_min, pK_pl, f):
        """Вычисляет изоэлектрическую точку (IEP) на основе заданных параметров."""
        # Вычисление K_pl и K_min через отрицательные логарифмы
        K_pl = pow(10, -pK_pl)
        K_min = pow(10, -pK_min)

        # Вычисление вспомогательных выражений
        ratio = (2 * f - 1) / (2 * (1 - f))
        sqrt_term = np.sqrt(
            pow(K_min / (2 * K_pl), 2) * pow((2 * f - 1) / (1 - f), 2) 
            + (f / (1 - f)) * (K_min / K_pl)
        )

        # Логарифм основного выражения
        memb = math.log10(ratio * (K_min / K_pl) + sqrt_term)

        # Итоговый расчет pI
        return pK_min + memb

def alpha_buf_plus(pH_b, pK_plus_protein):
        return (1 + 10 ** (pH_b - pK_plus_protein)) ** (-1)

def alpha_buf_minus(pK_minus_protein, pH_b):
        return (1 + 10 ** (pK_minus_protein - pH_b)) ** (-1)
    
def alpha_plus_in_out(pH_b, pK_plus, psi):
        return (
            1
            + (1 - alpha_buf_plus(pH_b, pK_plus))
            / (alpha_buf_plus(pH_b, pK_plus))
            * np.exp(psi)
        ) ** (-1)

def alpha_minus_in_out(pH_b, pK_minus, psi):
        return (
            1
            + (1 - alpha_buf_minus(pK_minus, pH_b))
            / (alpha_buf_minus(pK_minus, pH_b))
            * np.exp(-1 * psi)
        ) ** (-1)

def delta_F_ion(f_pl, psi, alpha_buf_plus, alpha_buf_minus):
        return f_pl * np.log(
            np.exp(psi)
            / (alpha_buf_plus + (1 - alpha_buf_plus) * np.exp(psi))
        ) + (1 - f_pl) * np.log(
            np.exp(-1 * psi)
            / (alpha_buf_minus + (1 - alpha_buf_minus) * np.exp(-1 * psi))
        )
    
def anion_brush(
    Cs: float = 0.001,
    f_plus: float = 0.5,
    pK_minus: float = 5,
    pK_plus: float = 5,
    pK_brush: float = 5.5,
    delta_pH_prot: float = None, 
    delta_pH_brush: float = None,
    lb: float = 1.0,
    a: float = 1.0,
    
    N: int = 300,
    S: float = 100.0,
    
):
    
    """Для белка: pI = pH_b - delta_pH_b
    Для анионной щетки: pK_brush = pH_b - delta_pH_b
    Для катионной щетки: pK_brush = pH_b + delta_pH_b"""

    # Вычисляем изоэлектрическую точку pI
    pI = find_IEP(pK_minus, pK_plus, f_plus)

    # Проверяем, заданы ли параметры для расчета pH_b
    if delta_pH_prot is not None:
        pH_b = pI + delta_pH_prot
        delta_pH_brush = pH_b - pK_brush
    elif delta_pH_brush is not None:
        pH_b = pK_brush + delta_pH_brush
        delta_pH_prot = pH_b - pI
    else:
        raise ValueError("Необходимо задать хотя бы один из параметров: delta_pH_prot или delta_pH_brush.")
    
    """Постоянные параметры для щетки"""
    
    alpha_b: float = (1 + 10 ** (-(pH_b - pK_brush))) ** (-1)
    
    K: float = sqrt(8 * pi * lb * Cs)
    
    H_0: float = sqrt(8 / (3 * pi**2)) * N * sqrt(alpha_b) / a
    
    dzeta_b: float = (2 * pi * lb * alpha_b * N * H_0) / S
    
    """alpha_H  и толщина щетки H"""
    
    def dzeta_func(alpha_h):

        h = ((alpha_h - alpha_b) * K * H_0 * alpha_h) / (
            2 * alpha_b
            * np.sqrt((alpha_b - alpha_b * alpha_h)
            * (alpha_h - alpha_h * alpha_b))
        )

        return -1 * (
            alpha_b**2
            * integrate.quad(
                lambda t: (
                    1
                    - (1 - alpha_h)
                    * (1 + 2 * alpha_b * t**2)
                    * np.exp(alpha_b * (h**2 - t**2))
                )
                / (1 - (1 - alpha_h) * np.exp(alpha_b * (h**2 - t**2))) ** 3,
                0,
                h,
            )[0]
            + ((K * H_0) ** 2 * alpha_b)
            / (4)
            * integrate.quad(
                lambda t: (
                    alpha_b
                    / (1 - alpha_b)
                    * ((1 - alpha_h) * np.exp(alpha_b * (h**2 - t**2)))
                    / (1 - (1 - alpha_h) * np.exp(alpha_b
                                                  * (h**2 - t**2))) ** 2
                )
                - (
                    (1 - alpha_b)
                    / alpha_b
                    * (np.exp(-1 * alpha_b * (h**2 - t**2)))
                    / (1 - alpha_h)
                ),
                0,
                h,
            )[0]
        )

    start = 0.0001

    while True:
        try:
            result = brentq(
                lambda alpha_h: dzeta_func(alpha_h) - dzeta_b, alpha_b - start, alpha_b
            )
            break
        except:
            start += 0.001

    alpha_H: float = result  # type: ignore

    h_find = -1 * (
        ((alpha_H - alpha_b) * K * H_0 * alpha_H)
        / (
            2
            * alpha_b
            * np.sqrt((alpha_b - alpha_b * alpha_H) * (alpha_H - alpha_H * alpha_b))
        )
    )

    H = h_find * H_0

    tlambda = (alpha_H * H_0**2) / (alpha_b * H)
    
    """Число слоев"""
    
    z_in_range = np.linspace(0, H, num=200)
    z_out_range = np.linspace(H, H + 20, num=50)
    
    """Профиль плотности полимера"""
    
    def c_p(z):
        const1 = alpha_b / (2 * np.pi * lb * H_0**2)
        const2 = (K**2 * H_0**2) / (4 * alpha_b)
        first = (
            1
            - (1 - alpha_H)
            * (1 + 2 * alpha_b * z**2 / H_0**2)
            * np.exp(alpha_b * (H**2 - z**2) / H_0**2)
        ) / (1 - (1 - alpha_H) * np.exp(alpha_b * (H**2 - z**2) / H_0**2)) ** 3
        second = (
            alpha_b
            / (1 - alpha_b)
            * ((1 - alpha_H) * np.exp(alpha_b * (H**2 - z**2) / H_0**2))
            / (1 - (1 - alpha_H) * np.exp(alpha_b * (H**2 - z**2) / H_0**2)) ** 2
        )
        third = (
            (1 - alpha_b)
            / alpha_b
            * (np.exp(-1 * alpha_b * (H**2 - z**2) / H_0**2))
            / (1 - alpha_H)
        )
        return const1 * (first + const2 * (second - third))

    c_polymer = c_p(z_in_range)
    
    """alpha_z"""
    
    def alpha_from_z(z):
        return 1 - (1 - alpha_H) * np.exp((alpha_b * (H**2 - z**2)) / (H_0**2))

    alpha_z = alpha_from_z(z_in_range)

    alpha_z_mean = (integrate.quad(lambda z: alpha_from_z(z) * c_p(z), 0, H)[0]) / (
        N / S
    )
    
    """Электростатический потенциал"""

    def psi_in_z(z, alpha_b, H, H_0, alpha_H):
        """ Потенциал внутри щетки. """
        exponent = alpha_b * (H**2 - z**2) / (H_0**2)
        return -alpha_b * (H**2 - z**2) / (H_0**2) + np.log(
            (1 - alpha_b) / (alpha_b * (1 - alpha_H)) * (1 - (1 - alpha_H) * np.exp(exponent))
        )

    def psi_out_z(z, K, tlambda, H):
        """ Потенциал снаружи щетки. """
        sqrt_term = np.sqrt((K * tlambda) ** 2 + 1)
        minus_one = K * tlambda + sqrt_term - 1
        plus_one = K * tlambda - sqrt_term + 1
        exp_term = np.exp(-K * (z - H))
        
        return -2 * np.log((minus_one + plus_one * exp_term) / (minus_one - plus_one * exp_term))

    def psi_in_0(alpha_b, H, H_0, alpha_H):
        """ Потенциал на поверхности прививки. """
        exponent = alpha_b * (H**2) / (H_0**2)
        return -alpha_b * (H**2) / (H_0**2) + np.log(
            (1 - alpha_b) / (alpha_b * (1 - alpha_H)) * (1 - (1 - alpha_H) * np.exp(exponent))
        )

    def psi_in_H(alpha_b, alpha_H):
        """ Потенциал на границе щетки. """
        return np.log((alpha_H * (1 - alpha_b)) / (alpha_b * (1 - alpha_H)))

    # Вычисление значений
    psi_in = psi_in_z(z_in_range, alpha_b, H, H_0, alpha_H)
    psi_out = psi_out_z(z_out_range, K, tlambda, H)
    psi_in_zero = psi_in_0(alpha_b, H, H_0, alpha_H)
    psi_in_H_value = psi_in_H(alpha_b, alpha_H)
    
    """Степени ионизации"""
    
    alpha_anion_pl_in = alpha_plus_in_out(pH_b, pK_plus, psi_in_z(z_in_range, alpha_b, H, H_0, alpha_H))
    alpha_anion_pl_out = alpha_plus_in_out(pH_b, pK_plus, psi_out_z(z_out_range, K, tlambda, H))
    alpha_anion_min_in = alpha_minus_in_out(pH_b, pK_minus, psi_in_z(z_in_range, alpha_b, H, H_0, alpha_H))
    alpha_anion_min_out = alpha_minus_in_out(pH_b, pK_minus, psi_out_z(z_out_range, K, tlambda, H))
    
    """Свободная энергия электростатических взаимодействий"""
    
    def delta_F_ion(psi, alpha_buf_plus_fast, alpha_buf_minus_fast):
        return f_plus * np.log(
            np.exp(psi)
            / (alpha_buf_plus_fast + (1 - alpha_buf_plus_fast) * np.exp(psi))
        ) + (1 - f_plus) * np.log(
            np.exp(-1 * psi)
            / (alpha_buf_minus_fast + (1 - alpha_buf_minus_fast) * np.exp(-1 * psi))
        )

    return pI, pH_b, H, alpha_z_mean, z_in_range, z_out_range, c_polymer, alpha_z,\
        psi_in, psi_out, psi_in_zero, psi_in_H_value, \
        alpha_anion_pl_in, alpha_anion_min_in, alpha_anion_pl_out, alpha_anion_min_out


"""Расчет для слабой катионной щетки"""

def cation_brush(
    Cs: float = 0.001,
    f_plus: float = 0.5,
    pK_minus: float = 5,
    pK_plus: float = 5,
    pK_brush: float = 5.5,
    delta_pH_prot: float = None, 
    delta_pH_brush: float = None,
    lb: float = 1.0,
    a: float = 1.0,
    
    N: int = 300,
    S: float = 100.0,
    
):
    
    """Для белка: pI = pH_b - delta_pH_b
    Для анионной щетки: pK_brush = pH_b - delta_pH_b
    Для катионной щетки: pK_brush = pH_b + delta_pH_b"""

    # Вычисляем изоэлектрическую точку pI
    pI_prot_cation = find_IEP(pK_minus, pK_plus, f_plus)

    # Проверяем, заданы ли параметры для расчета pH_b
    if delta_pH_prot is not None:
        pH_b_cation = pI_prot_cation + delta_pH_prot
        delta_pH_brush = pH_b_cation - pK_brush
    elif delta_pH_brush is not None:
        pH_b_cation = pK_brush + delta_pH_brush
        delta_pH_prot = pH_b_cation - pI_prot_cation
    else:
        raise ValueError("Необходимо задать хотя бы один из параметров: delta_pH_prot или delta_pH_brush.")
    
    """Постоянные параметры для щетки"""
    
    alpha_b_cation: float = (1 + 10 ** (pH_b_cation - pK_brush)) ** (-1)
    
    K: float = sqrt(8 * pi * lb * Cs)
    
    H_0: float = sqrt(8 / (3 * pi**2)) * N * sqrt(alpha_b_cation) / a
    
    dzeta_b: float = (2 * pi * lb * alpha_b_cation * N * H_0) / S
    
    """alpha_H  и толщина щетки H"""
    
    def dzeta_func(alpha_h):

        h = ((alpha_h - alpha_b_cation) * K * H_0 * alpha_h) / (
            2 * alpha_b_cation
            * np.sqrt((alpha_b_cation - alpha_b_cation * alpha_h)
            * (alpha_h - alpha_h * alpha_b_cation))
        )

        return -1 * (
            alpha_b_cation**2
            * integrate.quad(
                lambda t: (
                    1
                    - (1 - alpha_h)
                    * (1 + 2 * alpha_b_cation * t**2)
                    * np.exp(alpha_b_cation * (h**2 - t**2))
                )
                / (1 - (1 - alpha_h) * np.exp(alpha_b_cation * (h**2 - t**2))) ** 3,
                0,
                h,
            )[0]
            + ((K * H_0) ** 2 * alpha_b_cation)
            / (4)
            * integrate.quad(
                lambda t: (
                    alpha_b_cation
                    / (1 - alpha_b_cation)
                    * ((1 - alpha_h) * np.exp(alpha_b_cation * (h**2 - t**2)))
                    / (1 - (1 - alpha_h) * np.exp(alpha_b_cation
                                                  * (h**2 - t**2))) ** 2
                )
                - (
                    (1 - alpha_b_cation)
                    / alpha_b_cation
                    * (np.exp(-1 * alpha_b_cation * (h**2 - t**2)))
                    / (1 - alpha_h)
                ),
                0,
                h,
            )[0]
        )

    start = 0.0001

    while True:
        try:
            result = brentq(
                lambda alpha_h: dzeta_func(alpha_h) - dzeta_b, alpha_b_cation - start, alpha_b_cation
            )
            break
        except:
            start += 0.001

    alpha_H: float = result  # type: ignore

    h_find = -1 * (
        ((alpha_H - alpha_b_cation) * K * H_0 * alpha_H)
        / (
            2
            * alpha_b_cation
            * np.sqrt((alpha_b_cation - alpha_b_cation * alpha_H) * (alpha_H - alpha_H * alpha_b_cation))
        )
    )

    H_cat = h_find * H_0

    tlambda = (alpha_H * H_0**2) / (alpha_b_cation * H_cat)
    
    """Число слоев"""
    
    z_in_range_cat = np.linspace(0, H_cat, num=200)
    z_out_range_cat = np.linspace(H_cat, H_cat + 20, num=50)
    
    """Профиль плотности полимера"""
    
    def c_p(z):
        const1 = alpha_b_cation / (2 * np.pi * lb * H_0**2)
        const2 = (K**2 * H_0**2) / (4 * alpha_b_cation)
        first = (
            1
            - (1 - alpha_H)
            * (1 + 2 * alpha_b_cation * z**2 / H_0**2)
            * np.exp(alpha_b_cation * (H_cat**2 - z**2) / H_0**2)
        ) / (1 - (1 - alpha_H) * np.exp(alpha_b_cation * (H_cat**2 - z**2) / H_0**2)) ** 3
        second = (
            alpha_b_cation
            / (1 - alpha_b_cation)
            * ((1 - alpha_H) * np.exp(alpha_b_cation * (H_cat**2 - z**2) / H_0**2))
            / (1 - (1 - alpha_H) * np.exp(alpha_b_cation * (H_cat**2 - z**2) / H_0**2)) ** 2
        )
        third = (
            (1 - alpha_b_cation)
            / alpha_b_cation
            * (np.exp(-1 * alpha_b_cation * (H_cat**2 - z**2) / H_0**2))
            / (1 - alpha_H)
        )
        return const1 * (first + const2 * (second - third))

    c_polymer_cat = c_p(z_in_range_cat)
    
    """alpha_z"""
    
    def alpha_from_z(z):
        return 1 - (1 - alpha_H) * np.exp(-(alpha_b_cation * (H_cat**2 - z**2)) / (H_0**2))

    alpha_z_cat = alpha_from_z(z_in_range_cat)

    alpha_z_mean_cat = (integrate.quad(lambda z: alpha_from_z(z) * c_p(z), 0, H_cat)[0]) / (
        N / S
    )
    
    """Электростатический потенциал"""

    def psi_in_z(z, alpha_b, H, H_0, alpha_H):
        """ Потенциал внутри щетки. """
        exponent = alpha_b * (H**2 - z**2) / (H_0**2)
        return alpha_b * (H**2 - z**2) / (H_0**2) - np.log(
            (1 - alpha_b) / (alpha_b * (1 - alpha_H)) * (1 - (1 - alpha_H) * np.exp(exponent))
        )

    def psi_out_z(z, K, tlambda, H):
        """ Потенциал снаружи щетки. """
        sqrt_term = np.sqrt((K * tlambda) ** 2 + 1)
        minus_one = K * tlambda + sqrt_term - 1
        plus_one = K * tlambda - sqrt_term + 1
        exp_term = np.exp(-K * (z - H))
        
        return 2 * np.log((minus_one + plus_one * exp_term) / (minus_one - plus_one * exp_term))

    def psi_in_0(alpha_b, H, H_0, alpha_H):
        """ Потенциал на поверхности прививки. """
        exponent = alpha_b * (H**2) / (H_0**2)
        return alpha_b * (H**2) / (H_0**2) - np.log(
            (1 - alpha_b) / (alpha_b * (1 - alpha_H)) * (1 - (1 - alpha_H) * np.exp(exponent))
        )

    def psi_in_H(alpha_b, alpha_H):
        """ Потенциал на границе щетки. """
        return -np.log((alpha_H * (1 - alpha_b)) / (alpha_b * (1 - alpha_H)))

    # Вычисление значений
    psi_in_cat = psi_in_z(z_in_range_cat, alpha_b_cation, H_cat, H_0, alpha_H)
    psi_out_cat = psi_out_z(z_out_range_cat, K, tlambda, H_cat)
    psi_in_zero_cat = psi_in_0(alpha_b_cation, H_cat, H_0, alpha_H)
    psi_in_H_value_cat = psi_in_H(alpha_b_cation, alpha_H)
    
    """Степень ионизации"""
    
    alpha_cation_pl_in = alpha_plus_in_out(pH_b_cation, pK_plus, psi_in_z(z_in_range_cat, alpha_b_cation, H_cat, H_0, alpha_H))
    alpha_cation_pl_out = alpha_plus_in_out(pH_b_cation, pK_plus, psi_out_z(z_out_range_cat, K, tlambda, H_cat))
    alpha_cation_min_in = alpha_minus_in_out(pH_b_cation, pK_minus, psi_in_z(z_in_range_cat, alpha_b_cation, H_cat, H_0, alpha_H))
    alpha_cation_min_out = alpha_minus_in_out(pH_b_cation, pK_minus, psi_out_z(z_out_range_cat, K, tlambda, H_cat))
    
    """Свободная энергия электростатических взаимодействий"""
    
    

    return pI_prot_cation, pH_b_cation, H_cat, alpha_z_mean_cat, z_in_range_cat,\
        z_out_range_cat, c_polymer_cat, alpha_z_cat, psi_in_cat, psi_out_cat,\
        psi_in_zero_cat,psi_in_H_value_cat