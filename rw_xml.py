from bs4 import BeautifulSoup
import base64
###pip install lxml

def import_xml_settings(filename):
    '''
    Функция читает xml-файл и формирует словарь
    с списками для конект-строк.
    Результат возвращаем в виде dictionary. 
    Цель - импорт данных по всем подключениям к базам.
    Arguments:
        filename [str]: адрес файла с данными подключений
    Returns:
        [Dictionary]: результирующий словарь
    '''
    settings_set = {}

    fd = open(filename, 'r') 
    xml_file = fd.read() 
    soup = BeautifulSoup(xml_file, features="xml") 

    for tag in soup.findAll("item"): 
        label = base64.b64decode(tag["label"]).decode('utf-8')
        server = base64.b64decode(tag["server"]).decode('utf-8')
        bd = base64.b64decode(tag["database"]).decode('utf-8')
        login = base64.b64decode(tag["login"]).decode('utf-8')
        password = base64.b64decode(tag["password"]).decode('utf-8')
        settings_set[label] = [server, bd, login, password]
    
    fd.close()
    return settings_set

