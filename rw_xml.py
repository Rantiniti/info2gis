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

# функция добавления тэга для коннекта в xml-файл

def export_xml_setting(filename, s_set, name):
    '''
    Функция записывает в xml-файл данные конект-строки.
    Цель - экспорт данных, введенных вручную,
    по подключению к базе.
    Arguments:
        filename [str]: адрес файла с данными подключений
        s_set [dict]: данные для коннекта с БД
        name [str]: название набора данных для коннекта
    Returns:
        None
    '''
    s_set = dict(s_set)
    
    label = base64.b64encode(bytes(name, 'utf-8')).decode()
    server = base64.b64encode(bytes(s_set[name][0], 'utf-8')).decode()    
    bd = base64.b64encode(bytes(s_set[name][1], 'utf-8')).decode()
    login = base64.b64encode(bytes(s_set[name][2], 'utf-8')).decode()
    password = base64.b64encode(bytes(s_set[name][3], 'utf-8')).decode()
    is_remembered = base64.b64encode(bytes('true', 'utf-8')).decode()
    
    rest_string_tag = 'use_program="" pin_program="" link_program="" program="" path="" dir="" info=""'
    set_string = f'item label="{label}" server="{server}" database="{bd}" login="{login}" password="{password}" remember="{is_remembered}" {rest_string_tag}'
    
    fd = open(filename, 'r') 
    xml_file = fd.read() 
    soup = BeautifulSoup(xml_file, features="xml") 
    
    for item in soup.select('items'):
        finaltag=item.select('item')[-1]
        new_tag = soup.new_tag(set_string)
        finaltag.insert_after(new_tag)
    
    with open(filename, 'w') as f:
        f.write(soup.prettify())

# функция создания xml-файла для коннектовых настроек

def creating_xml_setting(filename, s_set, name):
    '''
    Функция создает xml-файл для данных конект-строк.
    Цель - создание файла с данными, введенными вручную,
    по подключению к базе.
    Arguments:
        filename [str]: адрес файла с данными подключений
        s_set [dict]: данные для коннекта с БД
        name [str]: название набора данных для коннекта
    Returns:
        None
    '''
    soup = BeautifulSoup(features='xml')
    soup.append(soup.new_tag("settings"))
    soup.settings.append(soup.new_tag("items"))
    soup.settings.items.append(soup.new_tag('item'))
    item_tag = soup.settings.items.select('item')[-1]
    item_tag['label'] = base64.b64encode(bytes(name, 'utf-8')).decode()
    item_tag['server'] = base64.b64encode(bytes(s_set[name][0], 'utf-8')).decode() 
    item_tag['bd'] = base64.b64encode(bytes(s_set[name][1], 'utf-8')).decode()
    item_tag['login'] = base64.b64encode(bytes(s_set[name][2], 'utf-8')).decode()
    item_tag['password'] = base64.b64encode(bytes(s_set[name][3], 'utf-8')).decode()
    item_tag['is_remembered'] = base64.b64encode(bytes('true', 'utf-8')).decode()
    item_tag['use_program'] = ""
    item_tag['pin_program'] = ""
    item_tag['link_program'] = ""
    item_tag['program'] = ""
    item_tag['path'] = ""
    item_tag['dir'] = ""
    item_tag['info'] = ""
    
    
    with open(filename, 'w') as f:
        f.write(soup.prettify())
        #print(f)
    
# функция проверки на нахождения настроек в xml-файле
    
def is_empty_settings(filename):
    '''
    Функция проверяет есть ли данные хотябы для одной коннект-строки.
    Arguments:
        filename [str]: адрес файла с данными подключений
    Returns:
        bool: true если настройки отсутствуют
    '''
    fd = open(filename, 'r') 
    xml_file = fd.read() 
    soup = BeautifulSoup(xml_file, features="xml") 
    
    if(not soup.select('item')):
        return True
    else:
        return False
    
    
# функция заполнения данными словаря создаваемого файла xml
def stuff_settings_xml(filename, s_set):
    '''
    Функция создает xml-файл для данных конект-строк.
    Цель - создание файла и заполнение данными настроек 
        из словаря
    Arguments:
        filename [str]: адрес файла с данными подключений
        s_set [dict]: данные для коннекта с БД
    Returns:
        None
    '''
    soup = BeautifulSoup(features='xml')
    soup.append(soup.new_tag("settings"))
    soup.settings.append(soup.new_tag("items"))
    for item in s_set.keys():
        soup.settings.items.append(soup.new_tag('item'))
        item_tag = soup.settings.items.select('item')[-1]
        item_tag['label'] = base64.b64encode(bytes(item, 'utf-8')).decode()
        item_tag['server'] = base64.b64encode(bytes(s_set[item][0], 'utf-8')).decode() 
        item_tag['bd'] = base64.b64encode(bytes(s_set[item][1], 'utf-8')).decode()
        item_tag['login'] = base64.b64encode(bytes(s_set[item][2], 'utf-8')).decode()
        item_tag['password'] = base64.b64encode(bytes(s_set[item][3], 'utf-8')).decode()
        item_tag['is_remembered'] = base64.b64encode(bytes('true', 'utf-8')).decode()
        item_tag['use_program'] = ""
        item_tag['pin_program'] = ""
        item_tag['link_program'] = ""
        item_tag['program'] = ""
        item_tag['path'] = ""
        item_tag['dir'] = ""
        item_tag['info'] = ""
    
    with open(filename, 'w') as f:
        f.write(soup.prettify())
        
    