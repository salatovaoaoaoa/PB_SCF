import pandas as pd
from count_pro import count_pro
from config_loader import load_config

config = load_config()

def out_reader(valence=-0.5):
    cleaned_file_path = count_pro(**config)
    
    def add_combined_profile_to_file(file_path):
        df = pd.read_csv(file_path, sep='\t')
        phi_columns = [col for col in df.columns if col.startswith('mol_pol') and col.endswith('_phi')]
        df['combined_phi'] = df[phi_columns].sum(axis=1)
        df.to_csv(file_path, sep='\t', index=False)
        return df

    add_combined_profile_to_file(cleaned_file_path)
    
    df = pd.read_csv(cleaned_file_path, sep='\t')
    
    x = df['x']
    y = df['y']
    phi_brush = df['combined_phi']
    
    if valence != 0:
        psi = df['sys_noname_psi']
        phi_end_brush = df['mon_E_phi']
        return x, y, psi, phi_brush, phi_end_brush
    
    phi_end_brush = df['mon_E_phi']
    return x, y, phi_brush, phi_end_brush