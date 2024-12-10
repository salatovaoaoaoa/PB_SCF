import sys
import os
sys.path.append('/home/tpopova/prj/PB_SCF/')

import numpy as np

from math import sqrt
from math import pi
from math import atan
from math import ceil

from scipy.special import i0
from scipy.special import i1
import scipy.integrate as integrate
from scipy.optimize import root

def dendrons_pore(
    Cs : float = 0.001,
    
    #параметры щетки
    alpha : float = 0.5,
    S : float = 150.0,
    
    #параметры поры
    D : float = 200.0,
    
    #параметры дендрона
    g : int = 1,
    q : int = 1,
    n_base : int = 10,
    N_opt : int = None,
    
    #const
    lb : float = 1.0, 
    a : float = 1.0,
):
    #Вычисляю коэффициент (coef) и общую N:
    
    if N_opt is None:
        if g == 0:
            N = n_base
            coef = pi/(2 * N)
        if g == 1:
            coef = pow(n_base, -1) * atan(pow(q, -1/2))
            N = n_base * (1 + q)
        if g == 2:
            coef = pow(n_base, -1) * atan(pow(q * (q + 2), -1/2))
            N = n_base * (1 + q + pow(q, 2))
        if g == 3:
            equation = (
                (pow(q, 2) + 2 * q + 3) - sqrt(pow(q**2 + 2*q + 3, 2) - 4)
                )/(2 * q)
            coef = pow(n_base, -1) * atan(pow(equation, 1/2))
            N = n_base * (1 + q + pow(q, 2) + pow(q, 3))
    else:
        if g == 0:
            n = N_opt
            N = N_opt
            coef = pi/(2 * N)

        if g == 1:
            n = ceil(N_opt / (1 + q))
            N = N_opt
            coef = pow(n, -1) * atan(pow(q, -1/2))
            
        if g == 2:
            n = ceil(N_opt / (1 + q + pow(q, 2)))
            N = N_opt
            coef = pow(n, -1) * atan(pow(q * (q + 2), -1/2))

        if g == 3:
            n = ceil(N_opt / (1 + q + pow(q, 2) + pow(q, 3)))
            N = N_opt
            equation = (
                (pow(q, 2) + 2 * q + 3) - sqrt(pow(q**2 + 2*q + 3, 2) - 4)
                )/(2 * q)
            coef = pow(n, -1) * atan(pow(equation, 1/2))

    #Theta
    l = S/(2*pi*D)
    theta = N/l
    
    #Обратная длина Дебая
    K: float = sqrt(8 * pi * lb * Cs)
    
    #Характеристическая толщина (зависит от k)
    H_0_k = sqrt((2 * pow(a, 2))/3) * pow(alpha, 1/2)/coef
    
    #zeta bulk
    zeta_b: float = (2 * pi * D * lb * alpha * N)/S
    
    #Толщина щетки функция
    
    def find_h(h):

        tlambda = H_0_k/h

        rho = h * (D/H_0_k - h)

        c_plus = (K*H_0_k/2)**2 * np.exp(h**2 + 2/(K*tlambda) * i0((D-h*H_0_k)*K)/i1((D-h*H_0_k)*K))\
            * (D/H_0_k * (integrate.quad(lambda t: np.exp(-t ** 2), 0, h)[0]) - (1 - np.exp(-1 * h**2))/2)

        c_minus = (K*H_0_k/2)**2 * np.exp(-1 * h**2 - 2/(K*tlambda) * i0((D-h*H_0_k)*K)/i1((D-h*H_0_k)*K))\
            * (D/H_0_k * (integrate.quad(lambda t: np.exp(t ** 2), 0, h)[0]) - (np.exp(h**2) - 1)/2)
        
        return rho + c_plus - c_minus - zeta_b
    
    h_solution = root(lambda h: find_h(h), 0.01, method='lm')
    
    H_dendrons = h_solution.x * H_0_k
    tlambda_dendrons = H_0_k/h_solution.x
    
    """Функции для вычисления электростатического потенциала, плотности полимера и плотности заряда"""
    
    #Электростатический потенциал
    
    def psi_out(r, tLambda, H_):
        return -2/(K*tLambda) * (i0(r*K))/(i1((D-H_)*K))
    
    def psi_in(r, tLambda, H_):
        first = ((D-r)**2 - H_**2)/H_0_k**2
        psi_H = -2/(K*tLambda) * (i0((D-H_)*K))/(i1((D-H_)*K))
        return first + psi_H
    
    #Плотность заряда rho
    
    def rho_in(r):
        return -1/(2*pi*lb*H_0_k**2) * (2*r - D)/r
    
    #Плотность полимера
    
    def c_p(r, psi):
        
        rho = rho_in(r)

        c_plus = Cs * np.exp(-1 * psi)

        c_minus = Cs * np.exp(psi)

        return (-1 * rho + c_plus - c_minus)/alpha
    
    """Генерации массивов электростатического потенциала, плотности полимера и плотности заряда"""
    
    # Координата r
    r_in_dendrons = np.linspace(D, D-H_dendrons[0], num = 500)
    r_out_dendrons = np.linspace(D-H_dendrons[0], 0, num = 500)
    
    # Электростатический потенциал
    
    psi_in_dendrons = psi_in(r_in_dendrons, tlambda_dendrons, H_dendrons)
    psi_out_dendrons = psi_out(r_out_dendrons, tlambda_dendrons, H_dendrons)
    
    # Плотность полимера
    
    c_pol_dendrons = c_p(r_in_dendrons, psi_in(r_in_dendrons, tlambda_dendrons, H_dendrons))
    
    # Плотность заряда
    
    rho_dendrons = rho_in(r_in_dendrons)
    
    return N, n, theta, H_dendrons, r_in_dendrons, r_out_dendrons, psi_in_dendrons, psi_out_dendrons, c_pol_dendrons, rho_dendrons