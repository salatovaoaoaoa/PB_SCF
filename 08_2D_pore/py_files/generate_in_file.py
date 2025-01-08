def generate_in_file(filename, D = 100, L_pore = 100, N = 300, theta = 1130):
    with open(filename, 'w') as file:
        # Начальное содержимое
        file.write(f"""lat : cyl : geometry : cylindrical
lat : cyl : gradients : 2

lat : cyl : lattice_type : simple_cubic
lat : cyl : bondlength : 3e-10

lat : cyl : n_layers_x : {D * 1.3}
lat : cyl : n_layers_y : {L_pore + 2 * L_pore * 0.3}

//surface
lat : cyl : upperbound_y : surface
mon : S : freedom : frozen
mon : S : frozen_range : 22,31;24,70
//mon : S : frozen_range : upperbound_y

//monomers

mon : W : freedom : free
mon : A : freedom : free
mon : E : freedom : free

mon : A : valence : -0.5
mon : E : valence : -0.5

// chi
mon : A : chi_S : -0.55
mon : E : chi_S : -0.55

mon : A : chi_W : 0.5
mon : E : chi_W : 0.5

mon : A : chi_Na : 0.5
mon : E : chi_Na : 0.5

mon : A : chi_Cl : 0.5
mon : E : chi_Cl : 0.5

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
mol : Cl : phibulk : 0.008s

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

        # Генерация блоков от pol0 до pol39 (длина поры - 1)
        for i in range(0, L_pore):
            block = f"""
//chain{i}
mol : pol{i} : composition : (X{i})1(A){N - 2}(E)1
mol : pol{i} : freedom : restricted
mol : pol{i} : theta : {theta}

pro : mol : pol{i} : phi

mon : X{i} : chi_S : -0.55
mon : X{i} : chi_W : 0.5
mon : X{i} : chi_Cl : 0.5
mon : X{i} : chi_Na : 0.5

mon : X{i} : valence : -0.5
mon : X{i} : freedom : pinned
mon : X{i} : pinned_range : {D+1},{L_pore * 0.3 + 1 + i};{D+1},{L_pore * 0.3 + 1 + i}
//chain{i}
"""
            file.write(block)

# Генерация файла
generate_in_file("2d_pore.in")
