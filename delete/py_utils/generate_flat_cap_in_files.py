import sys
import os
import subprocess
sys.path.append('/home/tpopova/prj/PB_SCF')

from math import sqrt
from math import exp
from math import pi
import numpy as np

def generate_flat_cap_in_files(template_cap: str = 'temp_surface.in',
                   
                   #название параметра
                   range_param: str = 'N_layers',
                   
                   type_lowerbound: str = 'surface',
                   
                   N_brush: int = 200,
                   N_layers: int = 300,
                   S: int = 100,
                   Cs: float = 0.001,
                   alpha: float = 0.5,
                   min_range_value: float = 4,
                   max_range_value: float = 4,
                   
                   chi: float = 0.5,
                   ): 
    #какие параметры меняем?
    change_param = N_layers
    
    #theta
    theta = N_brush/S

    with open(template_cap, 'r') as file:
        data = file.readlines()

    # Изменяем указанные параметры
    for str in range(len(data)):
        if 'lat : flat : n_layers' in data[str]:
            data[str] = f'lat : flat : n_layers : {N_layers}\n'
        if 'lat : flat : lowerbound' in data[str]:
            if type_lowerbound == 'surface':
                data[str] = f'lat : flat : lowerbound : surface\n'
                data[str] += f'mon : U : freedom : frozen\n'
                data[str] += f'mon : U : frozen_range : lowerbound\n'
                data[str] += f'mon : X0 : chi_U : -0.6\n'
                data[str] += f'mon : A : chi_U : -0.6\n'
                data[str] += f'mon : G : chi_U : -0.6\n'
            else: 
                data[str] = f'lat : flat : lowerbound : {type_lowerbound}\n'
        if 'mon : X0 : valence' in data[str]:
            data[str] = f'mon : X0 : valence : {-alpha}\n'
        if 'mon : A : valence' in data[str]:
            data[str] = f'mon : A : valence : {-alpha}\n'
        if 'mon : G : valence' in data[str]:
            data[str] = f'mon : G : valence : {-alpha}\n'
        if 'mol : Cl : phibulk' in data[str]:
            data[str] = f'mol : Cl : phibulk : {Cs}\n'
        if 'mol : brush  : composition' in data[str]:
            data[str] = f'mol : brush  : composition : (X0)1(A){N_brush - 2}(G)1\n'
        if 'mol : brush : theta' in data[str]:
            data[str] = f'mol : brush : theta : {theta}\n'
    
            
    if alpha == 0:
        lines_to_remove = [
            'lat : flat : bondlength : 3e-10\n',
            f'mon : X0 : chi_Na : {chi}\n',
            f'mon : A : chi_Na : {chi}\n',
            f'mon : G : chi_Na : {chi}\n',
            f'mon : X0 : chi_Cl : {chi}\n',
            f'mon : A : chi_Cl : {chi}\n',
            f'mon : G : chi_Cl : {chi}\n',
            f'mon : X0 : valence : {-alpha}\n',
            f'mon : A : valence : {-alpha}\n',
            f'mon : G : valence : {-alpha}\n',
            'mon : Na : valence : 1\n',
            'mon : Cl : valence : -1\n',
            'mon : Na : freedom : free\n',
            'mon : Cl : freedom : free\n',
            'mol : Na : composition  : (Na)1\n',
            'mol : Na : freedom : neutralizer\n',
            'mol : Cl : composition : (Cl)1\n',
            'mol : Cl : freedom : free\n',
            f'mol : Cl : phibulk : {Cs}\n',
            'pro : sys : noname : psi\n',
        ]
        data = [line for line in data if line not in lines_to_remove]
        data.append('\n')
        
        data.append('lat : flat : upperbound : surface\n')
        data.append('mon : S : freedom : frozen\n')
        data.append('mon : S : frozen_range : upperbound\n')
        data.append('mon : X0 : chi_S : -0.3\n')
        data.append('mon : A : chi_S : -0.3\n')
        data.append('mon : G : chi_S : -0.3\n')
        

    # Создаем папку в зависимости от значения change_param
    folder_name = f'FD_flat_cap_range_{range_param}_from_{min_range_value}_to_{max_range_value}'
    folder_name_ = folder_name.replace('.', '_')
    if not os.path.exists(folder_name_):
        os.makedirs(folder_name_)

    # Записываем изменения обратно в файл
    file_name_prefix = f'FD_flat_cap_range_{range_param}_{round(change_param, 5)}'
    full_file_name = f'{file_name_prefix}_n_layers_{N_layers}_N_{N_brush}_S_{round(S,2)}_theta_{round(theta,2)}.in'
    
    #избавляюсь от точек:
    last_dot_index = full_file_name.rfind('.')
    result = full_file_name[:last_dot_index].replace('.', '_') + full_file_name[last_dot_index:]
    
    new_file_path = os.path.join(folder_name_, result)
    
    with open(new_file_path, 'w') as file:
        file.writelines(data)

    #Считает намикс
    subprocess.call(['namics', os.path.abspath(new_file_path)])

    # Переносим посчитанные файлы
    
    # Создаем папку, где будут храниться output файлы
    folder_name_out = f'FD_flat_cap_outfiles_range_{range_param}_from_{min_range_value}_to_{max_range_value}'
        
    # заменяем все точки на _
    folder_name_out__ = folder_name_out.replace('.', '_')
    os.makedirs(f'{folder_name_out__}', exist_ok=True)
    # Получаем список файлов в папке "output"
    files_in_output = os.listdir('output')
    # Путь до созданной папки
    to_folder_out = os.path.abspath(f'{folder_name_out__}')

    # Перемещаем каждый файл в созданную папку
    for file_in_output in files_in_output:
        file_path = os.path.join('output', file_in_output)
        if os.path.isfile(file_path):
            new_file_path = os.path.join(to_folder_out, file_in_output)
            os.rename(file_path, new_file_path)
            
    file_name_pro_flat_cap = os.path.join(to_folder_out, file_in_output)
    
    return file_name_pro_flat_cap