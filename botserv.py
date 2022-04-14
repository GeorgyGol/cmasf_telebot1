from aiogram.utils.markdown import text, bold, hbold, html_decoration


list_pages = [3, 5, 10]

import dbserv

def show_news(top=list_pages[0]):
    _mess = list()
    lnews = dbserv.get_news(top=top)
    header = 'Новости,'
    for n in lnews:
        _mess.append(text(hbold(n["dt"].strftime(format="%d.%m.%Y")), n["txt"], sep=': '))
    return header, _mess

def show_notes(top=list_pages[0]):
    _mess = list()
    header = 'Аналитические записки,'
    lnots = dbserv.get_notes(top=top)
    for n in lnots:
        _hd = f'<b>{n["dt"].strftime(format="%d.%m.%Y")}</b>: <i>({n["cat"]})</i>'
        _lnk = html_decoration.link(value=n['txt'], link=n['file'])
        _mess.append(text(_hd, _lnk, sep='\n'))
    return header, _mess

def show_reps(top=list_pages[0]):
    _mess = list()
    header = 'Презентации и статьи,'
    lpres = dbserv.get_pres(top=top)
    for p in lpres:
        _hd = f'<b>{p["dt"].strftime(format="%d.%m.%Y")}</b>: ({p["cat"]})'
        _lnk = html_decoration.link(value=p['txt'], link=p['file'])
        _dscr = html_decoration.spoiler(value=p['descr'])
        _auth = html_decoration.italic(value=p['auth'])
        _mess.append(text(_hd, _auth, _lnk, _dscr, sep='\n'))
    return header, _mess

# отсюда - mons
def show_infl(top=list_pages[0]):
    _mess = list()
    header = 'Мониторинги инфляции,'
    for n in dbserv.get_mon_infl(top=top):
        _hd = f'<b>{n["dt"].strftime(format="%d.%m.%Y")}:</b> '
        # _ms = text(n['text'])
        _mess.append(text(_hd, n['txt'], sep=''))
    return header, _mess

def show_tends(top=list_pages[0]):
    _mess = list()
    header = 'Анализ макроэкономических тенденций,'
    for n in dbserv.get_mon_tends(top=top):
        _hd = f'<b>{n["dt"].strftime(format="%d.%m.%Y")}:</b> '
        # _ms = text(n['text'])
        _mess.append(text(_hd, n['txt'], sep=''))
    return header, _mess

def show_fin(top=list_pages[0]):
    _mess = list()
    header = 'Финансовые индикаторы,'
    for n in dbserv.get_mon_fi(top=top):
        _num = hbold(f'№ {n["num"]}: ')
        _lnk = html_decoration.link(value=n['txt'], link=n['file'])
        _mess.append(text(_num, _lnk, sep='\n'))
    return header, _mess

def show_trends(top=list_pages[0]):
    _mess = list()
    header = 'Тренды российской экономики,'
    for n in dbserv.get_mon_trends(top=top):
        _num = hbold(f'№ {n["num"]}: ')
        _lnk = html_decoration.link(value=n['txt'], link=n['file'])
        _mess.append(text(_num, _lnk, sep='\n'))
    return header, _mess

def show_santech(top=list_pages[0]):
    _mess = list()
    header = 'Технологические санкции и их последствия,'
    for n in dbserv.get_mon_santech(top=top):
        _lnk = html_decoration.link(value=n['txt'], link=n['file'])
        _mess.append(text(_lnk, sep='\n'))
    return header, _mess

def show_growtech(top=list_pages[0]):
    _mess = list()
    header = 'Технологическое развитие России и мира,'
    for n in dbserv.get_mon_growtech(top=top):
        _lnk = html_decoration.link(value=n['txt'], link=n['file'])
        _mess.append(text(_lnk, sep='\n'))
    return header, _mess

def show_socmon(top=list_pages[0]):
    _mess = list()
    header = 'Социальные процессы,'
    for n in dbserv.get_mon_socproc(top=top):
        _num = hbold(f'№ {n["num"]}: ')
        _lnk = html_decoration.link(value=n['txt'], link=n['file'])
        _mess.append(text(_num, _lnk, sep='\n'))
    return header, _mess

def show_tez(top=list_pages[0]):
    _mess = list()
    header = 'Тринадцать тезисов,'
    for n in dbserv.get_mon_e13(top=top):
        _num = hbold(f'№ {n["dt"]}: ')
        _lnk = html_decoration.link(value=n['txt'], link=n['file'])
        _mess.append(text(_num, _lnk, sep='\n'))
    return header, _mess

dict_mons = {'infl':show_infl, 'tends':show_tends, 'fin':show_fin,
             'trends':show_trends, 'santech':show_santech, 'growtech':show_growtech,
             'socmon':show_socmon, 'tez':show_tez}

dict_mons_head = {'infl': 'Инфляция',
                  'trends':'Тренды',
                  'santech':'Тех санкции',
                  'growtech': 'Тех развитие',
                  'fin':'Фин индикаторы',
                  'tends':'Анализ тенденций',
                  'socmon':'Соц процессы',
                  'tez':'13 тезисов'}

dict_main = {'news':show_news, 'notes':show_notes, 'reps':show_reps}
dict_main_head = {'news':'Новости',
                  'reps':'Презентации',
                  'notes':'Аналитика',
                  'mons':'Мониторинги'}