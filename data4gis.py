import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy as sa
from sqlalchemy.sql import text, select, and_, or_, asc, desc, between
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql.expression import update
import numpy as np
import inspect
from os import path

###-----------------------------------------------------------------------

def get_sql_query(qtext, engine_connect):
    '''
    Функция считывает результат запроса из БД
    и возварщает его в виде dataframe  
    Arguments:
        qtext str: текст запроса sql
        conn: текущий connect 
    Returns:
        dataframe: результирующий датасет
    '''
    with engine_connect.connect().execution_options(autocommit=True) as conn:
        return(pd.read_sql_query(text(qtext), con=conn))
        # get dataframe from sql select


def query_ais_debts():
    '''
    Функция возвращает sql-запрос для получения
    данных по должникам из АИС для последующей 
    работы с данными в функции binding_debts
    Arguments:
    Returns:
        str: sql запрос данных по должникам в БД "АИС ЖКХ"
    '''
    #-----finding the path of the current script-file------------
    script_name = inspect.getframeinfo(inspect.currentframe()).filename
    path_script = path.dirname(path.abspath(script_name))
    query_file= f"{path_script}\query_debts.txt"
    
    with open(query_file) as q:
        sql_text = q.read()
    
    return sql_text


def column2str(df):
    '''
    Функция преобразует тип данных
    признаков: номера лс и наименование помещений
    из float в str
    Arguments:
        df Dataframe: исходный датасет
    Returns:
        dataframe: результирующий датасет
    '''
    for col in df.columns:
        if ('appart' in col) or ('number' in col):
            df = df.astype({col: str})
    return df
#---------------------------------------------------------------------------------------------------------------

def binding_debts(data, server, database, username, password, driver='ODBC Driver 17 for SQL Server'):
    '''
    Функция получает на входе датафрейм с данными по запросам Минтруда,
    вытягиевает данные из АИС ЖКХ о текущих должниках и мержирует датасеты
    по фиас адресам и наименованиям помещений.
    Arguments:
        data dict: словарь датафреймов из запросов с ГИС ЖКХ
        server, database, username, password, driver: 
                        данные для строки подключения к БД АИС ЖКХ
    Returns:
        Dataframe: датафрейм подбитый для заливки шаблона 
        с послеюдущим экспортом данных по должникам в ГИС ЖКХ
    '''
    
    connection_uri = sa.engine.URL.create(
    "mssql+pyodbc",
    username=username,
    password=password,
    host=server,
    database=database,
    query={"driver": driver},
    )
    
    engine = create_engine(connection_uri)
    meta = MetaData()
    
    df = get_sql_query(query_ais_debts(), engine)
    
    # если должников в АИС ЖКХ нет,
    # то выдаем результирующий датасет с отсутствием долгов
    if df.empty:
        result_df = data[1][['№ запроса', 'Идентификатор запроса в ГИС ЖКХ']]
        result_df['подтверждено'] = 'нет'
        return result_df
    
    df = column2str(df)
    
    # объединяем датафреймы из словаря в один с опорными признаками
    gis_df = pd.merge(data[0], data[1], how='inner', on=['№ запроса'])[[
        'Идентификатор адреса', 'Номер квартиры, комнаты, блока жилого дома',
        '№ запроса', 'Идентификатор запроса в ГИС ЖКХ']]
    
    # убираем префикс "кв. "
    gis_df['Номер квартиры, комнаты, блока жилого дома'] = gis_df['Номер квартиры, комнаты, блока жилого дома'].apply(
        lambda x: x[4:])
    
    # объединяем данные ГИС ЖКХ и АИС ЖКХ
    result_df = pd.merge(gis_df, df, how='left', 
                         left_on = ['Идентификатор адреса', 'Номер квартиры, комнаты, блока жилого дома'],
                         right_on=['fias', 'appart'])
    
    # если среди запросов с соцзащиты нет должников в данных аис
    # возвращаем датасет с инфой об отсутствии долгов
    if result_df.empty:
        result_df['подтверждено'] = 'нет'
        return result_df[['№ запроса', 'Идентификатор запроса в ГИС ЖКХ', 'подтверждено']]
    
    # формируем датасет с учетом найденных должников
    result_df['подтверждено'] = result_df['number'].apply(lambda x: 'нет' if(pd.isna(x)) else 'да')
    result_df = result_df[['№ запроса', 'Идентификатор запроса в ГИС ЖКХ', 'подтверждено', 'lastdName', 'firstName', 'secondName']]
    
    return result_df
