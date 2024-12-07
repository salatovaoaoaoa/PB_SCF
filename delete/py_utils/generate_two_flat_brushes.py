import sys
import os
import subprocess
sys.path.append('/home/tpopova/prj/PB_SCF')

from math import sqrt
from math import exp
from math import pi
import numpy as np

def generate_two_flat_brush_in_files(template_two: str = 'temp_surface.in',
                   
                   #название параметра
                   range_param: str = 'N_layers',
                   
                   N_brush_left: int = 200,
                   N_brush_right: int = 200,
                   N_layers: int = 300,
                   S_left: int = 100,
                   S_right: int = 100,
                   Cs: float = 0.001,
                   alpha_left: float = 0.5,
                   alpha_right: float = 0.5,
                   min_range_value: float = 4,
                   max_range_value: float = 4,
                   ): 
    #какие параметры меняем?
    change_param = N_layers
    
    #theta
    theta_right = N_brush_right/S_right
    theta_left = N_brush_left/S_left

    with open(template_two, 'r') as file:
        data = file.readlines()

    # Изменяем указанные параметры
    for str in range(len(data)):
        if 'lat : flat : n_layers' in data[str]:
            data[str] = f'lat : flat : n_layers : {N_layers}\n'
            
        if 'mon : X0 : valence' in data[str]:
            data[str] = f'mon : X0 : valence : {-alpha_left}\n'
        if 'mon : A : valence' in data[str]:
            data[str] = f'mon : A : valence : {-alpha_left}\n'
        if 'mon : G : valence' in data[str]:
            data[str] = f'mon : G : valence : {-alpha_left}\n'
            
        if 'mon : Z0 : valence' in data[str]:
            data[str] = f'mon : Z0 : valence : {-alpha_right}\n'
        if 'mon : B : valence' in data[str]:
            data[str] = f'mon : B : valence : {-alpha_right}\n'
        if 'mon : E : valence' in data[str]:
            data[str] = f'mon : E : valence : {-alpha_right}\n'
            
        if 'mol : Cl : phibulk' in data[str]:
            data[str] = f'mol : Cl : phibulk : {Cs}\n'
            
        if 'mol : brushleft  : composition' in data[str]:
            data[str] = f'mol : brushleft  : composition : (X0)1(A){N_brush_left-2}(G)1\n'
        if 'mol : brushleft : theta' in data[str]:
            data[str] = f'mol : brushleft : theta : {theta_left}\n'
            
        if 'mol : brushright  : composition' in data[str]:
            data[str] = f'mol : brushright  : composition : (Z0)1(B){N_brush_right-2}(E)1\n'
        if 'mol : brushright : theta' in data[str]:
            data[str] = f'mol : brushright : theta : {theta_right}\n'
        

    # Создаем папку в зависимости от значения change_param
    folder_name = f'FD_two_brushes_range_{range_param}_from_{min_range_value}_to_{max_range_value}'
    folder_name_ = folder_name.replace('.', '_')
    if not os.path.exists(folder_name_):
        os.makedirs(folder_name_)

    # Записываем изменения обратно в файл
    file_name_prefix = f'FD_two_brushes_range_{range_param}_{round(change_param, 5)}'
    full_file_name = f'{file_name_prefix}_n_layers_{N_layers}_N_{N_brush_right}_S_{round(S_right,2)}_theta_{round(theta_right,2)}.in'
    
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
    folder_name_out = f'FD_two_brushes_outfiles_range_{range_param}_from_{min_range_value}_to_{max_range_value}'
        
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
            
    file_name_pro_two_brushes = os.path.join(to_folder_out, file_in_output)
    
    return file_name_pro_two_brushes