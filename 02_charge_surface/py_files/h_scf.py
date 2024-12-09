import numpy as np

def h_scf(dens_pol_profile = np.asarray([0, 1, 2])):
    
        # Нахожу площадь под кривой
    def calculate_area(c_pol):
        area = np.trapz(c_pol)
        return area

    def find_index(values, target_percentage=0.999):
        total_area = calculate_area(values)
        target_area = total_area * target_percentage
        current_area = 0

        for i in range(len(values)):
            # Вычисляю площадь до текущего элемента
            current_area += (values[i] + (values[i+1] if i+1 < len(values) else 0)) / 2 if i+1 < len(values) else (values[i]) * (1 if i+1 < len(values) else 0)
            
            if current_area >= target_area:
                return i
        return -1  # Если не найден индекс

    index = find_index(dens_pol_profile)

    return index