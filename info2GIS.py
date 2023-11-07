from tkinter.ttk import Combobox
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
import inspect
from os import path
import pandas as pd
import shutil

from rw_xml import import_xml_settings, export_xml_setting
from data4gis import binding_debts

#-----finding the path of the current script-file------------
script_name = inspect.getframeinfo(inspect.currentframe()).filename
path_script = path.dirname(path.abspath(script_name))
setting_filename = f"{path_script}\settings.xml"
file_parameters = ""
settings_set = {}
gis_data = {}
current_bd_set = []
#--------------------------funcs-------------------------------
def get_settings_set(filename):
    '''
    Функция запускает функцию импорта словаря с данными для строк подключений, 
    по переданному адресу файла
    Результат возвращаем в виде dictionary. 
    Arguments:
        filename [str]: адрес файла с данными подключений
    Returns:
        [Dictionary]: результирующий словарь
    '''
    global settings_set
    settings_set = import_xml_settings(filename)
    
def get_current_bd_set(jur_label):
    '''
    Функция выбирает данные для строки подключения, 
    по переданному идентификатору юридического лица
    Результат возвращаем в виде dictionary. 
    Arguments:
        jur_label [str]: идентификатор юр. лица (УК)
    Returns:
        [list]: результирующий список
    '''
    global settings_set, current_bd_set
    current_bd_set = settings_set.get(jur_label, []).copy()
    return current_bd_set

def no_params():
    '''
    Функция производит проверку на наличие уже выбранных
    данных юр.лица для подключения к БД. 
    Arguments:
    Returns:
        [Boolean]: True/Существуют данные (False/Отсутствуют данные)
    '''
    #print(current_bd_set)
    if not current_bd_set:
        return True
    else: 
        return False

def read_gis_file(file):
    '''
    Функция читает данные из файла
    в датафрейм и присвивает его глобальной
    переменной gis_data
    Arguments:
        file [str]: имя excel-файла
    Returns:
        None
    '''
    global gis_data
    gis_data = pd.read_excel(file, sheet_name=[0, 1])
    lbl_info_debts.config(text="Данные шаблона получены")
    btn_debts_start.config(state="normal")
    

