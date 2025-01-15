import os
import shutil
from math import pi

def generate_in_file(
    output_dir="2D_pore_in_files",  # Каталог для сохранения файлов
    target_dir="/home/tpopova/prj/PB_SCF/08_2D_pore/scf_templates",  # Путь для перемещения
    D: int = 20,
    L_pore: int = 10,
    L_wall: int = 20,
    space: int = 10,
    N: int = 50,
    S: int = 70,
    Cs: float = 0.01,
    valence: float = -0.5, 
    chi_surf: float = -0.55,
    chi_solv: float = 0.5
):
    # Создаём директорию, если её нет
    os.makedirs(output_dir, exist_ok=True)
    
    theta = 2 * pi * D * N * (1 / S)

    # Генерация имени файла
    base_filename = f"2D_v_{valence}_D_{D}_N_{N}_theta_{theta:.2f}.in"
    
    # Разделяем строку на части до и после последней точки
    base_filename_parts = base_filename.rsplit('.', 1)

    # Заменяем все точки на подчеркивания в первой части
    base_filename_parts[0] = base_filename_parts[0].replace('.', '_')

    # Собираем строку обратно, добавив точку между частями
    base_filename = '.'.join(base_filename_parts)
    
    filename = os.path.join(output_dir, base_filename)
    
    with open(filename, 'w') as file:
        # Общее для любого случая (заряженный или незаряженный)
        file.write(f"""lat : cyl : geometry : cylindrical
lat : cyl : gradients : 2

lat : cyl : lattice_type : simple_cubic

lat : cyl : n_layers_x : {int(D + L_wall)}
lat : cyl : n_layers_y : {int(L_pore + 2 * space)}

//surface #2
mon : S : freedom : frozen
mon : S : frozen_range : {int(D + 1)},{int(space + 1)};{int(D + L_wall)},{space + L_pore}

//monomers

mon : W : freedom : free
mon : A : freedom : free
mon : E : freedom : free

// chi
mon : A : chi_S : {chi_surf}
mon : E : chi_S : {chi_surf}

mon : A : chi_W : {chi_solv}
mon : E : chi_W : {chi_solv}

//solution

mol : water : composition : (W)1
mol : water : freedom : solvent

//output

output : pro : append : false
output : pro : write_bounds : false

pro : mon : E : phi

newton : isaac : method : pseudohessian
newton : isaac : iterationlimit : 10000000
newton : isaac : tolerance : 1e-8
newton : isaac : deltamax : 0.1

// chains
""")
        # Генерация блоков pol
        for i in range(0, L_pore):
            block = f"""
//chain{i}
mol : pol{i} : composition : (X{i})1(A){N - 2}(E)1
mol : pol{i} : freedom : restricted
mol : pol{i} : theta : {theta}

pro : mol : pol{i} : phi

mon : X{i} : chi_S : {chi_surf}
mon : X{i} : chi_W : {chi_solv}

mon : X{i} : freedom : pinned
mon : X{i} : pinned_range : {D},{int(space + 1 + i)};{D},{int(space + 1 + i)}
//chain{i}
"""
            file.write(block)

        if valence != 0:
            charge_append = f"""
lat : cyl : bondlength : 3e-10
mon : A : valence : {valence}
mon : E : valence : {valence}
mon : A : chi_Na : {chi_solv}
mon : E : chi_Na : {chi_solv}

mon : A : chi_Cl : {chi_solv}
mon : E : chi_Cl : {chi_solv}
mon : Na : valence : 1
mon : Cl : valence : -1

mon : Na : freedom : free
mon : Cl : freedom : free

mol : Na : composition  : (Na)1
mol : Na : freedom : neutralizer

mol : Cl : composition : (Cl)1
mol : Cl : freedom : free
mol : Cl : phibulk : {Cs}
pro : sys : noname : psi
"""
            file.write(charge_append)
            
            # Генерация блоков pol (charge Xi)
            for i in range(0, L_pore):
                block_charge = f"""
//chain{i}
mon : X{i} : chi_Cl : {chi_solv}
mon : X{i} : chi_Na : {chi_solv}
mon : X{i} : valence : {valence}
//chain{i}
"""
                file.write(block_charge)
    
    # Проверяем, существует ли уже папка
    target_folder = os.path.join(target_dir, os.path.basename(output_dir))

    # Если папка существует, удаляем её
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)

    # Перемещаем новую папку в целевой каталог
    shutil.move(output_dir, target_dir)

    # Путь до файла
    file_in_path = os.path.join(target_dir, os.path.basename(output_dir), base_filename)
    
    return file_in_path
