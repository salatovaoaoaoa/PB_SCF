import numpy as np
import math
import scipy.integrate as integrate
import pandas as pd

from math import sqrt
from math import pi
from numpy import exp
from scipy.optimize import brentq


def anneal_brush_cation(
    N: int = 300,
    S: float = 100,
    Cs: float = 0.001,
    lb: float = 1,
    a: float = 1,
    delta_pK_cation: float = 0.3,  # Отступ от pK щетки
    pK_cation: float = 5,
    # Параметры белка
    f_plus: float = 0.5,  # доля заряженных групп на поверхности
    pK_plus: float = 5,
    pK_minus: float = 5,
    V: float = 169.843,
    file_name="annealing_brush_temp.pro",
    chi: float = 0.5,
    
    minus_layers: int = 2
):
    #                                   CONST по pH
    # IEP of protein

    def find_IEP(Pk_, Pk_plus):

        X_iep = (10 ** (Pk_plus - Pk_)) / 2 \
                * (2 * f_plus - 1) / (1 - f_plus) + np.sqrt(
                ((10 ** (Pk_plus - Pk_)) ** 2) / 4
                * ((2 * f_plus - 1) / (1 - f_plus)) ** 2
                + (10 ** (Pk_plus - Pk_) * f_plus) / (1 - f_plus)
        )

        return math.log10(X_iep) + Pk_

    pH_iep_cation = find_IEP(pK_minus, pK_plus)

    # pH of solution

    pH_b_cation: float = pK_cation + delta_pK_cation

    # delta for protein

    delta_pH_b_cation: float = pH_b_cation - pH_iep_cation

    #                             ПОСТОЯННЫЕ ПАРАМЕТРЫ ЩЕТКИ

    # степень ионизации на бесконечности

    alpha_b_cation: float = (1 + 10 ** (delta_pK_cation)) ** (-1)

    # Обратная длина Дебая

    K: float = sqrt(8 * pi * lb * Cs)

    # Характеристическая толщина щетки

    H_0: float = sqrt(8 / (3 * pi**2)) * N * sqrt(alpha_b_cation) / a

    # dzeta bulk
    dzeta_b: float = (2 * pi * lb * alpha_b_cation * N * H_0) / S

    # Находим alpha_h и толщину щетки h

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

    alpha_H_cation: float = result  # type: ignore

    h_find = -1 * (
        ((alpha_H_cation - alpha_b_cation) * K * H_0 * alpha_H_cation)
        / (
            2
            * alpha_b_cation
            * np.sqrt((alpha_b_cation - alpha_b_cation * alpha_H_cation) * (alpha_H_cation - alpha_H_cation * alpha_b_cation))
        )
    )

    H_cation = h_find * H_0

    tlambda = (alpha_H_cation * H_0**2) / (alpha_b_cation * H_cation)

    # Координата

    z_in_range_cation = np.linspace(0, H_cation, num=round(H_cation-minus_layers))
    z_out_range_cation = np.linspace(H_cation, H_cation + 20, num=20)

    def c_p(z):
        const1 = alpha_b_cation / (2 * np.pi * lb * H_0**2)
        const2 = (K**2 * H_0**2) / (4 * alpha_b_cation)
        first = (
            1
            - (1 - alpha_H_cation)
            * (1 + 2 * alpha_b_cation * z**2 / H_0**2)
            * np.exp(alpha_b_cation * (H_cation**2 - z**2) / H_0**2)
        ) / (1 - (1 - alpha_H_cation) * np.exp(alpha_b_cation * (H_cation**2 - z**2) / H_0**2)) ** 3
        second = (
            alpha_b_cation
            / (1 - alpha_b_cation)
            * ((1 - alpha_H_cation) * np.exp(alpha_b_cation * (H_cation**2 - z**2) / H_0**2))
            / (1 - (1 - alpha_H_cation) * np.exp(alpha_b_cation * (H_cation**2 - z**2) / H_0**2)) ** 2
        )
        third = (
            (1 - alpha_b_cation)
            / alpha_b_cation
            * (np.exp(-1 * alpha_b_cation * (H_cation**2 - z**2) / H_0**2))
            / (1 - alpha_H_cation)
        )
        return const1 * (first + const2 * (second - third))

    # alpha z

    def alpha_from_z(z):
        return 1 - (1 - alpha_H_cation) * np.exp(-(alpha_b_cation * (H_cation**2 - z**2)) / (H_0**2))

    alpha_z_cation = alpha_from_z(z_in_range_cation)

    alpha_z_mean_cation = (integrate.quad(lambda z: alpha_from_z(z) * c_p(z), 0, H_cation)[0]) / (
        N / S
    )

    #                              ЭЛЕКТРОСТАТИЧЕСКИЙ ПОТЕНЦИАЛ

    # на границе щетки

    psi_in_H = np.log((alpha_H_cation * (1 - alpha_b_cation)) / (alpha_b_cation * (1 - alpha_H_cation)))

    # внутри щетки

    def psi_in_z(z):
        return alpha_b_cation * (H_cation**2 - z**2) / (H_0**2) - np.log(
            (1 - alpha_b_cation)
            / (alpha_b_cation * (1 - alpha_H_cation))
            * (1 - (1 - alpha_H_cation) * np.exp(alpha_b_cation * (H_cation**2 - z**2) / (H_0**2)))
        )

    psi_in_cation = psi_in_z(z_in_range_cation)

    # снаружи щетки

    def psi_out_z(z):

        minus_one = K * tlambda + np.sqrt((K * tlambda) ** 2 + 1) - 1
        plus_one = K * tlambda - np.sqrt((K * tlambda) ** 2 + 1) + 1
        exp = np.exp(-1 * K * (z - H_cation))

        return 2 * np.log((minus_one + plus_one * exp) / (minus_one - plus_one * exp))

    psi_out_cation = psi_out_z(z_out_range_cation)

    # на поверхности прививки

    def psi_in_0():
        return -1 * alpha_b_cation * (H_cation**2) / (H_0**2) + np.log(
            (1 - alpha_b_cation)
            / (alpha_b_cation * (1 - alpha_H_cation))
            * (1 - (1 - alpha_H_cation) * np.exp(alpha_b_cation * (H_cation**2) / (H_0**2)))
        )

    psi_in_zero = psi_in_0()

    #               СТЕПЕНЬ ИОНИЗАЦИИ В БУФЕРЕ

    def alpha_buf_plus(pH_b, pK_plus_protein):
        return (1 + 10 ** (pH_b - pK_plus_protein)) ** (-1)

    def alpha_buf_minus(pK_minus_protein, pH_b):
        return (1 + 10 ** (pK_minus_protein - pH_b)) ** (-1)

    #             СТЕПЕНЬ ИОНИЗАЦИИ В ЩЕТКЕ

    def alpha_plus_in():
        return (
            1
            + (1 - alpha_buf_plus(pH_b_cation, pK_plus))
            / (alpha_buf_plus(pH_b_cation, pK_plus))
            * np.exp(psi_in_z(z_in_range_cation))
        ) ** (-1)

    def alpha_plus_out():
        return (
            1
            + (1 - alpha_buf_plus(pH_b_cation, pK_plus))
            / (alpha_buf_plus(pH_b_cation, pK_plus))
            * np.exp(psi_out_z(z_out_range_cation))
        ) ** (-1)

    def alpha_minus_in():
        return (
            1
            + (1 - alpha_buf_minus(pK_minus, pH_b_cation))
            / (alpha_buf_minus(pK_minus, pH_b_cation))
            * np.exp(-1 * psi_in_z(z_in_range_cation))
        ) ** (-1)

    def alpha_minus_out():
        return (
            1
            + (1 - alpha_buf_minus(pK_minus, pH_b_cation))
            / (alpha_buf_minus(pK_minus, pH_b_cation))
            * np.exp(-1 * psi_out_z(z_out_range_cation))
        ) ** (-1)

    alpha_pl_in = alpha_plus_in()
    alpha_pl_out = alpha_plus_out()
    alpha_min_in = alpha_minus_in()
    alpha_min_out = alpha_minus_out()

    # Свободная энергия

    def alpha_buf_plus_fast():
        return (1 + 10 ** (delta_pH_b_cation + pH_iep_cation - pK_plus)) ** (-1)

    def alpha_buf_minus_fast():
        return (1 + 10 ** (pK_minus - delta_pH_b_cation - pH_iep_cation)) ** (-1)

    def delta_F_ion(psi, alpha_buf_plus_fast, alpha_buf_minus_fast):
        return f_plus * np.log(
            np.exp(psi)
            / (alpha_buf_plus_fast + (1 - alpha_buf_plus_fast) * np.exp(psi))
        ) + (1 - f_plus) * np.log(
            np.exp(-1 * psi)
            / (alpha_buf_minus_fast + (1 - alpha_buf_minus_fast) * np.exp(-1 * psi))
        )

    f_ion_in_cation = delta_F_ion(
        psi_in_z(z_in_range_cation), alpha_buf_plus_fast(), alpha_buf_minus_fast()
    )
    f_ion_out_cation = delta_F_ion(
        psi_out_z(z_out_range_cation), alpha_buf_plus_fast(), alpha_buf_minus_fast()
    )

    # Заряд

    def Q_exp(alpha_buf_plus_fast, alpha_buf_minus_fast, psi):
        return f_plus * (
            1 + (1 - alpha_buf_plus_fast) / alpha_buf_plus_fast * np.exp(psi)
        ) ** (-1) - (1 - f_plus) * (
            1 + (1 - alpha_buf_minus_fast) / alpha_buf_minus_fast * np.exp(-1 * psi)
        ) ** (
            -1
        )

    charge_in = Q_exp(
        alpha_buf_plus_fast(), alpha_buf_minus_fast(), psi_in_z(z_in_range_cation)
    )

    charge_out = Q_exp(
        alpha_buf_plus_fast(), alpha_buf_minus_fast(), psi_out_z(z_out_range_cation)
    )

    # #Плотность заряда rho (z)

    def rho(z):
        memb = -1 * alpha_b_cation / (2 * pi * lb * (H_0) ** 2)
        numerator = 1 - (1 - alpha_H_cation) * (1 + 2 * alpha_b_cation * z**2 / H_0**2) * exp(
            alpha_b_cation * (H_cation**2 - z**2) / H_0**2
        )
        denominator = (1 - (1 - alpha_H_cation) * exp(alpha_b_cation * (H_cation**2 - z**2) / H_0**2)) ** 2
        return memb * (numerator) / (denominator)

    rho_range = [rho(z_in_range_cation[i]) for i in range(len(z_in_range_cation))]

    polymer_dens_anneal_cation = np.asarray(
        [
            (-1 * rho_range[i] - Cs * np.exp(psi_in_cation[i]) + Cs * np.exp(-psi_in_cation[i]))
            / (alpha_z_cation[i])
            for i in range(len(z_in_range_cation))
        ]
    )
    
    if file_name is None:
        parse_SCF_psi_cation = 0
        parse_SCF_phi_cation = 0
        f_ion_SCF_cation = 0
        charge_SCF_cation = 0
    else:

        # Профили SCF

        # NAMICS
        parse_SCF_psi_cation = pd.read_csv(file_name, sep="\t")["sys_noname_psi"][
            minus_layers : round(H_cation) + 20
        ]
        parse_SCF_phi_cation = pd.read_csv(file_name, sep="\t")["mol_brush_phi"][minus_layers : round(H_cation) + 20]

        f_ion_SCF_cation = delta_F_ion(
            parse_SCF_psi_cation, alpha_buf_plus_fast(), alpha_buf_minus_fast()
        )
        charge_SCF = Q_exp(alpha_buf_plus_fast(), alpha_buf_minus_fast(), parse_SCF_psi_cation)

    # РАСЧЕТ ОСМОТИЧЕСКОГО И ОБЪЕМНОГО ВКЛАДОВ

    def f_osmotic(phi):
        return -1 * np.log(1 - phi) - 2 * chi * phi

    def f_volume_protein(psi):
        return 4 * V * Cs * (np.sinh(psi / 2)) ** 2

        #  ОСМОТИЧЕСКИЙ ВКЛАД В СВОБОДНУЮ ЭНЕРГИЮ (ТЕОРИЯ)

    F_osm_cation = f_osmotic(polymer_dens_anneal_cation)

    # ВКЛАД В СВОБОДНУЮ ЭНЕРГИЮ ОТ БЕЛКА (ТЕОРИЯ)

    F_vol_in_cation = f_volume_protein(psi_in_cation)
    F_vol_out_cation = f_volume_protein(psi_out_cation)

    # ПОЛНАЯ СВОБОДНАЯ ЭНЕРГИЯ (ТЕОРИЯ)

    F_full_theory_in_cation = f_ion_in_cation + F_vol_in_cation + F_osm_cation
    F_full_theory_out_cation = f_ion_out_cation + F_vol_out_cation

    #  ОСМОТИЧЕСКИЙ ВКЛАД В СВОБОДНУЮ ЭНЕРГИЮ (SCF)

    F_osm_SCF_cation = f_osmotic(parse_SCF_phi_cation)

    # ВКЛАД В СВОБОДНУЮ ЭНЕРГИЮ ОТ БЕЛКА (SCF)

    F_vol_SCF_cation = f_volume_protein(parse_SCF_psi_cation)

    # ПОЛНАЯ СВОБОДНАЯ ЭНЕРГИЯ (SCF)

    F_full_SCF_cation = f_ion_SCF_cation + F_vol_SCF_cation + F_osm_SCF_cation

    # #Заряд белка вне щетки

    # Q_mean = charge_out[-1]

    return (
        H_cation,
        alpha_H_cation,
        alpha_z_mean_cation,
        alpha_z_cation,
        alpha_b_cation,
        pH_b_cation,
        pH_iep_cation,
        delta_pH_b_cation,
        z_in_range_cation,
        z_out_range_cation,
        psi_in_cation,
        psi_out_cation,
        polymer_dens_anneal_cation,
        parse_SCF_psi_cation,
        parse_SCF_phi_cation,
        f_ion_in_cation,
        f_ion_out_cation, 
        F_vol_in_cation, 
        F_vol_out_cation, 
        F_osm_cation,
        F_full_theory_in_cation, 
        F_full_theory_out_cation,
        
        f_ion_SCF_cation,
        F_osm_SCF_cation,
        F_vol_SCF_cation,
        F_full_SCF_cation 
    )
