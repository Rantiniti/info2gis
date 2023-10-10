import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy as sa
from sqlalchemy.sql import text, select, and_, or_, asc, desc, between
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql.expression import update
import numpy as np

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
    return f"with jud as ( "\
                f"select  "\
                f"e.id_efls [efls],  "\
                f"max(ej.date_end) [date_judge]  "\
                f"from EFls_judge ej  "\
                f"join Efls e on e.id_efls = ej.id_efls  "\
                f"where getdate() between e.date_beg and e.date_end  "\
                f"and ej.is_full_payed is null  "\
                f"and ej.date_verdict is not null  "\
                f"and (ej.id_type_efls_judge_mark <> 1 or ej.id_type_efls_judge_mark is null)  "\
                f"group by e.id_efls) "\
            f"select  "\
            f"e.number,   "\
            f"a.name [appart],  "\
            f"dbo.fn_people_full_name(pg.id_people) [fio],  "\
            f"(select fname from People where id_people = pg.id_people) [lastdName],  "\
            f"isnull ((select mname from People where id_people = pg.id_people), '-') [firstName],  "\
            f"isnull ((select lname from People where id_people = pg.id_people), '-') [secondName],  "\
            f"aa.value [fias],  "\
            f"dbo.fn_addr_full_name(h.id_addr) [address]  "\
            f"from Efls e "\
            f"join Addr a on a.id_addr = e.id_addr_appart  "\
            f"join Addr h on h.id_addr = a.id_addr_up  "\
            f"join Addr_attr aa on aa.id_addr = h.id_addr  "\
            f"join Addr_appart_type at on at.id_addr_appart = a.id_addr  "\
            f"join Type_addr_appart ta on ta.id_type_addr_appart = at.id_type_addr_appart   "\
            f"join vi_People_gen pg on pg.id_efls = e.id_efls  "\
            f"join jud j on j.efls = e.id_efls  "\
            f"where aa.id_attr = 1001  "\
            f"and getdate() between pg.date_beg and pg.date_end  "\
            f"and getdate() between e.date_beg and e.date_end  "\
            f"and at.id_type_addr_appart <> 4  "\
            f"order by dbo.fn_addr_element(dbo.fn_addr_full_name(a.id_addr)) "


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
        None
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
    df = column2str(df)
    
    # объединяем датафреймы из словаря в один с опорными признаками
    gis_df = pd.merge(data[0], data[1], how='inner', on=['№ запроса'])[[
        'Идентификатор адреса', 'Номер квартиры, комнаты, блока жилого дома',
        'Идентификатор запроса в ГИС ЖКХ']]
    
    # убираем префикс "кв. "
    gis_df['Номер квартиры, комнаты, блока жилого дома'] = gis_df['Номер квартиры, комнаты, блока жилого дома'].apply(
        lambda x: x[4:])
    
    # объединяем данные ГИС ЖКХ и АИС ЖКХ
    result_df = pd.merge(gis_df, df, how='left', 
                         left_on = ['Идентификатор адреса', 'Номер квартиры, комнаты, блока жилого дома'],
                         right_on=['fias', 'appart'])
    
    pass