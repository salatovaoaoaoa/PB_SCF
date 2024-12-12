import sys
import os
import subprocess
sys.path.append('/home/tpopova/prj/PB_SCF')

from math import pi

def create_in(
    template_shpere: str = 'pore_temp.in',
    
    #название параметра
    range_param: str = 'Cs',
    min_val : float = 0.1,
    max_val : float = 0.1,
    
    r_sphere : int = 5,
    Cs : float = 0.001,
    chi : float = 0.5,
    chi_surf : float = -0.6,
    
    N_layers : int = 200,
    N : int = 300,
    
    S : float = 200.0,
    alpha : float = 0.5,
    
    ):

    #Theta
    theta = 4 * pi * r_sphere**2 * N/S

    with open(template_shpere, 'r') as file:
        data = file.readlines()

    # Изменяем указанные параметры
    
    for str in range(len(data)):
        
        #Число слоев
        if 'lat : sphere : n_layers' in data[str]:
            data[str] = f'lat : sphere : n_layers : {N_layers}\n'
            
        # Радиус сферы
        
        if 'lat : sphere : offset_first_layer' in data[str]:
            data[str] = f'lat : sphere : offset_first_layer : {r_sphere}\n'
        
        #chi для поверхности
        elif 'mon : X0 : chi_S' in data[str]:
            data[str] = f'mon : X0 : chi_S : {chi_surf}\n'
        elif 'mon : A : chi_S' in data[str]:
            data[str] = f'mon : A : chi_S : {chi_surf}\n'
        elif 'mon : E : chi_S' in data[str]:
            data[str] = f'mon : E : chi_S : {chi_surf}\n'
        
        #chi для растворителя
        elif 'mon : X0 : chi_W' in data[str]:
            data[str] = f'mon : X0 : chi_W : {chi}\n'
        elif 'mon : A : chi_W' in data[str]:
            data[str] = f'mon : A : chi_W : {chi}\n'
        elif 'mon : E : chi_W' in data[str]:
            data[str] = f'mon : E : chi_W : {chi}\n'
        
        #chi для натрия
        elif 'mon : X0 : chi_Na' in data[str]:
            data[str] = f'mon : X0 : chi_Na : {chi}\n'
        elif 'mon : A : chi_Na' in data[str]:
            data[str] = f'mon : A : chi_Na : {chi}\n'
        elif 'mon : E : chi_Na' in data[str]:
            data[str] = f'mon : E : chi_Na : {chi}\n'
        
        #chi для Cl
        elif 'mon : X0 : chi_Cl' in data[str]:
            data[str] = f'mon : X0 : chi_Cl : {chi}\n'
        elif 'mon : A : chi_Cl' in data[str]:
            data[str] = f'mon : A : chi_Cl : {chi}\n'
        elif 'mon : E : chi_Cl' in data[str]:
            data[str] = f'mon : E : chi_Cl : {chi}\n'
            
        # Валентность
        
        elif 'mon : X0 : valence' in data[str]:
            data[str] = f'mon : X0 : valence : {-alpha}\n'
        elif 'mon : A : valence' in data[str]:
            data[str] = f'mon : A : valence : {-alpha}\n'
        elif 'mon : E : valence' in data[str]:
            data[str] = f'mon : E : valence : {-alpha}\n'
        # Соль
        elif 'mol : Cl : phibulk' in data[str]:
            data[str] = f'mol : Cl : phibulk : {Cs}\n'
        
        #Композиция полимера
        elif 'mol : pol  : composition' in data[str]:
            data[str] = f'mol : pol  : composition : (X0)1(A){N - 2}(E)1\n'
        
        # Плотность прививки
        elif 'mol : pol : theta' in data[str]:
            data[str] = f'mol : pol : theta : {theta}\n'

    # Создаем папку в зависимости от значения change_param
    
    folder_name = f'sphereRange_{range_param}_from_{min_val}_to_{max_val}'
    folder_name_ = folder_name.replace('.', '_')
    
    if not os.path.exists(folder_name_):
        os.makedirs(folder_name_)

    # Записываем изменения обратно в файл
    
    file_name_prefix = f'sphereRange_{range_param}'
    full_file_name = f'{file_name_prefix}_Cs_{round(Cs,5)}_R_sp_{r_sphere}_N_{N}_theta_{round(theta,2)}_chi_{chi}_alpha_{alpha}.in'
    
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
    folder_name_out = f'sphereRange_out_{range_param}_{min_val}_to_{max_val}'
        
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