import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardRemove)
from aiogram.types.message import ParseMode, ContentType
from aiogram.utils.markdown import text, hbold, html_decoration

import botserv
import dbserv

storage = RedisStorage2(os.environ['REDIS_HOST'], 6379, db=0)
logging.basicConfig(level=logging.ERROR)

bot = Bot(token=os.environ['BTOK'])
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


class OrderFood(StatesGroup):
    select_rubr = State()
    select_mon = State()


def iterate_group(iterator, count):
    for i in range(0, len(iterator), count):
        yield iterator[i:i + count]


def main_menu():
    ikbt = InlineKeyboardMarkup()
    ikbt.row(InlineKeyboardButton(botserv.dict_main_head['news'], callback_data='news'),
             InlineKeyboardButton(botserv.dict_main_head['reps'], callback_data='reps'),
             InlineKeyboardButton(botserv.dict_main_head['notes'], callback_data='notes'))

    ikbt.row(InlineKeyboardButton(botserv.dict_main_head['mons'], callback_data='mons'),
             InlineKeyboardButton('Сайт Центра', url='http://www.forecast.ru')
             )

    # ikbt.row()
    return ikbt

def mons_menu():
    ikbt = InlineKeyboardMarkup()
    ikbt.row(InlineKeyboardButton(botserv.dict_mons_head['infl'], callback_data='infl'),
             # InlineKeyboardButton(botserv.dict_mons_head['rail'], callback_data='rail'),
             InlineKeyboardButton(botserv.dict_mons_head['trends'], callback_data='trends'))

    ikbt.row(InlineKeyboardButton(botserv.dict_mons_head['santech'], callback_data='santech'),
             InlineKeyboardButton(botserv.dict_mons_head['growtech'], callback_data='growtech'),
             InlineKeyboardButton(botserv.dict_mons_head['fin'], callback_data='fin'))

    ikbt.row(InlineKeyboardButton(botserv.dict_mons_head['tends'], callback_data='tends'),
             InlineKeyboardButton(botserv.dict_mons_head['socmon'], callback_data='socmon'),
             InlineKeyboardButton(botserv.dict_mons_head['tez'], callback_data='tez'))
    return ikbt

def item_menu():
    ikbt = InlineKeyboardMarkup()
    ikbt.row(InlineKeyboardButton(f'{botserv.list_pages[0]} последних', callback_data=str(botserv.list_pages[0])),
             InlineKeyboardButton(f'{botserv.list_pages[1]} последних', callback_data=str(botserv.list_pages[1])),
             InlineKeyboardButton(f'{botserv.list_pages[2]} последних', callback_data=str(botserv.list_pages[2])))
    return ikbt


def rplmain_menu(show_main=False, show_back=False):
    rkbt = ReplyKeyboardMarkup(resize_keyboard=True)
    if show_main:
        # rkbt.row(KeyboardButton('back'), KeyboardButton('main'),
        #          KeyboardButton('help'), KeyboardButton('stop'))
        rkbt.row(KeyboardButton('back'), KeyboardButton('main'))
    else:
        if show_back:
            # rkbt.row(KeyboardButton('back'), KeyboardButton('help'), KeyboardButton('stop'))
            rkbt.row(KeyboardButton('back'))
        else:
            # rkbt.row(KeyboardButton('help'), KeyboardButton('stop'))
            return ReplyKeyboardRemove()
    return rkbt


