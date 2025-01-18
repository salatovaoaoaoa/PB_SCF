import sys
import os
import subprocess
from math import pi

sys.path.append('/home/tpopova/prj/PB_SCF')


def create_in(
    range_param: str = 'Cs',
    min_val: float = 0.1,
    max_val: float = 0.1,
    Cs: float = 0.001,
    chi_first_try: float = 0.5,
    chi_ions_first_try: float = 0.5,
    chi_surf_first_try: float = -0.6,
    N_layers_first_try: int = 200,
    N_first_try: int = 30,

    S: float = 100.0,
    alpha: float = 0.5,
    Kuhn: str = '7e-09',
    initial_cond: bool = True,
    
    N_layers: int = 200,
    N: int = 30,
    chi: float = 0.5,
    chi_ions: float = 0.5,
    chi_surf: float = -0.6,
    
    # epsilon: float = 80,
):
    theta_first_try = N_first_try / S
    theta = N / S
    
#     mon : W: epsilon : {epsilon}
# mon : Na: epsilon : {epsilon}
# mon : Cl: epsilon : {epsilon}

# mon : X0: epsilon : {epsilon}
# mon : A: epsilon : {epsilon}
# mon : G: epsilon : {epsilon}

    # Контент для initial_cond = True
    content_true = f"""
lat : flat : geometry : planar
lat : flat : gradients : 1
lat : flat : n_layers : {N_layers_first_try}
lat : flat : lattice_type : simple_cubic
lat : flat : bondlength : {Kuhn}
lat : flat : lowerbound : surface

mon : S : freedom : frozen
mon : S : frozen_range : lowerbound

mon : X0 : freedom : pinned
mon : X0 : pinned_range : 1;1

mon : W : freedom : free
mon : A : freedom : free
mon : G : freedom : free

mon : X0 : chi_S : {chi_surf_first_try}
mon : A : chi_S : {chi_surf_first_try}
mon : G : chi_S : {chi_surf_first_try}

mon : X0 : chi_W : {chi_first_try}
mon : A : chi_W : {chi_first_try}
mon : G : chi_W : {chi_first_try}

mon : X0 : chi_Na : {chi_ions_first_try}
mon : A : chi_Na : {chi_ions_first_try}
mon : G : chi_Na : {chi_ions_first_try}

mon : X0 : chi_Cl : {chi_ions_first_try}
mon : A : chi_Cl : {chi_ions_first_try}
mon : G : chi_Cl : {chi_ions_first_try}

mon : X0 : valence : {alpha}
mon : A : valence : {alpha}
mon : G : valence : {alpha}

mon : Na : valence : 1
mon : Cl : valence : -1

mon : Na : freedom : free
mon : Cl : freedom : free

mol : Cl : composition  : (Cl)1
mol : Cl : freedom : neutralizer

mol : Na : composition : (Na)1
mol : Na : freedom : free
mol : Na : phibulk : {Cs}

mol : water : composition : (W)1
mol : water : freedom : solvent

mol : brush  : composition : (X0)1(A){N_first_try - 2}(G)1
mol : brush : freedom : restricted
mol : brush : theta : {theta_first_try}

newton : isaac : method : pseudohessian
newton : isaac : iterationlimit : 10000000
newton : isaac : tolerance : 1e-8
newton : isaac : deltamax : 0.1

start

sys : chi_flat : initial_guess : previous_result

lat : flat : n_layers : {N_layers}
mol : brush  : composition : (X0)1(A){N - 2}(G)1
mol : brush : theta : {theta}

mon : X0 : chi_S : {chi_surf}
mon : A : chi_S : {chi_surf}
mon : G : chi_S : {chi_surf}

mon : X0 : chi_W : {chi}
mon : A : chi_W : {chi}
mon : G : chi_W : {chi}

mon : X0 : chi_Na : {chi_ions}
mon : A : chi_Na : {chi_ions}
mon : G : chi_Na : {chi_ions}

mon : X0 : chi_Cl : {chi_ions}
mon : A : chi_Cl : {chi_ions}
mon : G : chi_Cl : {chi_ions}

output : pro : append : false
output : pro : write_bounds : false

pro : sys : noname : psi
pro : mol : brush : phi
pro : mon : G : phi
pro : mol : Na : phi
pro : mol : Cl : phi
"""

    # Контент для initial_cond = False
    content_false = f"""
lat : flat : geometry : planar
lat : flat : gradients : 1
lat : flat : n_layers : {N_layers}
lat : flat : lattice_type : simple_cubic
lat : flat : bondlength : {Kuhn}
lat : flat : lowerbound : surface

mon : S : freedom : frozen
mon : S : frozen_range : lowerbound

mon : X0 : freedom : pinned
mon : X0 : pinned_range : 1;1

mon : W : freedom : free
mon : A : freedom : free
mon : G : freedom : free

mon : X0 : chi_S : {chi_surf}
mon : A : chi_S : {chi_surf}
mon : G : chi_S : {chi_surf}

mon : X0 : chi_W : {chi}
mon : A : chi_W : {chi}
mon : G : chi_W : {chi}

mon : X0 : chi_Na : {chi_ions}
mon : A : chi_Na : {chi_ions}
mon : G : chi_Na : {chi_ions}

mon : X0 : chi_Cl : {chi_ions}
mon : A : chi_Cl : {chi_ions}
mon : G : chi_Cl : {chi_ions}

mon : X0 : valence : {alpha}
mon : A : valence : {alpha}
mon : G : valence : {alpha}

mon : Na : valence : 1
mon : Cl : valence : -1

mon : Na : freedom : free
mon : Cl : freedom : free

mol : Cl : composition  : (Cl)1
mol : Cl : freedom : neutralizer

mol : Na : composition : (Na)1
mol : Na : freedom : free
mol : Na : phibulk : {Cs}

mol : water : composition : (W)1
mol : water : freedom : solvent

mol : brush  : composition : (X0)1(A){N - 2}(G)1
mol : brush : freedom : restricted
mol : brush : theta : {theta}

output : pro : append : false
output : pro : write_bounds : false

pro : sys : noname : psi
pro : mol : brush : phi
pro : mon : G : phi
pro : mol : Na : phi
pro : mol : Cl : phi

newton : isaac : method : pseudohessian
newton : isaac : iterationlimit : 10000000
newton : isaac : tolerance : 1e-8
newton : isaac : deltamax : 0.1
"""

    # Выбор контента
    content = content_true if initial_cond else content_false

    # Если alpha == 0, удаляем определенные строки
    if alpha == 0:
        lines_to_remove = [
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
            'mon : Na : freedom : free\n',
            'mon : Cl : freedom : free\n',
            'mol : Na : composition : (Na)1\n',
            'mol : Cl : freedom : neutralizer\n',
            'mol : Cl : composition  : (Cl)1\n',
            'mol : Cl : freedom : free\n',
            f'mol : Na : phibulk : {Cs}\n',
            'pro : sys : noname : psi\n',
        ]
        content = "\n".join([line for line in content.splitlines(keepends=True) if line not in lines_to_remove])

    # Создание папки
    folder_name = f'range_{range_param}_from_{min_val}_to_{max_val}'
    folder_name_ = folder_name.replace('.', '_')

    if not os.path.exists(folder_name_):
        os.makedirs(folder_name_)

    def replace_all_except_last(s, old, new):
        # Разделяем строку на две части: до последней точки и после неё
        parts = s.rsplit('.', 1)
        
        # Заменяем все старые значения на новые в первой части
        parts[0] = parts[0].replace(old, new)
        
        # Возвращаем обратно, соединяя обе части с последней точкой
        return '.'.join(parts)

    # Имя выходного файла
    file_name_prefix = f'range_{range_param}'
    full_file_name = f'{file_name_prefix}_Cs_{round(Cs, 5)}_N_{N}_S_{round(S, 2)}_theta_{round(theta, 2)}_chi_{chi}_alpha_{alpha}.in'
    result = replace_all_except_last(full_file_name, '.', '_')

    new_file_path = os.path.join(folder_name_, result)

    # Запись файла
    with open(new_file_path, 'w') as file:
        file.write(content)

    # Запуск subprocess
    subprocess.call(['namics', os.path.abspath(new_file_path)])

    # Перенос output файлов
    folder_name_out = f'range_out_{range_param}_{min_val}_to_{max_val}'.replace('.', '_')
    os.makedirs(folder_name_out, exist_ok=True)
    files_in_output = os.listdir('output')

    for file_in_output in files_in_output:
        file_path = os.path.join('output', file_in_output)
        if os.path.isfile(file_path):
            new_file_path = os.path.join(folder_name_out, file_in_output)
            os.rename(file_path, new_file_path)

    # Возвращаем путь к выходному файлу
    return new_file_path