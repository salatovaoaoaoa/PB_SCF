import sys
import os
import subprocess
sys.path.append('/home/tpopova/prj/PB_SCF')

from math import pi

def create_in(
    template_surf_charge: str = 'pore_temp.in',
    
    #название параметра
    range_param: str = 'Cs',
    min_val : float = 0.1,
    max_val : float = 0.1,
    
    Cs : float = 0.001,
    chi :float = 0.5,
    chi_surf : float = -0.6,
    
    N_layers : int = 200,
    N : int = 30,
    S : float = 100.0,
    alpha : float = 0.5,
    Kuhn : str = '7e-09',
    
    ):

    #Theta
    theta = N/S

    with open(template_surf_charge, 'r') as file:
        data = file.readlines()

    # Изменяем указанные параметры
    
    for str in range(len(data)):
        
        #Число слоев
        if 'lat : flat : n_layers' in data[str]:
            data[str] = f'lat : flat : n_layers : {N_layers}\n'
        
        # сегмент Куна
        
        elif 'lat : flat : bondlength' in data[str]:
            data[str] = f'lat : flat : bondlength : {Kuhn}\n'
        
        #chi для поверхности
        elif 'mon : X0 : chi_S' in data[str]:
            data[str] = f'mon : X0 : chi_S : {chi_surf}\n'
        elif 'mon : A : chi_S' in data[str]:
            data[str] = f'mon : A : chi_S : {chi_surf}\n'
        elif 'mon : G : chi_S' in data[str]:
            data[str] = f'mon : G : chi_S : {chi_surf}\n'
        
        #chi для растворителя
        elif 'mon : X0 : chi_W' in data[str]:
            data[str] = f'mon : X0 : chi_W : {chi}\n'
        elif 'mon : A : chi_W' in data[str]:
            data[str] = f'mon : A : chi_W : {chi}\n'
        elif 'mon : G : chi_W' in data[str]:
            data[str] = f'mon : G : chi_W : {chi}\n'
        
        #chi для натрия
        elif 'mon : X0 : chi_Na' in data[str]:
            data[str] = f'mon : X0 : chi_Na : {chi}\n'
        elif 'mon : A : chi_Na' in data[str]:
            data[str] = f'mon : A : chi_Na : {chi}\n'
        elif 'mon : G : chi_Na' in data[str]:
            data[str] = f'mon : G : chi_Na : {chi}\n'
        
        #chi для Cl
        elif 'mon : X0 : chi_Cl' in data[str]:
            data[str] = f'mon : X0 : chi_Cl : {chi}\n'
        elif 'mon : A : chi_Cl' in data[str]:
            data[str] = f'mon : A : chi_Cl : {chi}\n'
        elif 'mon : G : chi_Cl' in data[str]:
            data[str] = f'mon : G : chi_Cl : {chi}\n'
            
        # Валентность
        
        elif 'mon : X0 : valence' in data[str]:
            data[str] = f'mon : X0 : valence : {alpha}\n'
        elif 'mon : A : valence' in data[str]:
            data[str] = f'mon : A : valence : {alpha}\n'
        elif 'mon : G : valence' in data[str]:
            data[str] = f'mon : G : valence : {alpha}\n'
        
        # Соль
        elif 'mol : Na : phibulk' in data[str]:
            data[str] = f'mol : Na : phibulk : {Cs}\n'
        
        #Композиция полимера
        elif 'mol : brush  : composition' in data[str]:
            data[str] = f'mol : brush  : composition : (X0)1(A){N - 2}(G)1\n'
        
        # Плотность прививки
        elif 'mol : brush : theta' in data[str]:
            data[str] = f'mol : brush : theta : {theta}\n'

    if alpha == 0:
        lines_to_remove = [
            f'mon : W: epsilon : 80\n',
            f'lat : flat : bondlength : {Kuhn}\n',
            f'mon : X0 : chi_Na : {chi}\n',
            f'mon : A : chi_Na : {chi}\n',
            f'mon : G : chi_Na : {chi}\n',
            f'mon : X0 : chi_Cl : {chi}\n',
            f'mon : A : chi_Cl : {chi}\n',
            f'mon : G : chi_Cl : {chi}\n',
            f'mon : X0 : valence : {alpha}\n',
            f'mon : A : valence : {alpha}\n',
            f'mon : G : valence : {alpha}\n',
            'mon : Na : valence : 1\n',
            'mon : Cl : valence : -1\n',
            'mol : Na : freedom : free\n',
            'mon : Cl : freedom : free\n',
            'mol : Na : composition : (Na)1\n',
            'mol : Cl : freedom : neutralizer\n',
            'mol : Cl : composition  : (Cl)1\n',
            'mol : Cl : freedom : free\n',
            f'mol : Na : phibulk : {Cs}\n',
            'pro : sys : noname : psi\n',
        ]
        data = [line for line in data if line not in lines_to_remove]

    # Создаем папку в зависимости от значения change_param
    
    folder_name = f'chiRange_{range_param}_from_{min_val}_to_{max_val}'
    folder_name_ = folder_name.replace('.', '_')
    
    if not os.path.exists(folder_name_):
        os.makedirs(folder_name_)

    # Записываем изменения обратно в файл
    
    file_name_prefix = f'chiRange_{range_param}'
    full_file_name = f'{file_name_prefix}_Cs_{round(Cs,5)}_N_{N}_S_{round(S,2)}_theta_{round(theta,2)}_chi_{chi}_alpha_{alpha}.in'
    
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
    folder_name_out = f'chiRange_out_{range_param}_{min_val}_to_{max_val}'
        
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