import os
import yaml
import logging

def find_config_file(root_dir=".", file_name="config.yaml"):
    """
    Ищет файл с указанным именем во всех подпапках указанной директории.
    
    :param root_dir: Корневая директория для поиска.
    :param file_name: Имя файла для поиска.
    :return: Путь к найденному файлу или None, если файл не найден.
    """
    for dirpath, _, filenames in os.walk(root_dir):
        if file_name in filenames:
            return os.path.join(dirpath, file_name)
    return None

def load_config(config_path=None):
    """
    Загружает конфигурацию из файла. Если путь не указан, ищет config.yaml в текущей директории.
    
    :param config_path: Путь к файлу конфигурации.
    :return: Словарь с конфигурацией.
    """
    if config_path is None:
        # Ищем файл config.yaml во всей папке 08_2D_pore
        config_path = find_config_file(root_dir="/home/tpopova/prj/PB_SCF/08_2D_pore", file_name="config.yaml")
        if config_path is None:
            logging.error("Файл config.yaml не найден в папке 08_2D_pore или её подпапках.")
            raise FileNotFoundError("Файл config.yaml не найден.")
    
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)