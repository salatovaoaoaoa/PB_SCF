import os
import subprocess
import shutil
import logging
from config_loader import load_config
from generate_in_file import generate_in_file

config = load_config()

def count_pro(range_param, min_val, max_val, output_dir, target_dir, D, L_pore, L_wall,
              space, N, S, Cs, valence, chi_surf, chi_solv):
    
    # Генерация in файла
    file_in_path = generate_in_file(**config)
    
    # Запуск NAMICS
    try:
        subprocess.check_call(['namics', os.path.abspath(file_in_path)])
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при выполнении NAMICS: {e}")
        raise
    
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