async def show_context_menu(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    _top = user_data.get('top')

    cur_state = user_data.get('current_R')
    if cur_state == 'mons':
        cur_mon = user_data.get('select_mons')
        if cur_mon and (cur_mon != 'main'):
            await bot.send_message(chat_id=message.chat.id,
                                   text=text(f'Вы в подразделе Мониторинги - {botserv.dict_mons_head[cur_mon]}',
                                             f'Показаны {_top} последних. Показать:', sep='\n'),
                                   reply_markup=item_menu(), parse_mode=ParseMode.HTML)
        else:
            await bot.send_message(chat_id=message.chat.id, text='Вы в подразделе Мониторинги. выберете подраздел',
                                   reply_markup=mons_menu(), parse_mode=ParseMode.HTML)
    elif cur_state:
        await bot.send_message(chat_id=message.chat.id,
                               text=text(f'Вы в разделе {botserv.dict_main_head[cur_state]}',
                                         f'Показаны {_top} последних. Показать:', sep='\n'),
                               reply_markup=item_menu(), parse_mode=ParseMode.HTML)


@dp.message_handler(commands='start', state='*')
@dp.message_handler(Text(equals='start'), state='*')
async def start(message: types.Message, state: FSMContext):
    if message.chat.type == 'group':
        return
    await state.finish()
    user = message.from_user
    if dbserv.update_user(user) == 0:
        th = text(html_decoration.bold(f'Здравствуйте {message.from_user.full_name}!'),
                  'Вас приветствует телеграм бот <i>Центра макроэкономического анализа и краткосрочного прогнозирования</i>',
                  sep='\n')
    else:
        th = text(html_decoration.bold(f'С возвращением, {message.from_user.full_name}!'),
                  'ЦМАКП снова с вами!', sep='\n')
    await bot.send_message(chat_id=message.chat.id, text=th, parse_mode=ParseMode.HTML, reply_markup=rplmain_menu())

    _mess = text('Выберете раздел:', sep='\n')
    await bot.send_message(chat_id=message.chat.id,
                           text=_mess, reply_markup=main_menu(), parse_mode=ParseMode.HTML)

    await OrderFood.select_rubr.set()


@dp.message_handler(state='*', commands='help')
@dp.message_handler(Text(equals='help'), state='*')
async def show_help(message: types.Message, state: FSMContext):
    _mess = text(hbold('Центр макроэкономического анализа и краткосрочного прогнозирования'),
                 'Представлено неполное зекрало сайта Центра',
                 'Для перехода на сайт Центра - кнопка "Сайт Центра" в самом низу ленты',
                 hbold('Работа с данным ботом (команды вводятся только с кнопок бота):'),
                 'Выберете основной раздел (Новости, Аналитика и т.п.). По умолчанию показано 5 последних по времени публикации записей. Кнопками под списком можно увеличить выборку до 20 записей',
                 'Если раздел имеет подразделы (например, Мониторинг) под сообщением будет показано меню для выбора подраздела',
                 'Возврат в предидущее меню - кнопка Back в самом низу ленты (не привязано к сообщениям)',
                 'Возврат в главное меню (меню выбора раздела) - кнопка main. Если текущий просматриваемый раздел не имеет подразделов, то в главное меню возвращает кнопка back',
                 sep='\n')
    await bot.send_message(chat_id=message.chat.id, disable_web_page_preview=True,
                           text=_mess, reply_markup=main_menu(), parse_mode=ParseMode.HTML)
    await show_context_menu(message, state)

@dp.message_handler(commands='stop', state='*')
@dp.message_handler(Text(equals='stop'), state='*')
async def show_state(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(chat_id=message.chat.id, text='Надеюсь, еще увидимся!')

@dp.message_handler(state='*', commands='main')
@dp.message_handler(Text(equals='main'), state='*')
async def show_main(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get('current_R'):
        await bot.send_message(chat_id=message.chat.id,
                               text='Центр макроэкономического анализа и краткосрочного прогнозирования',
                               reply_markup=rplmain_menu(), parse_mode=ParseMode.HTML)
        await bot.send_message(chat_id=message.chat.id,
                               text='Выберете раздел', reply_markup=main_menu(), parse_mode=ParseMode.HTML)
        await state.finish()
        await OrderFood.select_rubr.set()


@dp.message_handler(state='*', commands='back')
@dp.message_handler(Text(equals='back'), state='*')
async def show_back(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if (user_data.get('current_R') == 'mons') and (user_data.get('select_mons') != 'main'):
        await state.update_data(current_R='mons', top=botserv.list_pages[0], select_mons='main')
        await bot.send_message(chat_id=message.chat.id, parse_mode=types.ParseMode.HTML,
                               text=hbold('МОНИТОРИНГИ'), reply_markup=rplmain_menu(show_main=True))
        await bot.send_message(chat_id=message.chat.id,
                               text='Выберете мониторинг', reply_markup=mons_menu())
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text='ОСНОВНОЕ МЕНЮ',
                               reply_markup=rplmain_menu(), parse_mode=ParseMode.HTML)
        await bot.send_message(chat_id=message.chat.id,
                               text='Выберете раздел', reply_markup=main_menu(), parse_mode=ParseMode.HTML)
        await state.finish()
        await OrderFood.select_rubr.set()


async def show_items(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    _top = user_data.get('top')
    show_back = False
    show_main = False
    try:
        header, _mess = botserv.dict_main[user_data.get('current_R')](top=_top)
        show_back = True
    except KeyError:
        if user_data.get('current_R') == 'mons':
            try:
                header, _mess = botserv.dict_mons[user_data.get('select_mons')](top=_top)
                show_main = True
            except:
                pass

    for mg in iterate_group(_mess, 5):
        await bot.send_message(chat_id=message.chat.id,
                               text=text(*mg, sep='\n\n'),
                               parse_mode=types.ParseMode.HTML, disable_web_page_preview=True,
                               reply_markup=rplmain_menu(show_main=show_main, show_back=show_back))
    await bot.send_message(chat_id=message.chat.id,
                           text=f'{header} показаны {_top} последних. Показать:', reply_markup=item_menu())


@dp.callback_query_handler(Text(equals=['news', 'notes', 'reps'], ignore_case=True), state=OrderFood.select_rubr)
async def process_items(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(current_R=callback_query.data, top=botserv.list_pages[0])
    await show_items(callback_query.message, state)


@dp.callback_query_handler(Text(equals='mons', ignore_case=True), state=OrderFood.select_rubr)
async def process_mons(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await OrderFood.select_mon.set()
    await state.update_data(current_R=callback_query.data, top=botserv.list_pages[0], select_mons='main')
    await bot.send_message(chat_id=callback_query.message.chat.id, parse_mode=types.ParseMode.HTML,
                           text=hbold('МОНИТОРИНГИ'), reply_markup=rplmain_menu(show_back=True))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Выберете мониторинг', reply_markup=mons_menu())


@dp.callback_query_handler(Text(equals=['infl', 'fin', 'trends', 'rail', 'tends',
                                        'santech', 'growtech', 'socmon', 'tez'],
                                ignore_case=True), state=OrderFood.select_mon)
async def process_mon_items(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(select_mons=callback_query.data, top=botserv.list_pages[0])
    await show_items(callback_query.message, state)


@dp.callback_query_handler(lambda cbm: cbm.data and cbm.data in list(map(str, botserv.list_pages)),
                           state=[OrderFood.select_rubr, OrderFood.select_mon])
async def process_news(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(top=int(callback_query.data))
    await show_items(callback_query.message, state)


@dp.callback_query_handler(state=OrderFood.select_rubr)
async def process_select(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(current_R=callback_query.data)
    _mess = 'Выберете раздел:'
    await bot.edit_message_text(message_id=callback_query.message.message_id,
                                chat_id=callback_query.message.chat.id,
                                parse_mode=types.ParseMode.HTML,
                                text=f'{_mess}{callback_query.data}', reply_markup=main_menu())
    ud = await state.get_data()
    print(ud)

@dp.message_handler(state='*')
async def echo(message: types.Message, state: FSMContext):
    await message.reply(text='Непонятная команда')
    await show_context_menu(message, state)


@dp.message_handler(content_types=ContentType.ANY, state='*')
async def unknown_message(msg: types.Message, state: FSMContext):
    message_text = text('Ха-ха. Вы пошутили - я тоже посмеялся',
                        '(help вам в помощь)')

    await bot.send_message(msg.from_user.id, message_text, parse_mode=types.ParseMode.HTML,
                           reply_markup=main_menu())
    await show_context_menu(msg, state)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
