import yaml
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load_config(file_path:str=os.path.join(BASE_DIR,'config_01','config.yml')):
    with open(file_path,'r') as file:
        config = yaml.safe_load(file)

    return config