from tkinter.ttk import Combobox
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
import inspect
from os import path

from rw_xml import import_xml_settings

#-----finding the path of the current script-file------------
script_name = inspect.getframeinfo(inspect.currentframe()).filename
path_script = path.dirname(path.abspath(script_name))
setting_filename = f"{path_script}\settings.xml"
file_parameters = ""
settings_set = {}
#--------------------------funcs-------------------------------
def get_settings_set(filename):
    global settings_set
    settings_set = import_xml_settings(filename)
    
def get_current_bd_set(jur_label):
    global settings_set, current_bd_set
    current_bd_set = settings_set.get(jur_label, []).copy()
    return current_bd_set

def no_params():
    #print(current_bd_set)
    if not current_bd_set:
        return True
    else: 
        return False
    
#--------------------------funcs4events------------------------
def import_params():
    global setting_filename
    
    # После нажатия кнопки Импортировать       
    file = filedialog.askopenfilename(filetypes = (('xml files', '*.xml'),('All files', '*.*')))
    global file_parameters
    file_parameters = file
    # get global settings_set
    get_settings_set(file_parameters)
    combo.config(values=list(settings_set.keys())[::-1])
    combo_close_ls.config(values=list(settings_set.keys())[::-1])
    combo_main.config(values=list(settings_set.keys())[::-1])
    shutil.copyfile(file, setting_filename)


def save_set():
    pass


def select_jur(event):
    
    if combo_MC.get():
        get_current_bd_set(combo_MC.get())
        if not no_params():
            btn_open.config(state="normal")
            lbl_info.config(text= f"{current_bd_set}\
                \n Загрузите файл шаблона с номерами ЕЛС")
            btn_load_close_ls.config(state="normal")
            lbl_info_close_ls.config(text= f"{current_bd_set}\
                \n Загрузите файл шаблона для экспорта закрытых ЛС")
            btn_kadastr_open.config(state="normal")
            lbl_info_kadastr.config(text = f"{current_bd_set}\
                \n Загрузите файл шаблона с объектами ЖФ")
            btn_kvitirovanie_open.config(state="normal")
            lbl_info_kvitirovanie.config(text = f"{current_bd_set}\
                \n Загрузите файл шаблона Извещения о принятии к исполнению распоряжений")
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

lbl_lable = Label(tab_settings, text="Наименование:")
lbl_lable.grid(row=3, column=0, padx=5, pady=5)
txt_lable = Entry(tab_settings, width=22)
txt_lable.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

lbl_srv = Label(tab_settings, text="Сервер:")
lbl_srv.grid(row=4, column=0, padx=5, pady=5)
txt_srv = Entry(tab_settings, width=22)
txt_srv.grid(row=4, column=1, columnspan=2, padx=5, pady=5)

lbl_bd = Label(tab_settings, text="База:")
lbl_bd.grid(row=5, column=0, padx=5, pady=5)
txt_bd = Entry(tab_settings, width=22)
txt_bd.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

lbl_usr = Label(tab_settings, text="Пользователь:")
lbl_usr.grid(row=6, column=0, padx=5, pady=5)
txt_usr = Entry(tab_settings, width=22)
txt_usr.grid(row=6, column=1, columnspan=2, padx=5, pady=5)

lbl_pass = Label(tab_settings, text="Пароль:")
lbl_pass.grid(row=7, column=0, padx=5, pady=5)
txt_pass = Entry(tab_settings, width=22)
txt_pass.grid(row=7, column=1, columnspan=2, padx=5, pady=5)

btn_saving = Button(tab_settings, text="Сохранить", command=save_set)
btn_saving.grid(row=8, column=1)
btn_saving.config(state="disabled")

lbl_setting_info = Label(tab_settings, text = "отсутствует статус настроек", font=("Arial Bold", 10), fg="red")
lbl_setting_info.grid(row=9, column=0, columnspan=3)

combo_MC = Combobox(tab_settings, state="readonly")
combo_MC.grid(row=10, column=0, columnspan=3)  
combo_MC.bind("<<ComboboxSelected>>", select_jur)

#--------------------------------------------------------------

window.mainloop()
