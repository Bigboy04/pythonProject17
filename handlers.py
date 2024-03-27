import re

from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, User, InputFile, BufferedInputFile
from aiogram import F, types
from aiogram.fsm.state import default_state
from bot import dp, bot
from kb import cost_calculation_keyboard, create_inline_kb, create_reply_kb
from states import CostCalculateStates
from utils import RaschetStoimosti

pattern = r'^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$'


@dp.message(Command("start"))
async def start_command_handler(message: Message):
    print("start")
    await message.answer('''Доброго времени суток,
Мы рады вас приветствовать в нашем боте. 
Он предназначен для рассчета стоимости лестниц.''', reply_markup=cost_calculation_keyboard())


@dp.message(F.text == 'Рассчитать стоимость')
async def cost_calculate_sent(message: Message, state: FSMContext):
    await state.set_state(CostCalculateStates.type_of_stairs)
    await message.answer('Выберите тип лестницы:',
                         reply_markup=create_reply_kb(["Прямая",
                                                       "Г - образная (с забежными ступенями)",
                                                       "Г - образная (с площадкой)",
                                                       "П - образная (с забежными ступенями)",
                                                       "П - образная (с площадкой)"]))


@dp.message(StateFilter(CostCalculateStates.type_of_stairs), F.text != '')
async def type_of_stairs_sent(message: Message, state: FSMContext):
    match message.text:
        case "Прямая":
            t = 1
        case "Г - образная (с забежными ступенями)":
            t = 2
        case "Г - образная (с площадкой)":
            t = 3
        case "П - образная (с забежными ступенями)":
            t = 4
        case "П - образная (с площадкой)":
            t = 5
    await state.update_data(type_of_stairs=t)
    await state.set_state(CostCalculateStates.opening)
    await message.answer('Какая лестница вам нужна',
                         reply_markup=create_reply_kb(["Открытая", "Закрытая"], one_time_keyboard=True))


@dp.message(StateFilter(CostCalculateStates.opening), F.text != '')
async def opening_sent(message: Message, state: FSMContext):
    match message.text:
        case "Открытая":
            t = 0
        case "Закрытая":
            t = 1
    await state.update_data(opening=t)
    await state.set_state(CostCalculateStates.height_from_floor_to_floor)
    await message.answer("Введите высоту от пола до пола в мм")


@dp.message(lambda message: not message.text.isdigit(), StateFilter(CostCalculateStates.height_from_floor_to_floor))
async def not_height_from_floor_to_floor_sent(message: Message, state: FSMContext):
    await message.answer('''Неправильно введено значение,
Введите высоту от пола до пола в мм''')


@dp.message(StateFilter(CostCalculateStates.height_from_floor_to_floor), F.text.isdigit())
async def height_from_floor_to_floor_sent(message: Message, state: FSMContext):
    await state.update_data(height_from_floor_to_floor=message.text)
    await state.set_state(CostCalculateStates.fence)
    await message.answer("Выберите тип ограждения:",
                         reply_markup=create_reply_kb(
                             ['Нет - без ограждений по маршу',
                              'Ограждение по 1 стороне марша',
                              'Ограждение по 2-м сторонам марша',
                              'Ограждение по 1 стороне марша + поручень по стене'], one_time_keyboard=True))


@dp.message(StateFilter(CostCalculateStates.fence), F.text != '')
async def fence_sent(message: Message, state: FSMContext):
    match message.text:
        case 'Нет - без ограждений по маршу':
            t = 0
        case 'Ограждение по 1 стороне марша':
            t = 1
        case 'Ограждение по 2-м сторонам марша':
            t = 2
        case 'Ограждение по 1 стороне марша + поручень по стене':
            t = 3
    await state.update_data(fence=t)
    await state.set_state(CostCalculateStates.k)
    await message.answer(
        "Если нужно ограждение на второй этаж - введите значение в пог. м.\nЕсли не нужно - введите 0")


@dp.message(lambda message: not re.match(pattern, message.text), StateFilter(CostCalculateStates.k))
async def not_k_sent(message: Message, state: FSMContext):
    await message.answer('''Неправильно введено значение,
Если нужно ограждение на второй этаж - введите значение в пог. м.
Если не нужно - введите 0''')


@dp.message(StateFilter(CostCalculateStates.k), F.text.regexp(pattern))
async def k_sent(message: Message, state: FSMContext):
    await state.update_data(k=message.text)
    await state.set_state(CostCalculateStates.rounding)
    await message.answer("Закруглить ступени: ",
                         reply_markup=create_reply_kb(
                             ['Нет',
                              'Одна пригласительная ступень',
                              'Две или более пригласительные ступени',
                              'Одна в две стороны',
                              'Две или более в две стороны']))


@dp.message(StateFilter(CostCalculateStates.rounding), F.text != '')
async def rounding_sent(message: Message, state: FSMContext):
    match message.text:
        case 'Нет':
            t = 0
        case 'Одна пригласительная ступень':
            t = 1
        case 'Две или более пригласительные ступени':
            t = 2
        case 'Одна в две стороны':
            t = 3
        case 'Две или более в две стороны':
            t = 4
    await state.update_data(rounding=t)
    data = await state.get_data()
    rs = RaschetStoimosti(int(data['type_of_stairs']), int(data['opening']), int(data['height_from_floor_to_floor']),
                          int(data['fence']), float(data['k']), int(data['rounding']))
    output_file = rs.create_table_1()
    document = BufferedInputFile(output_file.getvalue(), filename='Расчет Стоимости.xlsx')
    await message.answer(f'Стоимость:\nСорт В: {rs.arr2[0]} руб.\nСорт А: {rs.arr2[1]} руб.\nЛиственница: {rs.arr2[2]} руб.\nДуб: {rs.arr2[3]} руб.')
    await bot.send_document(chat_id=message.from_user.id, caption='''
Файл расчета стоимости:
Для корректного отображения откройте его в MS Excel или Google Таблицы''',
                            document=document,
                            reply_markup=cost_calculation_keyboard())
    await state.clear()


@dp.message(StateFilter(default_state), F.text != 'Рассчитать стоимость')
async def hz_command_handler(message: Message):
    await message.answer('''Неизвестная команда,
Если вы хотите рассчитать стоимость, нажмите на кнопку''', reply_markup=cost_calculation_keyboard())
