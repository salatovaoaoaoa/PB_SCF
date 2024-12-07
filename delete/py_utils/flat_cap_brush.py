import numpy as np
import scipy.integrate as integrate
from scipy.optimize import brentq

from mpmath import exp
from numpy import pi
from numpy import sqrt


def flat_brush_cap(
    N: int = 300,
    S: float = 100,
    Cs: float = 0.001,
    lb: float = 1,
    a: float = 1,
    alpha: float = 0.5,
    l: float = 88.8,
):

    K: float = sqrt(8 * pi * lb * Cs)

    H_0: float = sqrt(8 / (3 * pi**2)) * N * alpha ** (1 / 2)

    dzeta_bulk: float = (alpha * N * 2 * pi * lb * H_0) / S

    def h_find(h):

        main_part = (2 * h / (K * H_0)) * ((exp(K * H_0 * h) + exp(2 * K * l - K * H_0 * h)) / (1 - exp(2 * K * l))
        )

        return (
            h
            + (K * H_0 / 2) ** 2
            * exp(h**2 - main_part)
            * integrate.quad(lambda t: np.exp(-(t**2)), 0, h)[0]
            - (K * H_0 / 2) ** 2
            * exp(-(h**2) + main_part)
            * integrate.quad(lambda t: np.exp(t**2), 0, h)[0]
        )

    h_answer = brentq(lambda h: np.float64(float(h_find(h))) - dzeta_bulk, 0.001, 10)

    H = H_0 * h_answer  # type: ignore

    # Координаты

    x_in_range = np.linspace(0, H, num=500)
    x_out_range = np.linspace(H, H + l, num=100)

    # Электростатический потенциал

    def psi_cap_out(x):

        return (2 * H / (K * H_0**2)) * ((np.exp(K * x) + np.exp(2 * K * l - K * x)) / (1 - np.exp(2 * K * l))
        )

    def psi_cap_in(x):

        first = (x**2 - H**2) / H_0**2

        psi_H = (2 * H / (K * H_0**2)) * (
            (np.exp(K * H) + np.exp(2 * K * l - K * H)) / (1 - np.exp(2 * K * l))
        )
        return first + psi_H

    psi_in_cap = psi_cap_in(x_in_range)
    psi_out_cap = psi_cap_out(x_out_range)
    
    #Плостность полимера
    
    def c_polymer(psi):
        rho = -1 * (2*pi*lb*H_0**2)**(-1)
        c_plus = Cs * np.exp(-psi)
        c_minus = Cs * np.exp(psi)
        
        return (-rho + c_plus - c_minus)/alpha
    
    c_p = c_polymer(psi_cap_in(x_in_range))

    return (
        H,
        x_in_range,
        psi_in_cap,
        c_p
    )
