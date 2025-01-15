import os
import shutil
from math import pi
import logging

def generate_in_file(
    range_param, min_val, max_val, output_dir, target_dir, D, L_pore, L_wall, space,
    N, S, Cs, valence, chi_surf, chi_solv
):
    """
    Генерирует файл входных данных для NAMICS и сохраняет его в указанный каталог.
    
    :param range_param: Параметр диапазона, используется в названии файла.
    :param min_val: Минимальное значение для диапазона.
    :param max_val: Максимальное значение для диапазона.
    :param output_dir: Директория для сохранения файла.
    :param target_dir: Директория, куда переместить результат.
    :param D: Радиус поры.
    :param L_pore: Длина поры.
    :param L_wall: Длина стенки.
    :param space: отступы от поры.
    :param N: Степень полимеризации
    :param Cs: Концентрация соли.
    :param valence: Заряд мономера.
    :param chi_surf: качество растворителя.
    :param chi_solv: качество растворителя.
    :return: Путь к сгенерированному файлу.
    """
    # Создание выходной директории, если она не существует
    os.makedirs(output_dir, exist_ok=True)

    # Вычисляем угол theta
    theta = 2 * pi * D * N * (1 / S)

    # Генерация имени файла
    base_filename = f"2D_v_{valence}_D_{D}_N_{N}_theta_{theta:.2f}.in"
    base_filename = base_filename.replace('.', '_', base_filename.count('.') - 1)

    # Путь к файлу
    filename = os.path.join(output_dir, base_filename)

    try:
        with open(filename, 'w') as file:
            # Запись общих настроек
            file.write(f"""lat : cyl : geometry : cylindrical
lat : cyl : gradients : 2
lat : cyl : lattice_type : simple_cubic
lat : cyl : n_layers_x : {int(D + L_wall)}
lat : cyl : n_layers_y : {int(L_pore + 2 * space)}""")

            # Генерация блоков для монологов
            file.write(f"""
//surface #2
mon : S : freedom : frozen
mon : S : frozen_range : {int(D + 1)},{int(space + 1)};{int(D + L_wall)},{space + L_pore}""")
            
            # Генерация блоков для молекул
            file.write(f"""
mon : W : freedom : free
mon : A : freedom : free
mon : E : freedom : free""")
            
            # Запись chi значений
            file.write(f"""
mon : A : chi_S : {chi_surf}
mon : E : chi_S : {chi_surf}

mon : A : chi_W : {chi_solv}
mon : E : chi_W : {chi_solv}""")

            # Запись данных для раствора
            file.write(f"""
mol : water : composition : (W)1
mol : water : freedom : solvent""")

            # Запись output данных
            file.write(f"""
output : pro : append : false
output : pro : write_bounds : false

pro : mon : E : phi

newton : isaac : method : pseudohessian
newton : isaac : iterationlimit : 10000000
newton : isaac : tolerance : 1e-8
newton : isaac : deltamax : 0.1

// chains""")
            
            # Генерация цепочек
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

            # Если валентность не равна нулю, добавляем дополнительные блоки
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

                # Генерация блоков для зарядов Xi
                for i in range(0, L_pore):
                    block_charge = f"""
//chain{i}
mon : X{i} : chi_Cl : {chi_solv}
mon : X{i} : chi_Na : {chi_solv}
mon : X{i} : valence : {valence}
//chain{i}
"""
                    file.write(block_charge)
        
        logging.info(f"Файл {base_filename} успешно создан в {output_dir}")
    except Exception as e:
        logging.error(f"Ошибка при создании файла {base_filename}: {e}")
        raise

    # Проверяем, существует ли уже папка в целевом каталоге
    target_folder = os.path.join(target_dir, os.path.basename(output_dir))

    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)

    # Перемещаем выходную папку в целевой каталог
    shutil.move(output_dir, target_dir)

    # Путь до сгенерированного файла
    file_in_path = os.path.join(target_dir, os.path.basename(output_dir), base_filename)
    return file_in_path