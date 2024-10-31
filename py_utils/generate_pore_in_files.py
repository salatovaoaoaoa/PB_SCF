import sys
import os
import subprocess
sys.path.append('/home/tpopova/prj/PB_SCF')

from math import sqrt
from math import exp
from math import pi
import numpy as np

def generate_pore_in_files(template_pore: str = 'pore_temp.in',
                   
                   #название параметра
                   range_param: str = 'Cs',

                   N_brush: int = 200,
                   S: int = 100,
                   Cs: float = 0.001,
                   alpha: float = -0.5,
                   D: float = 400,
                   min_range_value: float = 4,
                   max_range_value: float = 4,
                   
                   chi: float = 0.5,
                   ): 
    #какие параметры меняем?
    change_param = Cs
    #theta
    
    l_t = S/(2*pi*D)
    theta = N_brush/l_t

    with open(template_pore, 'r') as file:
        data = file.readlines()

    # Изменяем указанные параметры
    for str in range(len(data)):
        if 'lat : 1G : n_layers' in data[str]:
            data[str] = f'lat : 1G : n_layers : {D}\n'
        elif 'mon : X0 : valence' in data[str]:
            data[str] = f'mon : X0 : valence : {-alpha}\n'
        elif 'mon : A : valence' in data[str]:
            data[str] = f'mon : A : valence : {-alpha}\n'
        elif 'mon : E : valence' in data[str]:
            data[str] = f'mon : E : valence : {-alpha}\n'
        elif 'mol : Cl : phibulk' in data[str]:
            data[str] = f'mol : Cl : phibulk : {Cs}\n'
        elif 'mol : pol  : composition' in data[str]:
            data[str] = f'mol : pol  : composition : (X0)1(A){N_brush - 2}(E)1\n'
        elif 'mol : pol : theta' in data[str]:
            data[str] = f'mol : pol : theta : {theta}\n'
    
    if alpha == 0:
        lines_to_remove = [
            'lat : 1G : bondlength : 3e-10\n',
            f'mon : X0 : chi_Na : {chi}\n',
            f'mon : A : chi_Na : {chi}\n',
            f'mon : E : chi_Na : {chi}\n',
            f'mon : X0 : chi_Cl : {chi}\n',
            f'mon : A : chi_Cl : {chi}\n',
            f'mon : E : chi_Cl : {chi}\n',
            f'mon : X0 : valence : {-alpha}\n',
            f'mon : A : valence : {-alpha}\n',
            f'mon : E : valence : {-alpha}\n',
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
            'pro : mol : Cl : phi\n',
            'pro : mol : Na : phi\n'
        ]
        data = [line for line in data if line not in lines_to_remove]
        
        data.append('\n')
        
        data.append('lat : 1G : upperbound : surface\n')
        data.append('mon : S : freedom : frozen\n')
        data.append('mon : S : frozen_range : upperbound\n')
        data.append('mon : X0 : chi_S : -0.5\n')
        data.append('mon : A : chi_S : -0.5\n')
        data.append('mon : E : chi_S : -0.5\n')

    # Создаем папку в зависимости от значения change_param
    folder_name = f'_pore_range_{range_param}_from_{min_range_value}_to_{max_range_value}'
    folder_name_ = folder_name.replace('.', '_')
    if not os.path.exists(folder_name_):
        os.makedirs(folder_name_)

    # Записываем изменения обратно в файл
    file_name_prefix = f'_pore_range_{range_param}_{round(change_param, 5)}'
    full_file_name = f'{file_name_prefix}_D_{round(D,2)}_N_{N_brush}_S_{round(S,2)}_theta_{round(theta,2)}.in'
    
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
    folder_name_out = f'_pore_outfiles_range_{range_param}_from_{min_range_value}_to_{max_range_value}'
        
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
            
    file_name_pro = os.path.join(to_folder_out, file_in_output)
    
    return file_name_pro