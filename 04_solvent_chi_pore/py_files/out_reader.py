import pandas as pd

def out_reader(alpha : float = 0, file_names : str = 'annealing_brush_temp.pro'):
    
    file = f'{file_names}'
    
    phi_brush = pd.read_csv(file, sep='\t')['mol_pol_phi']
    phi_end_brush = pd.read_csv(file, sep='\t')['mon_E_phi']
        
    return phi_brush, phi_end_brush