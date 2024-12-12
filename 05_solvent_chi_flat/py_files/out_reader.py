import pandas as pd

def out_reader(alpha : float = 0, file_names : str = 'annealing_brush_temp.pro'):
    
    if alpha > 0:
        file = f'{file_names}'
        
        psi = pd.read_csv(file, sep='\t')['sys_noname_psi']
        phi_brush = pd.read_csv(file, sep='\t')['mol_brush_phi']
        phi_end_brush = pd.read_csv(file, sep='\t')['mon_G_phi']
        
        return psi, phi_brush, phi_end_brush
    
    if alpha == 0:
        file = f'{file_names}'

        phi_brush = pd.read_csv(file, sep='\t')['mol_brush_phi']
        phi_end_brush = pd.read_csv(file, sep='\t')['mon_G_phi']
        
    
        return phi_brush, phi_end_brush