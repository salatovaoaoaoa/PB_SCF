from math import pi

def generate_in_file(filename,
                     D : int = 20,
                     L_pore : int = 10,
                     L_wall : int = 20,
                     space : int = 10,
                     N : int = 50,
                     S : int = 70,
                     Cs : float = 0.01,
                     valence : float = -0.5, 
                     chi_surf : float = -0.55,
                     chi_solv : float = 0.5):
    
    theta = 2 * pi * D * N * (1/S)
    
    with open(filename, 'w') as file:
        # Начальное содержимое
        file.write(f"""lat : cyl : geometry : cylindrical
lat : cyl : gradients : 2

lat : cyl : lattice_type : simple_cubic
lat : cyl : bondlength : 3e-10

lat : cyl : n_layers_x : {int(D + L_wall)}
lat : cyl : n_layers_y : {int(L_pore + 2 * space)}

//surface #2
mon : S : freedom : frozen
mon : S : frozen_range : {int(D + 1)},{int(space + 1)};{int(D + L_wall)},{space + L_pore}

//monomers

mon : W : freedom : free
mon : A : freedom : free
mon : E : freedom : free

mon : A : valence : {valence}
mon : E : valence : {valence}

// chi
mon : A : chi_S : {chi_surf}
mon : E : chi_S : {chi_surf}

mon : A : chi_W : {chi_solv}
mon : E : chi_W : {chi_solv}

mon : A : chi_Na : {chi_solv}
mon : E : chi_Na : {chi_solv}

mon : A : chi_Cl : {chi_solv}
mon : E : chi_Cl : {chi_solv}

//solution

mol : water : composition : (W)1
mol : water : freedom : solvent

mon : Na : valence : 1
mon : Cl : valence : -1

mon : Na : freedom : free
mon : Cl : freedom : free

mol : Na : composition  : (Na)1
mol : Na : freedom : neutralizer

mol : Cl : composition : (Cl)1
mol : Cl : freedom : free
mol : Cl : phibulk : {Cs}

//output

output : pro : append : false
output : pro : write_bounds : false

pro : sys : noname : psi
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
mon : X{i} : chi_Cl : {chi_solv}
mon : X{i} : chi_Na : {chi_solv}

mon : X{i} : valence : {valence}
mon : X{i} : freedom : pinned
mon : X{i} : pinned_range : {D},{int(space + 1 + i)};{D},{int(space + 1 + i)}
//chain{i}
"""
            file.write(block)

            
# Для поверхности доп:
# //surface #1
# //lat : cyl : upperbound_y : surface
# //mon : S : freedom : frozen
# //mon : S : frozen_range : {int(D)},{int(space + 1)};{int(D + L_wall)},{space + L_pore}
# //mon : S : frozen_range : upperbound_y

# Генерация файла
generate_in_file("2d_pore.in")
