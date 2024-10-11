import sys
import os
import subprocess

sys.path.append("/home/tpopova/prj/PB_SCF")


def generate_in_files(
    template_anion: str = "annealing_anion_brush_temp.in",
    template_cation: str = "annealing_anion_brush_temp.in",
    template_quecnhed: str = "quecnhed_brush_temp.in",
    
    # Какой шаблон меняем?
    current_name: str = "annealing_anion_brush_temp.in",
    way: str = "/home/tpopova/prj/PB_SCF/templates/",
    
    # название параметра
    range_param: str = "dpK",
    range_param_q: str = "dpK",
    min_range_value: float = 4,
    max_range_value: float = 4,
    
    N_brush: int = 200,
    S: int = 100,
    pK_brush: float = 5,
    Cs: float = 0.001,
    delta_pK: float = 0.8,
    alpha_z_average: float = 0.5,
    chi: float = 0.5
):

    # какие параметры меняем? TODO 
    change_param_annealing = delta_pK
    change_param_quenched = alpha_z_average
    
    #pH для щеток
    
    pH_b = pK_brush + delta_pK
    
    if current_name == template_anion:
        pH_namics = (1 + 10 ** (pH_b)) ** (-1)
    else:
        pH_namics = (1 + 10 ** (14-pH_b)) ** (-1)

    # число слоев
    N_layers = N_brush + 20

    theta = N_brush / S

    with open(f"{way}{current_name}", "r") as file:
        data = file.readlines()

    # Изменяем указанные параметры
    for str in range(len(data)):
        if "state : H3O : alphabulk" in data[str]:
            data[str] = f"state : H3O : alphabulk : {pH_namics}\n"
        if "state : OH : alphabulk" in data[str]:
            data[str] = f"state : OH : alphabulk : {pH_namics}\n"
        if "lat : flat : n_layers" in data[str]:
            data[str] = f"lat : flat : n_layers : {N_layers}\n"
        if "reaction : weak : pK" in data[str]:
            data[str] = f"reaction : weak : pK : {pK_brush}\n"
        if "mol : Na : phibulk" in data[str]:
            data[str] = f"mol : Na : phibulk : {Cs}\n"
        if "mol : Cl : phibulk" in data[str]:
            data[str] = f"mol : Cl : phibulk : {Cs}\n"
        if "mol : brush  : composition" in data[str]:
            data[str] = f"mol : brush  : composition : (X0)1(A){N_brush-2}(G)1\n"
        if "mol : brush : theta" in data[str]:
            data[str] = f"mol : brush : theta : {theta}\n"
        
        if "mon : X0 : chi_W" in data[str]:
            data[str] = f"mon : X0 : chi_W : {chi}\n"
        if "mon : A : chi_W" in data[str]:
            data[str] = f"mon : A : chi_W : {chi}\n"
        if "mon : G : chi_W" in data[str]:
            data[str] = f"mon : G : chi_W : {chi}\n"
        
        if "mon : X0 : chi_P" in data[str]:
            data[str] = f"mon : X0 : chi_P : {chi}\n"
        if "mon : A : chi_P" in data[str]:
            data[str] = f"mon : A : chi_P : {chi}\n"
        if "mon : G : chi_P" in data[str]:
            data[str] = f"mon : G : chi_P : {chi}\n"
        
        if "mon : X0 : chi_M" in data[str]:
            data[str] = f"mon : X0 : chi_M : {chi}\n"
        if "mon : A : chi_M" in data[str]:
            data[str] = f"mon : A : chi_M : {chi}\n"
        if "mon : G : chi_M" in data[str]:
            data[str] = f"mon : G : chi_M : {chi}\n"

        # Quenched brush
        if "mon : A : valence" in data[str]:
            data[str] = f"mon : A : valence : {-1 * alpha_z_average}\n"
        if "mon : G : valence" in data[str]:
            data[str] = f"mon : G : valence : {-1 * alpha_z_average}\n"
        if "mon : X0 : valence" in data[str]:
            data[str] = f"mon : X0 : valence : {-1 * alpha_z_average}\n"

    # Создаем папку в зависимости от значения current_name
    folder_name = (
        f"FD_annealing_range_{range_param}_from_{min_range_value}_to_{max_range_value}"
        if current_name == template_anion
        else f"FD_quecnhed_range_{range_param_q}_from_{min_range_value}_to_{max_range_value}"
    )
    folder_name_ = folder_name.replace(".", "_")
    if not os.path.exists(folder_name_):
        os.makedirs(folder_name_)

    # Записываем изменения обратно в файл

    file_name_prefix = (
        f"F_annealing_range_{range_param}_{round(change_param_annealing, 4)}"
        if current_name == template_anion
        else f"F_quenched_range_{range_param_q}_{round(change_param_quenched, 4)}"
    )
    new_file_path = os.path.join(
        folder_name_,
        f"{file_name_prefix}_pH_b_{pH_b}_Cs_{Cs}_N_{N_brush}_theta_{theta}.in",
    ).replace(".", "_", 3)
    with open(new_file_path, "w") as file:
        file.writelines(data)

    # Считает намикс
    subprocess.call(["namics", os.path.abspath(new_file_path)])

    # Переносим посчитанные файлы

    # Создаем папку, где будут храниться output файлы
    folder_name_out = (
        f"FD_anneal_outfiles_range_{range_param}_from_{min_range_value}_to_{max_range_value}"
        if current_name == template_anion
        else f"FD_quecnhed_outfiles_range_{range_param_q}_from_{min_range_value}_to_{max_range_value}"
    )

    # заменяем все точки на _
    folder_name_out__ = folder_name_out.replace(".", "_")
    os.makedirs(f"{folder_name_out__}", exist_ok=True)
    # Получаем список файлов в папке "output"
    files_in_output = os.listdir("output")
    # Путь до созданной папки
    to_folder_out = os.path.abspath(f"{folder_name_out__}")

    # Перемещаем каждый файл в созданную папку
    for file_in_output in files_in_output:
        file_path = os.path.join("output", file_in_output)
        if os.path.isfile(file_path):
            new_file_path = os.path.join(to_folder_out, file_in_output)
            os.rename(file_path, new_file_path)

    file_name_pro = os.path.join(to_folder_out, file_in_output)

    return file_name_pro
