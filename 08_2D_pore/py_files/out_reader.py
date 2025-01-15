import sys
sys.path.append('/home/tpopova/prj/PB_SCF/08_2D_pore/py_files')
import pandas as pd

from count_pro import count_pro

def out_reader(
    range_param: str = 'Cs',
    min_val: float = 0.5,
    max_val: float = 0.5,
    output_dir="2D_pore_in_files",  # Каталог для сохранения файлов
    target_dir="/home/tpopova/prj/PB_SCF/08_2D_pore/scf_templates",  # Путь для перемещения
    D=40,
    L_pore=80,
    L_wall=20,
    space=10,
    N=80,
    S=100,
    Cs=0.005,
    valence=-0.5,
    chi_surf=-0.55,
    chi_solv=0.5
):
    
    cleaned_file_path = count_pro(range_param = range_param,
                                  min_val = min_val,
                                    max_val = max_val,
                                    output_dir=output_dir,
                                    target_dir=target_dir,
                                    D=D,
                                    L_pore=L_pore,
                                    L_wall=L_wall,
                                    space=space,
                                    N=N,
                                    S=S,
                                    Cs=Cs,
                                    valence=valence,
                                    chi_surf=chi_surf,
                                    chi_solv=chi_solv)
    
    def add_combined_profile_to_file(file_path):
        # Читаем файл в DataFrame
        df = pd.read_csv(file_path, sep='\t')
    
        # Находим столбцы, начинающиеся с 'mol_pol' и заканчивающиеся на '_phi'
        phi_columns = [col for col in df.columns if col.startswith('mol_pol') and col.endswith('_phi')]
        
        # Суммируем значения всех таких столбцов в новый столбец 'combined_phi'
        df['combined_phi'] = df[phi_columns].sum(axis=1)
        
        # Перезаписываем исходный файл с добавлением нового столбца
        df.to_csv(file_path, sep='\t', index=False)
        
        return df
    
    add_combined_profile_to_file(cleaned_file_path)
        
    if valence != 0:
        x = pd.read_csv(cleaned_file_path, sep='\t')['x']
        y = pd.read_csv(cleaned_file_path, sep='\t')['y']
        psi = pd.read_csv(cleaned_file_path, sep='\t')['sys_noname_psi']
        phi_end_brush = pd.read_csv(cleaned_file_path, sep='\t')['mon_E_phi']
        
        phi_brush = pd.read_csv(cleaned_file_path, sep='\t')['combined_phi']
        
        return x, y, psi, phi_brush, phi_end_brush
    
    if valence == 0:

        x = pd.read_csv(cleaned_file_path, sep='\t')['x']
        y = pd.read_csv(cleaned_file_path, sep='\t')['y']
        phi_end_brush = pd.read_csv(cleaned_file_path, sep='\t')['mon_E_phi']
        
        phi_brush = pd.read_csv(cleaned_file_path, sep='\t')['combined_phi']
    
        return x, y, phi_brush, phi_end_brush