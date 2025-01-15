import os
import yaml
import logging

# Логирование настроек
logging.basicConfig(level=logging.INFO)

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

def load_config(config_path=None, root_dir="/home/tpopova/prj/PB_SCF/08_2D_pore"):
    """
    Загружает конфигурацию из файла. Если путь не указан, ищет config.yaml в указанной директории.
    
    :param config_path: Путь к файлу конфигурации.
    :param root_dir: Корневая директория для поиска config.yaml.
    :return: Словарь с конфигурацией.
    """
    if config_path is None:
        # Ищем файл config.yaml в заданной директории
        config_path = find_config_file(root_dir=root_dir, file_name="config.yaml")
        if config_path is None:
            logging.error(f"Файл config.yaml не найден в папке {root_dir} или её подпапках.")
            raise FileNotFoundError("Файл config.yaml не найден.")
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logging.info(f"Конфигурация успешно загружена из {config_path}")
        return config
    except Exception as e:
        logging.error(f"Ошибка при загрузке конфигурации из {config_path}: {e}")
        raise

def save_config(config, config_path=None, root_dir="/home/tpopova/prj/PB_SCF/08_2D_pore"):
    """
    Сохраняет обновлённую конфигурацию обратно в YAML файл.
    
    :param config: Словарь с новой конфигурацией.
    :param config_path: Путь к файлу конфигурации.
    :param root_dir: Корневая директория для поиска config.yaml.
    """
    if config_path is None:
        # Ищем файл config.yaml в заданной директории
        config_path = find_config_file(root_dir=root_dir, file_name="config.yaml")
        if config_path is None:
            logging.error(f"Файл config.yaml не найден в папке {root_dir} или её подпапках.")
            raise FileNotFoundError("Файл config.yaml не найден.")
    
    try:
        with open(config_path, 'w') as file:
            yaml.safe_dump(config, file)
        logging.info(f"Конфигурация успешно сохранена в {config_path}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении конфигурации в {config_path}: {e}")
        raise

def update_config_param(config, param, value):
    """
    Обновляет конкретный параметр в конфигурации.
    
    :param config: Словарь с конфигурацией.
    :param param: Ключ параметра, который нужно обновить.
    :param value: Новое значение для параметра.
    :return: Обновлённая конфигурация.
    """
    if param in config:
        logging.info(f"Обновление параметра {param} на {value}")
        config[param] = value
    else:
        logging.warning(f"Параметр {param} не найден в конфигурации.")
    
    return config