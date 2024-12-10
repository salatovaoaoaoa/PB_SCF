import pandas as pd

def out_reader(file_names : str = 'annealing_brush_temp.pro'):
    
    file = f'{file_names}'
    
    psi = pd.read_csv(file, sep='\t')['sys_noname_psi']
    phi_brush = pd.read_csv(file, sep='\t')['mol_pol_phi']
    phi_end_brush = pd.read_csv(file, sep='\t')['mon_E_phi']
    phi_end_leg_brush = pd.read_csv(file, sep='\t')['mon_EL_phi']
    
    return psi, phi_brush, phi_end_brush, phi_end_leg_brush