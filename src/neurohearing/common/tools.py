import yaml

def load_config():
    # Read in the configuration file
    with open('config.yaml') as p:
        config = yaml.safe_load(p)
    return config

def parse_list(arg_str):
    """Konwertuje string 'a,b,c' na listę ['a','b','c']"""
    return [x.strip() for x in arg_str.split(',')] if arg_str else []


def parse_map(map_str):
    """
    Konwertuje string 'Arkusz1=klucz1,Arkusz2=klucz2' na słownik
    """
    mapping = {}
    for pair in map_str.split(','):
        sheet, key = pair.split('=')
        mapping[sheet.strip()] = key.strip()
    return mapping