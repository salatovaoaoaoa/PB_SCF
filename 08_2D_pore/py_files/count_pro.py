import subprocess
import os
import pandas as pd
import sys

sys.path.append('/home/tpopova/prj/PB_SCF/08_2D_pore/py_files')
from generate_in_file import generate_in_file

def count_pro(
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
    # Генерирую in файл
    file_in_path = generate_in_file(
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
        chi_solv=chi_solv
    )
    
    # Запуск NAMICS
    subprocess.call(['namics', os.path.abspath(file_in_path)])
    
    # Создание папки для вывода
    folder_name_out = f'2Dout_{range_param}_{min_val}_to_{max_val}'.replace('.', '_')
    os.makedirs(folder_name_out, exist_ok=True)
    
    # Получение имени единственного файла в output
    output_files = os.listdir('output')
    if len(output_files) != 1:
        raise ValueError("В папке 'output' ожидается только один файл.")
    
    file_name_pro = os.path.join('output', output_files[0])  # Путь к единственному файлу
    new_file_path = os.path.join(folder_name_out, output_files[0])  # Новый путь после переноса
    os.rename(file_name_pro, new_file_path)  # Перенос файла в новую папку
    
    # Очистка данных в .pro файле
    cleaned_file_path = os.path.join(folder_name_out, f"{output_files[0]}")
    with open(new_file_path, 'r') as file:
        lines = file.readlines()
    
    # Обработка заголовка и строк
    header = lines[0].strip().split("\t")
    cleaned_lines = []
    for line in lines[1:]:
        columns = line.strip().split("\t")
        cleaned_columns = columns[:len(header)]  # Убираем лишние столбцы
        cleaned_lines.append("\t".join(cleaned_columns))
    
    # Запись очищенного файла
    with open(cleaned_file_path, 'w') as file:
        file.write("\t".join(header) + "\n")
        file.writelines("\n".join(cleaned_lines))
    
    # Возврат пути к очищенному файлу
    return cleaned_file_path