def insert_data(df, file_name, sheetname="Ответы на запросы"):
    ##---sheetname = "Ответы на запросы" по умолчанию
    ##-- Сhecking for the presence of a file
    res_dir = path.normpath(path.expanduser("~/Desktop")) 
    res_file_name = f"\{current_bd_set[1]}__result"
    res_ext = ".xlsx"
    file_name2 = res_dir + res_file_name + res_ext
    number = 1
    while path.exists(file_name2):
        number += 1
        file_name2 = f"{res_dir}{res_file_name}_{number}{res_ext}"
    shutil.copyfile(file_name, file_name2)
    # вариант записи данных в excel-файл
    '''wb = ox.load_workbook(new_file_name)
    for ir in range(0, len(df)):
        for ic in range(0, len(df.iloc[ir])):
            wb[sheetname].cell(2 + ir, 1 + ic).value = df.iloc[ir][ic]
    wb.save(new_file_name)'''
    with pd.ExcelWriter(path = file_name2, mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
        df.to_excel(writer, sheet_name="Ответы на запросы", startrow=2, index= False, header= False )

#--------------------------------------------------------------        
#--------------------------funcs4events------------------------
def import_params():
    '''
    Функция-обработчик для импорта данных настроек коннектов к БД. 
    Получает имя  файла и передает его в функцию,
    на выходе которой будет словарь с данными для коннектов
    Настраивает интерфейс для последующих действий по выбору
    юрлица с котором будет вестись работа.
    Returns:
        None
    '''
    global setting_filename
    
    # После нажатия кнопки Импортировать       
    file = filedialog.askopenfilename(filetypes = (('xml files', '*.xml'),('All files', '*.*')))
    global file_parameters
    file_parameters = file
    # get global settings_set
    get_settings_set(file_parameters)
    combo_MC.config(values=list(settings_set.keys())[::-1])
    lbl_setting_info.config(text="Выберите организацию", fg="blue")

def add_param():
    '''
    Функция-обработчик открывает поля
    для ввода данных по коннекту пользователю 
    Arguments []:
    Returns:
    '''
    txt_lable.config(state=NORMAL)
    txt_srv.config(state=NORMAL)
    txt_bd.config(state=NORMAL)
    txt_usr.config(state=NORMAL)
    txt_pass.config(state=NORMAL)
    
    btn_saving.config(state="normal")
    pass


def save_set():
    '''
    Функция-обработчик сохраняет введенные данные
    пользователем 
    через добавление в файл предварительных настроек. 
    Arguments []:
    Returns:
    '''
    global settings_set
    global setting_filename
    
    list_connect_params = [txt_lable.get(), txt_srv.get(),
                           txt_bd.get(), txt_usr.get(), txt_pass.get()]
    
    
    if "" in list_connect_params:
        return 
    
    settings_set[list_connect_params[0]] = [list_connect_params[1], list_connect_params[2], 
                                       list_connect_params[3], list_connect_params[4]]
    
    # сохраняем добавленный набор для коннекта в xml-файл
    export_xml_setting(setting_filename, settings_set, list_connect_params[0])


def select_jur(event):
    '''
    Функция-обработчик получает название юр.лица
    и передает функцию для поиска и получения текущих рабочих
    настроек для текущего коннекта.
    Настраивает интерфейс для последующих действий пользователя.
    Returns:
        None
    '''
    if combo_MC.get():
        get_current_bd_set(combo_MC.get())
        if not no_params():
            btn_debts_open.config(state="normal")
            lbl_info_debts.config(text = f"{current_bd_set}\
                \n Загрузите файл шаблона Извещения о принятии к исполнению распоряжений")
            
def get_gis_data():
    '''
    Функция-обработчик запускает функцию
    получения рабочего датасета из excel-файла,
    указанного в окне-диалоге. 
    Arguments:
    Returns:
        None
    '''
    # Чтение шаблона с ЕЛС после нажатия Открыть
    file = filedialog.askopenfilename(filetypes = (("xlsx files","*.xlsx"),("all files","*.*")))
    global filename
    filename = file
    read_gis_file(file)  
    
    
def start_debts_procedure():
    '''
    Функция-обработчик запускает функцию binding_debts
    получения результирующего датафрейма с данными по должникам.
    Запись результата в excel-файл. 
    Arguments:
    Returns:
        None
    '''
    #pass
    df_result = binding_debts(gis_data, current_bd_set[0], current_bd_set[1], current_bd_set[2], current_bd_set[3])
    #res_dir = path.dirname(filename) 
    # разбиение имени файла для провеки на уже существующий файл
    # с таким же именем
    #res_file_name = f"\{current_bd_set[1]}_result"
    #res_ext = ".xlsx"
    #res_file = res_dir + res_file_name + res_ext
    #number = 1
    #while path.exists(res_file):
    #    number += 1
    #    res_file = f"{res_dir}{res_file_name}_{number}{res_ext}"
        
    #df_result.to_excel(res_file, sheet_name='Квитирование - Результат')
    insert_data(df_result, filename)
    lbl_info_debts.config(text="Обработка данных закончена! \n Результат: ")    
#-----------------------------------------------------------




#-------------------------------------------------------------
window = Tk()
window.title("Импорт информации в ГИС ЖКХ")
window.geometry('420x400')

for c in range(3): window.columnconfigure(index=c, weight=1)
for r in range(10): window.rowconfigure(index=r, weight=1)
#--------------------------------------------------------------
# tab_settings "Настройки" - 0
# tab_debts  "Импорт данных о должниках" - 1
# 
#--------------------------------------------------------------
tab_control = ttk.Notebook(window) 
enabled = IntVar()

tab_settings = ttk.Frame(tab_control)  
tab_control.add(tab_settings, text='Настройки')  
tab_control.pack(expand=1, fill='both') 

tab_debts = ttk.Frame(tab_control)  
tab_control.add(tab_debts, text='Импорт данных о должниках')  
tab_control.pack(expand=1, fill='both') 

#-------------------------- tab 1 -----------------------------
#--------------------------------------------------------------
lbl_import_params = Label(tab_settings, text = "Импорт настроек \n соединения с БД (xml-файл)", font = ("Arial Bold", 10))
lbl_import_params.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

btn_import_params = Button(tab_settings, text = "Загрузить", command=import_params)
btn_import_params.grid(row = 0, column = 2)

lbl_add = Label(tab_settings, text="Добавление данных для подключения к БД")
lbl_add.grid(row = 1, column=0, rowspan=2, columnspan=3, sticky=NSEW)
btn_add_setting = Button(tab_settings, text="Добавить", command=add_param)
btn_add_setting.grid(row=1, column=2)


lbl_lable = Label(tab_settings, text="Наименование:")
lbl_lable.grid(row=3, column=0, padx=5, pady=5)
txt_lable = Entry(tab_settings, width=22)
txt_lable.config(state=DISABLED)
txt_lable.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

lbl_srv = Label(tab_settings, text="Сервер:")
lbl_srv.grid(row=4, column=0, padx=5, pady=5)
txt_srv = Entry(tab_settings, width=22)
txt_srv.config(state=DISABLED)
txt_srv.grid(row=4, column=1, columnspan=2, padx=5, pady=5)

lbl_bd = Label(tab_settings, text="База:")
lbl_bd.grid(row=5, column=0, padx=5, pady=5)
txt_bd = Entry(tab_settings, width=22)
txt_bd.config(state=DISABLED)
txt_bd.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

lbl_usr = Label(tab_settings, text="Пользователь:")
lbl_usr.grid(row=6, column=0, padx=5, pady=5)
txt_usr = Entry(tab_settings, width=22)
txt_usr.config(state=DISABLED)
txt_usr.grid(row=6, column=1, columnspan=2, padx=5, pady=5)

lbl_pass = Label(tab_settings, text="Пароль:")
lbl_pass.grid(row=7, column=0, padx=5, pady=5)
txt_pass = Entry(tab_settings, width=22)
txt_pass.config(state=DISABLED)
txt_pass.grid(row=7, column=1, columnspan=2, padx=5, pady=5)
btn_saving = Button(tab_settings, text="Сохранить", command=save_set)
btn_saving.grid(row=8, column=1)
btn_saving.config(state="disabled")


lbl_setting_info = Label(tab_settings, text = "отсутствует статус настроек", font=("Arial Bold", 10), fg="red")
lbl_setting_info.grid(row=9, column=0, columnspan=3)

combo_MC = Combobox(tab_settings, state="readonly")
combo_MC.grid(row=10, column=0, columnspan=3)  
combo_MC.bind("<<ComboboxSelected>>", select_jur)

#list4addBD = [txt_lable, txt_srv, txt_bd, txt_usr, txt_pass]



#-------------------------- tab 2 (debts)----------------------
#--------------------------------------------------------------
lbl_debts_form = Label(tab_debts, text="Загрузите Извещения о принятии к исполнению распоряжений", 
                       font=("Arial Bold", 10))
lbl_debts_form.grid(row=0, column=0, columnspan=2)

btn_debts_open = Button(tab_debts, text="Открыть", bg="white", fg="black", command=get_gis_data)
btn_debts_open.grid(row=1, column=0, columnspan=3)
if not no_params():
    btn_debts_open.config(state="normal")
else:
    btn_debts_open.config(state="disabled")

lbl_info_debts = Label(tab_debts, font=("Arial Bold", 10), fg="green")
lbl_info_debts.grid(row=3, column=0, columnspan=3)

btn_debts_start = Button(tab_debts, text="Запуск", bg="white", fg="black", command=start_debts_procedure)
btn_debts_start.grid(row=5, column=0, columnspan=3)
if not no_params() and gis_data:
    btn_debts_start.config(state="normal")
else:
    btn_debts_start.config(state="disabled")
    

if no_params():
    lbl_info_debts.config(text="Настройте соединение с БД организации \n затем выберите нужную организацию")
#--------------------------------------------------------------
# если есть файл с настройками в рабочем каталоге, чиаем и привязываем данные
if path.exists(setting_filename):
        get_settings_set(setting_filename)
        combo_MC.config(values=list(settings_set.keys())[::-1])
        lbl_setting_info.config(text="Выберите организацию!", fg="blue")


window.mainloop()
