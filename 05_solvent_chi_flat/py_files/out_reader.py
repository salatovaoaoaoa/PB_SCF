import pandas as pd

def out_reader(alpha : float = 0, file_names : str = 'annealing_brush_temp.pro'):
    
    if alpha != 0:
        file = f'{file_names}'
        
        psi = pd.read_csv(file, sep='\t')['sys_noname_psi']
        q = pd.read_csv(file, sep='\t')['sys_noname_q']
        phi_brush = pd.read_csv(file, sep='\t')['mol_brush_phi']
        phi_end_brush = pd.read_csv(file, sep='\t')['mon_G_phi']
        phi_Na = pd.read_csv(file, sep='\t')['mol_Na_phi']
        phi_Cl = pd.read_csv(file, sep='\t')['mol_Cl_phi']
        phi_W = pd.read_csv(file, sep='\t')['mol_water_phi']
        
        return psi, q, phi_brush, phi_end_brush, phi_Na, phi_Cl, phi_W
    
    if alpha == 0:
        file = f'{file_names}'

        phi_brush = pd.read_csv(file, sep='\t')['mol_brush_phi']
        phi_end_brush = pd.read_csv(file, sep='\t')['mon_G_phi']
        phi_W = pd.read_csv(file, sep='\t')['mol_water_phi']
        
    
        return phi_brush, phi_end_brush, phi_W