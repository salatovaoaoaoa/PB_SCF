import pandas as pd
import math
import numpy as np

def free_energy(
        PK_MINUS: float = 7.0,
        PK_PLUS: float = 7.0,
        f_plus: float = 0.5,
        
        pH_B: float = 5.0,
        file_names : str = 'annealing_brush_temp.pro'):
    
    # парсим in файл
    file = f'{file_names}'
    
    psi = pd.read_csv(file, sep='\t')['sys_noname_psi']
    phi_brush = pd.read_csv(file, sep='\t')['mol_pol_phi']
    phi_end = pd.read_csv(file, sep='\t')['mon_E_phi']
    r_range = np.arange(len(phi_brush))
    
    #Считаем свободную энергию
    
    #IEP of protein

    def find_IEP(Pk_, Pk_plus):

        X_iep = (10**(Pk_plus-Pk_))/2 * (2*f_plus-1)/(1-f_plus) \
                + np.sqrt(((10**(Pk_plus-Pk_))**2)/4 * ((2*f_plus-1)/(1-f_plus))**2
                           + (10**(Pk_plus-Pk_) * f_plus)/(1-f_plus))
        
        return math.log10(X_iep) + Pk_

    pH_iep_in_quen = find_IEP(PK_MINUS, PK_PLUS)
    
    d_pH_b: float = pH_B - pH_iep_in_quen
    
    # СВОБОДНАЯ ЭНЕРГИЯ
    
    def alpha_buf_plus_exp(delta_pH_b, pH_iep, Pk_plus):
        return (1 + 10**(delta_pH_b + pH_iep - Pk_plus))**(-1)

    def alpha_buf_minus_exp(delta_pH_b, pH_iep, Pk_):
        return (1 + 10**(Pk_ - delta_pH_b - pH_iep))**(-1)

    def delta_F_ion_exp(psi, alpha_buf_plus_exp, alpha_buf_minus_exp):
        return f_plus * np.log(np.exp(psi)/(alpha_buf_plus_exp + (1 - alpha_buf_plus_exp) * np.exp(psi))) +\
               (1 - f_plus) * np.log(np.exp(-1 * psi)/(alpha_buf_minus_exp + (1 - alpha_buf_minus_exp) * np.exp(-1 * psi)))
    
    def Q_exp(alpha_buf_plus_e, alpha_buf_minus_e, psi):
        return f_plus * (1 + (1 - alpha_buf_plus_e)/alpha_buf_plus_e * np.exp(psi))**(-1)\
               - (1 - f_plus) * (1 + (1 - alpha_buf_minus_e)/alpha_buf_minus_e * np.exp(-1 * psi))**(-1)
               
    f_ion_SCF_quen = delta_F_ion_exp(psi,
                               alpha_buf_plus_exp(d_pH_b, pH_iep_in_quen, PK_PLUS),
                               alpha_buf_minus_exp(d_pH_b, pH_iep_in_quen, PK_MINUS))
    
    Q_SCF_quen = Q_exp(alpha_buf_plus_exp(d_pH_b, pH_iep_in_quen, PK_PLUS),
                               alpha_buf_minus_exp(d_pH_b, pH_iep_in_quen, PK_MINUS),
                      psi)
    
    return psi, phi_brush,r_range,  phi_end, f_ion_SCF_quen, Q_SCF_quen, pH_iep_in_quen, d_pH_b