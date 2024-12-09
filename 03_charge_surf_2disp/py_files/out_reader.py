import pandas as pd

def out_reader(file_names : str = 'annealing_brush_temp.pro'):
    
    file = f'{file_names}'
    
    psi = pd.read_csv(file, sep='\t')['sys_noname_psi']
    phi_brush1 = pd.read_csv(file, sep='\t')['mol_brush1_phi']
    phi_brush2 = pd.read_csv(file, sep='\t')['mol_brush2_phi']
    phi_end_brush1 = pd.read_csv(file, sep='\t')['mon_G_phi']
    phi_end_brush2 = pd.read_csv(file, sep='\t')['mon_E_phi']
    
    return psi, phi_brush1, phi_brush2, phi_end_brush1, phi_end_brush2