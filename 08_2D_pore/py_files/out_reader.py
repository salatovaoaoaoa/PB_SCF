import pandas as pd
import numpy as np
from count_pro import count_pro
from config_loader import load_config

config = load_config()

def out_reader(valence=-0.5):
    cleaned_file_path = count_pro(**config)
    
    def add_combined_profile_to_file(file_path):
        df = pd.read_csv(file_path, sep='\t')
        phi_columns = [col for col in df.columns if col.startswith('mol_pol') and col.endswith('_phi')]
        df['combined_phi'] = df[phi_columns].sum(axis=1)
        df.to_csv(file_path, sep='\t', index=False)
        return df

    add_combined_profile_to_file(cleaned_file_path)
    
    df = pd.read_csv(cleaned_file_path, sep='\t')
    
    x = df['x']
    y = df['y']
    phi_brush = df['combined_phi']
    phi_end_brush = df['mon_E_phi']
    
    if valence != 0:
        psi = df['sys_noname_psi']
        return df, x, y, psi, phi_brush, phi_end_brush
    
    return df, x, y, phi_brush, phi_end_brush

def get_profiles_by_y_or_x(df, y_or_x_values, profiles_name='sys_noname_psi', groupby='y', coord='x', use_fraction=False):
    """
    Возвращает данные для построения любых профилей vs `x` для заданных значений `y` или центра списка значений `y`.
    
    Параметры:
    - df: DataFrame с данными
    - y_or_x_values: Скалярное значение или массив значений `y` или доля от длины уникальных значений
    - profiles_name: Столбец профиля для построения
    - groupby: Столбец, по которому будет производиться группировка ('y' или 'x')
    - coord: Координаты для построения ('x' или 'y')
    - use_fraction: Флаг, указывающий, что нужно использовать доли от общего числа уникальных значений
    
    Возвращает:
    - Словарь, где ключи - значения y или x, а значения - DataFrame с соответствующими x и sys_noname_psi
    """
    # Преобразуем y_or_x_values в список, если это не так
    if not isinstance(y_or_x_values, list):
        y_or_x_values = [y_or_x_values]
    
    result_get_profiles_by_y_or_x = {}
    
    unique_vals = sorted(df[groupby].unique())
    
    # Если включена работа с долями
    if use_fraction:
        # Вычисляем индексы для долей (считая от начала)
        indices = [int(len(unique_vals) * fraction) for fraction in y_or_x_values]
        
        # Находим центр массива
        center_index = len(unique_vals) // 2
        
        if len(unique_vals) % 2 == 0:
            # Если количество элементов четное, центр между двумя значениями
            indices = [center_index - 1 + int(len(unique_vals) * fraction) for fraction in y_or_x_values]
        else:
            # Для нечетного массива центр просто в середине
            indices = [center_index + int(len(unique_vals) * fraction) for fraction in y_or_x_values]
        
        # Ограничиваем индексы, чтобы они не выходили за пределы массива unique_vals
        indices = [min(max(0, idx), len(unique_vals) - 1) for idx in indices]
        
        # Получаем значения для указанных индексов
        y_or_x_values = [unique_vals[idx] for idx in indices]
    
    # Получаем данные для указанных значений
    for val, group in df.groupby(groupby):
        if val in y_or_x_values:
            result_get_profiles_by_y_or_x[val] = group[[coord, profiles_name]]
    
    return result_get_profiles_by_y_or_x