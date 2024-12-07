import sys
import os
import subprocess
sys.path.append('/home/tpopova/prj/PB_SCF')

from math import pi

def create_in(
    template_pore: str = 'pore_temp.in',
    
    #название параметра
    range_param: str = 'Cs',
    min_val : float = 0.1,
    max_val : float = 0.1,
    
    Cs : float = 0.001,
    chi :float = 0.5, 
    
    D : int = 200,
    N : int = 30,
    S : float = 100.0,
    alpha : float = 0.5,
    
    pol_structure : str = 'P0'
    
    ):

    #Theta
    l = S/(2*pi*D)
    theta = N/l

    with open(template_pore, 'r') as file:
        data = file.readlines()

    # Изменяем указанные параметры
    
    for str in range(len(data)):
        
        #Число слоев
        if 'lat : 1G : n_layers' in data[str]:
            data[str] = f'lat : 1G : n_layers : {D}\n'
        
        #chi для растворителя
        elif 'mon : P0 : chi_W' in data[str]:
            data[str] = f'mon : P0 : chi_W : {chi}\n'
        elif 'mon : P : chi_W' in data[str]:
            data[str] = f'mon : P : chi_W : {chi}\n'
        elif 'mon : E : chi_W' in data[str]:
            data[str] = f'mon : E : chi_W : {chi}\n'
        
        #chi для натрия
        elif 'mon : P0 : chi_Na' in data[str]:
            data[str] = f'mon : P0 : chi_Na : {chi}\n'
        elif 'mon : P : chi_Na' in data[str]:
            data[str] = f'mon : P : chi_Na : {chi}\n'
        elif 'mon : E : chi_Na' in data[str]:
            data[str] = f'mon : E : chi_Na : {chi}\n'
        
        #chi для Cl
        elif 'mon : P0 : chi_Cl' in data[str]:
            data[str] = f'mon : P0 : chi_Cl : {chi}\n'
        elif 'mon : P : chi_Cl' in data[str]:
            data[str] = f'mon : P : chi_Cl : {chi}\n'
        elif 'mon : E : chi_Cl' in data[str]:
            data[str] = f'mon : E : chi_Cl : {chi}\n'
            
        # Валентность
        
        elif 'mon : P0 : valence' in data[str]:
            data[str] = f'mon : P0 : valence : {-alpha}\n'
        elif 'mon : P : valence' in data[str]:
            data[str] = f'mon : P : valence : {-alpha}\n'
        elif 'mon : E : valence' in data[str]:
            data[str] = f'mon : E : valence : {-alpha}\n'
        
        # Соль
        elif 'mol : Cl : phibulk' in data[str]:
            data[str] = f'mol : Cl : phibulk : {Cs}\n'
        
        #Композиция полимера
        elif 'mol : pol  : composition' in data[str]:
            data[str] = f'mol : pol  : composition : {pol_structure}\n'
        
        # Плотность прививки
        elif 'mol : pol : theta' in data[str]:
            data[str] = f'mol : pol : theta : {theta}\n'
    
    if alpha == 0:
        lines_to_remove = [
            'lat : 1G : bondlength : 3e-10\n',
            f'mon : P0 : chi_Na : {chi}\n',
            f'mon : P : chi_Na : {chi}\n'
            f'mon : E : chi_Na : {chi}\n'
            f'mon : P0 : chi_Cl : {chi}\n'
            f'mon : P : chi_Cl : {chi}\n'
            f'mon : E : chi_Cl : {chi}\n'
            f'mon : P0 : valence : {-alpha}\n'
            f'mon : P : valence : {-alpha}\n'
            f'mon : E : valence : {-alpha}\n'
            'mon : Na : valence : 1\n',
            'mon : Cl : valence : -1\n',
            'mon : Na : freedom : free\n',
            'mon : Cl : freedom : free\n',
            'mol : Na : composition  : (Na)1\n',
            'mol : Na : freedom : neutralizer\n',
            'mol : Cl : composition : (Cl)1\n',
            'mol : Cl : freedom : free\n',
            f'mol : Cl : phibulk : {Cs}\n',
            'pro : sys : noname : psi\n'
        ]
        data = [line for line in data if line not in lines_to_remove]
        
        data.append('\n')
        
        data.append('lat : 1G : upperbound : surface\n')
        data.append('mon : S : freedom : frozen\n')
        data.append('mon : S : frozen_range : upperbound\n')
        data.append('mon : P0 : chi_S : -0.5\n')
        data.append('mon : P : chi_S : -0.5\n')
        data.append('mon : E : chi_S : -0.5\n')

    # Создаем папку в зависимости от значения change_param
    
    folder_name = f'dendRange_{range_param}_from_{min_val}_to_{max_val}'
    folder_name_ = folder_name.replace('.', '_')
    
    if not os.path.exists(folder_name_):
        os.makedirs(folder_name_)

    # Записываем изменения обратно в файл
    
    file_name_prefix = f'dendRange_{range_param}'
    full_file_name = f'{file_name_prefix}_Cs_{round(Cs,5)}_D_{round(D,2)}_N_{N}_S_{round(S,2)}_theta_{round(theta,2)}_chi_{chi}_alpha_{alpha}.in'
    
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
    folder_name_out = f'dendRange_out_{range_param}_{min_val}_to_{max_val}'
        
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