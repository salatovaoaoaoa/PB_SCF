import os
import sys
import subprocess

sys.path.append("/home/tpopova/prj/PB_SCF")

# Функции для обработки путей и файлов
def create_folder_and_get_path(base_name, params):
    """
    Создает папку и возвращает путь для нового файла.
    """
    folder_name = base_name.format(**params).replace(".", "_")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def create_file_path(folder_name, file_prefix, params):
    """
    Создает полный путь для нового файла.
    """
    file_name = f"{file_prefix.format(**params)}.in"
    return os.path.join(folder_name, file_name)

def move_files_from_output(output_folder, destination_folder):
    """
    Перемещает файлы из папки 'output' в целевую папку.
    """
    os.makedirs(destination_folder, exist_ok=True)
    files_in_output = os.listdir(output_folder)
    for file_in_output in files_in_output:
        file_path = os.path.join(output_folder, file_in_output)
        if os.path.isfile(file_path):
            new_file_path = os.path.join(destination_folder, file_in_output)
            os.rename(file_path, new_file_path)
    return os.path.join(destination_folder, files_in_output[-1])

# Основная функция
def files_pro_anneal(
    way: str = "/home/tpopova/prj/PB_SCF/templates/",
    template_name_anion: str = "annealing_anion_brush_temp.in",
    
    range_param: str = "dpK",
    min_range_value: float = 4,
    max_range_value: float = 4,
    
    N_brush: int = 200,
    S: int = 100,
    pK_brush: float = 5,
    Cs: float = 0.001,
    delta_pH_brush: float = None,
    pH_b: float = None,
    chi_solvent: float = 0.5,
    chi_surface: float = -0.6,
    type_brush: str = 'cation'
):
    if delta_pH_brush is not None:
        # Вычисление pH раствора
        pH_b_namics = pK_brush + delta_pH_brush
    else:
        pH_b_namics = pH_b
    
    # Параметры для щетки
    N_layers = N_brush + 20  # Число слоев
    theta = N_brush / S  # Угол

    # Чтение шаблона
    with open(f"{way}{template_name_anion}", "r") as file:
        data = file.readlines()

    # Подготовка параметров для имен папок и файлов
    params = {
        'range_param': range_param,
        'min_range_value': min_range_value,
        'max_range_value': max_range_value,
        'Cs': Cs,
        'N': N_brush,
        'N_layers': N_layers,
        'theta': theta,
        'pH_b_namics': pH_b_namics,
        'chi_solvent': chi_solvent,
        'type_brush': type_brush
    }

    # Словарь, где ключами являются строки для замены, а значениями - новые данные
    replacements = {
        "lat : flat : n_layers": f"lat : flat : n_layers : {N_layers}\n",
        "mol : brush  : composition": f"mol : brush  : composition : (X0)1(A){N_brush-2}(G)1\n",
        "mol : brush : theta": f"mol : brush : theta : {theta}\n",
        
        "mon : X0 : chi_W": f"mon : X0 : chi_W : {chi_solvent}\n",
        "mon : A : chi_W": f"mon : A : chi_W : {chi_solvent}\n",
        "mon : G : chi_W": f"mon : G : chi_W : {chi_solvent}\n",
        
        "mon : X0 : chi_S": f"mon : X0 : chi_S : {chi_surface}\n",
        "mon : A : chi_S": f"mon : A : chi_S : {chi_surface}\n",
        "mon : G : chi_S": f"mon : G : chi_S : {chi_surface}\n",
        
        "mon : X0 : chi_P": f"mon : X0 : chi_P : {chi_solvent}\n",
        "mon : A : chi_P": f"mon : A : chi_P : {chi_solvent}\n",
        "mon : G : chi_P": f"mon : G : chi_P : {chi_solvent}\n",
        
        "mon : X0 : chi_M": f"mon : X0 : chi_M : {chi_solvent}\n",
        "mon : A : chi_M": f"mon : A : chi_M : {chi_solvent}\n",
        "mon : G : chi_M": f"mon : G : chi_M : {chi_solvent}\n",
        
        "mol : Na : phibulk": f"mol : Na : phibulk : {Cs}\n",
        "mol : Cl : phibulk": f"mol : Cl : phibulk : {Cs}\n",
        
        "reaction : weak : pK": f"reaction : weak : pK : {pK_brush}\n",
        "state : H3O : alphabulk": f"state : H3O : alphabulk : {(1 + 10**(pH_b_namics))**(-1)}\n",
    }

    # Заменяем строки в данных согласно словарю
    for i in range(len(data)):
        for key, value in replacements.items():
            if key in data[i]:
                data[i] = value

    # Общий шаблон для создания папок
    folder_base_name = "{type_brush}_range_{range_param}_from_{min_range_value}_to_{max_range_value}"

    # Создание папки для входных данных
    folder_name_in = create_folder_and_get_path(f"in_anneal_{folder_base_name}", params)

    # Запись данных в новый файл
    file_prefix = "file_anneal_{type_brush}_range_{range_param}_{min_range_value}_{max_range_value}_{pH_b_namics}_{Cs}"
    new_file_path = create_file_path(folder_name_in, file_prefix, params)
    
    with open(new_file_path, "w") as file:
        file.writelines(data)

    # Запуск симуляции
    subprocess.call(["namics", os.path.abspath(new_file_path)])

    # Создание папки для выходных файлов
    folder_name_out = create_folder_and_get_path(f"pro_anneal_{folder_base_name}", params)

    # Перемещаем файлы из папки "output"
    file_name_pro = move_files_from_output("output", folder_name_out)

    return file_name_pro
