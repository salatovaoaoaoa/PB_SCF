import sys
import os
import subprocess
sys.path.append('/home/tpopova/prj/PB_SCF')

from math import pi

def create_in(
    template_surf_charge: str = 'pore_temp.in',
    
    #название параметра
    range_param: str = 'theta',
    min_val : float = 0.1,
    max_val : float = 0.1,
    
    Cs : float = 0.001,
    chi : float = 0.5,
    chi_surf : float = -0.6,
    
    N_layers : int = 200,
    N_brush1 : int = 30,
    N_brush2 : int = 30,
    
    S_total : float = 200.0,
    alpha : float = 0.5,
    
    surf_val : float = 0.5
    
    ):

    #Theta
    
    theta_brush1 = N_brush1/S_total
    theta_brush2 = N_brush2/S_total

    with open(template_surf_charge, 'r') as file:
        data = file.readlines()

    # Изменяем указанные параметры
    
    for str in range(len(data)):
        
        #Число слоев
        if 'lat : flat : n_layers' in data[str]:
            data[str] = f'lat : flat : n_layers : {N_layers}\n'
            
        elif 'mon : S0 : valence' in data[str]:
            data[str] = f'mon : S0 : valence : {surf_val}\n'
        
        #chi для поверхности
        elif 'mon : X0 : chi_S0' in data[str]:
            data[str] = f'mon : X0 : chi_S0 : {chi_surf}\n'
        elif 'mon : A : chi_S0' in data[str]:
            data[str] = f'mon : A : chi_S0 : {chi_surf}\n'
        elif 'mon : G : chi_S0' in data[str]:
            data[str] = f'mon : G : chi_S0 : {chi_surf}\n'
            
        elif 'mon : P0 : chi_S0' in data[str]:
            data[str] = f'mon : P0 : chi_S0 : {chi_surf}\n'
        elif 'mon : E : chi_S0' in data[str]:
            data[str] = f'mon : E : chi_S0 : {chi_surf}\n'
        
        #chi для растворителя
        elif 'mon : X0 : chi_W' in data[str]:
            data[str] = f'mon : X0 : chi_W : {chi}\n'
        elif 'mon : A : chi_W' in data[str]:
            data[str] = f'mon : A : chi_W : {chi}\n'
        elif 'mon : G : chi_W' in data[str]:
            data[str] = f'mon : G : chi_W : {chi}\n'
            
        elif 'mon : P0 : chi_W' in data[str]:
            data[str] = f'mon : P0 : chi_W : {chi}\n'
        elif 'mon : E : chi_W' in data[str]:
            data[str] = f'mon : E : chi_W : {chi}\n'
        
        #chi для натрия
        elif 'mon : X0 : chi_Na' in data[str]:
            data[str] = f'mon : X0 : chi_Na : {chi}\n'
        elif 'mon : A : chi_Na' in data[str]:
            data[str] = f'mon : A : chi_Na : {chi}\n'
        elif 'mon : G : chi_Na' in data[str]:
            data[str] = f'mon : G : chi_Na : {chi}\n'
        
        elif 'mon : P0 : chi_Na' in data[str]:
            data[str] = f'mon : P0 : chi_Na : {chi}\n'
        elif 'mon : E : chi_Na' in data[str]:
            data[str] = f'mon : E : chi_Na : {chi}\n'
        
        #chi для Cl
        elif 'mon : X0 : chi_Cl' in data[str]:
            data[str] = f'mon : X0 : chi_Cl : {chi}\n'
        elif 'mon : A : chi_Cl' in data[str]:
            data[str] = f'mon : A : chi_Cl : {chi}\n'
        elif 'mon : G : chi_Cl' in data[str]:
            data[str] = f'mon : G : chi_Cl : {chi}\n'
        
        elif 'mon : P0 : chi_Cl' in data[str]:
            data[str] = f'mon : P0 : chi_Cl : {chi}\n'
        elif 'mon : E : chi_Cl' in data[str]:
            data[str] = f'mon : E : chi_Cl : {chi}\n'
            
        # Валентность
        
        elif 'mon : X0 : valence' in data[str]:
            data[str] = f'mon : X0 : valence : {-alpha}\n'
        elif 'mon : A : valence' in data[str]:
            data[str] = f'mon : A : valence : {-alpha}\n'
        elif 'mon : G : valence' in data[str]:
            data[str] = f'mon : G : valence : {-alpha}\n'
        
        elif 'mon : P0 : valence' in data[str]:
            data[str] = f'mon : P0 : valence : {-alpha}\n'
        elif 'mon : E : valence' in data[str]:
            data[str] = f'mon : E : valence : {-alpha}\n'
        
        # Соль
        elif 'mol : Cl : phibulk' in data[str]:
            data[str] = f'mol : Cl : phibulk : {Cs}\n'
        
        #Композиция полимера
        elif 'mol : brush1  : composition' in data[str]:
            data[str] = f'mol : brush1  : composition : (X0)1(A){N_brush1 - 2}(G)1\n'
            
        elif 'mol : brush2  : composition' in data[str]:
            data[str] = f'mol : brush2  : composition : (P0)1(A){N_brush2 - 2}(E)1\n'
        
        # Плотность прививки
        elif 'mol : brush1 : theta' in data[str]:
            data[str] = f'mol : brush1 : theta : {theta_brush1}\n'
        elif 'mol : brush2 : theta' in data[str]:
            data[str] = f'mol : brush2 : theta : {theta_brush2}\n'

    # Создаем папку в зависимости от значения change_param
    
    folder_name = f'surfRange_{range_param}_from_{min_val}_to_{max_val}'
    folder_name_ = folder_name.replace('.', '_')
    
    if not os.path.exists(folder_name_):
        os.makedirs(folder_name_)

    # Записываем изменения обратно в файл
    
    file_name_prefix = f'surfRange_{range_param}'
    full_file_name = f'{file_name_prefix}_Cs_{round(Cs,5)}_s_val_{round(surf_val,2)}_N1_{N_brush1}_N2_{N_brush2}_theta1_{round(theta_brush1,2)}_chi_{chi}_alpha_{alpha}.in'
    
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
    folder_name_out = f'surfRange_out_{range_param}_{min_val}_to_{max_val}'
        
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