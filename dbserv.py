import re

import pymssql
from aiogram.types.user import User

import keys
from botserv import list_pages

# engine = create_engine(f'mssql+pymssql://{user}:{password}@{server}/{database}')
_replbr = re.compile(r'(?i)</?br>')


def _get_items(table: str = '', top: int = list_pages[0], sortby: str = 'NDate'):
    assert len(table) > 0
    with pymssql.connect(host=keys.server, user=keys.user,
                         password=keys.password, database=keys.database) as conn:
        cursor = conn.cursor()
        strSQL = f'''SELECT top {top} * 
FROM [dbo].[{table}] 
WHERE ([dbo].[{table}].[IsVisible] <> 0) order by [{sortby}] DESC'''
        cursor.execute(strSQL)
        return [n for n in cursor]


def get_news(top: int = list_pages[0]) -> list:
    rl = _get_items(table='News', top=top)
    return [{'dt': i[1], 'txt': _replbr.sub('\n', i[2])} for i in rl]


def get_notes(top: int = list_pages[0]) -> list:
    rl = _get_items(table='AnalitNotes', top=top, sortby='A_Date')
    return [{'dt': n[1], 'txt': n[2], 'cat': n[4], 'file': n[5]} for n in rl]


def get_pres(top: int = list_pages[0]) -> list:
    rl = _get_items(table='ANALIT', top=top, sortby='ADate')
    return [{'dt': n[1], 'txt': _replbr.sub('\n', n[2]), 'descr': _replbr.sub('\n', n[3]),
             'cat': n[-1], 'auth': n[5], 'file': n[6]} for n in rl]


def update_user(user: User) -> int:
    """
    обновление данных пользователя: если пользователя нет - запись в БД его id, полного имени, ссылки
    если есть - инкремент счетчика посещений
    :param user: aiogram.types.user.User - структура пользователя из телеграмм
    :return:
    """
    assert user

    with pymssql.connect(host=keys.server, user=keys.user,
                         password=keys.password, database=keys.database) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM [dbo].[teleuser] where [id]='{user.id}'")
        row = cursor.fetchone()

        if row:
            cnt = row[-1] + 1
            _updateSQL = f'UPDATE dbo.teleuser SET dbo.teleuser.cnt = {cnt}'
            cursor.execute(_updateSQL)
        else:
            cnt = 0
            _insertSQL = f'''INSERT INTO [dbo].[teleuser] ([id], [full_name], [url], [mention], [lang], [cnt])
VALUES
('{user.id}', '{user.full_name}', '{user.url}', '{user.mention}', '{user.language_code}', {cnt})'''
            cursor.execute(_insertSQL)
        conn.commit()
        return cnt


def get_mon_infl(top=list_pages[0]):
    with pymssql.connect(host=keys.server, user=keys.user,
                         password=keys.password, database=keys.database) as conn:
        cursor = conn.cursor()
        strSQL = f'''SELECT top {top} * 
    FROM [dbo].[News] 
    WHERE ([dbo].[News].[IsVisible] <> 0) and ([dbo].[News].[NText] like '%О динамике инфляции%') order by [NDate] DESC'''
        cursor.execute(strSQL)
        lret = list()
        for i in cursor:
            _text = _replbr.sub('\n', i[2])
            _text = re.search(r'(?i)(?P<head><a.*a>)', _text).group('head')
            lret.append({'dt': i[1], 'txt': _text})
        return lret


def get_mon_tends(top=list_pages[0]):
    with pymssql.connect(host=keys.server, user=keys.user,
                         password=keys.password, database=keys.database) as conn:
        cursor = conn.cursor()
        strSQL = f'''SELECT top {top} * 
    FROM [dbo].[News] 
    WHERE ([dbo].[News].[IsVisible] <> 0) and ([dbo].[News].[NText] like '%Анализ макроэкономических тенденций%') order by [NDate] DESC'''
        cursor.execute(strSQL)
        lret = list()
        for i in cursor:
            _text = _replbr.sub('\n', i[2])
            _text = re.search(r'(?i)(?P<head><a.*a>)', _text).group('head')
            lret.append({'dt': i[1], 'txt': _text})
        return lret


def get_mon_fi(top=list_pages[0]):
    lret = _get_items(table='FI_Mons', top=top, sortby='M_Num')
    return [{'num': i[1], 'txt': i[3], 'file': i[4]} for i in lret]


def get_mon_trends(top=list_pages[0]):
    lret = _get_items(table='BP_Mons', top=top, sortby='M_Num')
    return [{'num': i[1], 'txt': i[3], 'file': i[4]} for i in lret]


def get_mon_santech(top=list_pages[0]):
    lret = _get_items(table='ST_Mons', top=top, sortby='M_Num')
    return [{'num': i[1], 'txt': i[3], 'file': i[4]} for i in lret]


def get_mon_growtech(top=list_pages[0]):
    lret = _get_items(table='HT_Mons', top=top, sortby='M_Num')
    return [{'num': i[1], 'txt': i[3], 'file': i[4]} for i in lret]


def get_mon_socproc(top=list_pages[0]):
    lret = _get_items(table='SC_Mons', top=top, sortby='M_Num')
    return [{'num': i[1], 'txt': i[3], 'file': i[4]} for i in lret]


def get_mon_e13(top=list_pages[0]):
    lret = _get_items(table='E13_Mons', top=top, sortby='M_Num')
    return [{'num': i[1], 'dt': i[3], 'txt': i[2], 'file': i[4]} for i in lret]


# def rrddss():
#     r = redis.Redis(host=os.environ['REDIS_HOST'], db=0)
#     r.mset({'testk1':'blablabla', 'testk2':'blublublu'})
#     print(r.get('testk1'))
#     print(r.get('testk1'))

if __name__ == '__main__':
    # update_user(None)
    # x = get_news(top=10)
    # x = get_mon_infl(top=20)
    # x = get_mon_fi(top=15)
    # x = get_mon_trends(top=15)
    # x = get_mon_santech(top=15)
    # x = get_mon_growtech(top=15)
    # x = get_mon_e13(top=5)
    x = get_mon_tends(top=list_pages[0])
    for i in x:
        print(i)

    # rrddss()
    # print(get_notes())
    # print(get_pres())
    # print(_get_items(table='News'))
    print('all done')
