from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.utils.executor import start_polling
import os, asyncio
from settings import TOKEN, Password, directory
import keyboards
from database import execute_read_query, query_db, table_state, table_users, connection_users
from functions import *


#Класс состояний
class ClientState(StatesGroup):
    UpdateName = State()
    Prihod = State()
    TimeAndDate = State()
    InputTime = State()
    InputReport = State()
    InputDate = State()
    ProductionReport = State()
    OperationNames = State()
    ProjectsOutsideTasks = State()
    ProjectsTasks = State()
    FinishTimeOutsideTasks = State()
    NameProject = State()
    NameDetails = State()
    SpoilageReport = State()
    OperationSpoilageNames = State()
    ChoiceReasonSpoilage = State()
    NameSpoilageProject = State()
    VesSpoilage = State()
    GetPhotoSpoilage = State()
    FinishWork = State()
    InputFinishDate = State()
    InputFinishTime = State()


storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot,
                storage=storage)


#Приветственное сообщение
@dp.message_handler(commands=["start"], state=None)
async def start_command(message: Message):
    #Прверка, есть пользователь в базе данных
    if (message.chat.id) not in execute_read_query(connection_users, "SELECT chat_id FROM users"):
        if message.text == "/start " + Password:
            await message.answer("Вас нет в базе данных\nОтправьте своё ФИО")
            await ClientState.UpdateName.set()
        else:
            await message.answer("У вас нет доступа к этому боту(")
    else:
            await ClientState.Prihod.set()
            await message.answer("<b>Добро пожаловать в бота</b>", reply_markup=keyboards.come_in_block, parse_mode="HTML")


#Добавление нового пользователя в базу данных
@dp.message_handler(state=ClientState.UpdateName)
async def Update_name(message: Message):
    await append_user(message)
    await message.answer("Имя сохранено", reply_markup=keyboards.come_in_block)
    await ClientState.Prihod.set()


#Направление на указание времени прихода
@dp.message_handler(state=ClientState.Prihod)
async def prihod(message: Message):
    if message.text == "Приход":
        await ClientState.TimeAndDate.set()
        await message.answer("Выберите способ указания даты и времени", reply_markup=keyboards.time_block)
    elif message.text == "Просмотр статистики":
        await message.answer("Отправьте количество дней или выберите из предложенных вариантов: ", reply_markup = keyboards.state_interval)
    else:
        await Generate_state(message)


#Добавление времени прихода
@dp.message_handler(state=ClientState.TimeAndDate)
async def time_and_date(message: Message):
    if message.text == "Взять текущее":
        await Get_Time_Auto(message, "Приход")
        await message.answer("Данные занесены в таблицу", reply_markup=keyboards.reports_block)
        await ClientState.InputReport.set()
    elif message.text == "Указать вручную":
        await ClientState.InputDate.set()
        await message.answer("Отправьте дату в формате ДД.ММ.ГГГГ")


#Сохранение даты и запрос времени прихода
@dp.message_handler(state=ClientState.InputDate)
async def input_date(message: Message, state: FSMContext):
    await message.answer("Теперь отправьте время в формате ЧЧ:ММ")
    async with state.proxy() as work_information:
        work_information['date'] = message.text
    await ClientState.InputTime.set()


#Сохранение врмени прихода и занесение данных в таблицу "Приход/Уход"
@dp.message_handler(state=ClientState.InputTime)
async def input_time(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['time'] = message.text
    await write_time_manually(message, "Приход", work_information)
    await state.finish()
    await message.answer("Данные занесены в таблицу", reply_markup=keyboards.reports_block)
    await ClientState.InputReport.set()


#Выбор отчёта для заполнения и кнопка "Уход"
@dp.message_handler(state=ClientState.InputReport)
async def input_report(message: Message, state: FSMContext):
    if message.text == "Отчёт производства":
        list_body = get_now_date_and_time(message.chat.id)
        async with state.proxy() as work_information:
            work_information['date'] = list_body[0]
        await ClientState.OperationNames.set()
        await message.answer("Выберите название операции", reply_markup=keyboards.operations_names_block)
    elif message.text == "Отчёт по браку":
        list_body = get_now_date_and_time(message.chat.id)
        async with state.proxy() as work_information:
            work_information['date'] = list_body[0]
        await ClientState.OperationSpoilageNames.set()
        await message.answer("Выберите, где обнаружен брак", reply_markup=keyboards.place_of_spoilage_detection)
    elif message.text == "Уход":
        await ClientState.FinishWork.set()
        await message.answer("Выберите способ указания времени", reply_markup=keyboards.time_block)
    elif message.text == "Просмотр статистики":
        await message.answer("Отправьте количество дней или выберите из предложенных вариантов: ", reply_markup = keyboards.state_interval)
    else:
        await Generate_state(message)


#Выбор названия операции на клавиатуре
@dp.message_handler(state=ClientState.OperationNames)
async def operanion_names(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['name_operation'] = message.text
    if message.text == "Задачи вне проектов":
        async with state.proxy() as work_information:
            work_information['ves'] = "-"
            work_information['name_details'] = "-"
        await ClientState.ProjectsOutsideTasks.set()
        await message.answer("Отправьте время начала операции в формате ЧЧ:ММ")
    else:
        async with state.proxy() as work_information:
            work_information['start_time'] = "-"
            work_information['finish_time'] = "-"
        await ClientState.ProjectsTasks.set()
        await message.answer("Отправьте вес в граммах")


#Заполнение времени начала и конца работы для задач вне проектов
@dp.message_handler(state=ClientState.ProjectsOutsideTasks)
async def projects_outside_tasks(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['start_time'] = message.text
    await ClientState.FinishTimeOutsideTasks.set()
    await message.answer("Теперь отправьте время окончания работы")
    

@dp.message_handler(state=ClientState.FinishTimeOutsideTasks)
async def finish_time_outside_tasks(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['finish_time'] = message.text
    await ClientState.NameProject.set()
    await message.answer("Отправьте наименование проекта")


#Заполнение веса для отчёта производства
@dp.message_handler(state=ClientState.ProjectsTasks)
async def project_tasks(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['ves'] = message.text
    await ClientState.NameDetails.set()
    await message.answer("Отправте название детали")


#заполнение названия деталей для отчёта производства
@dp.message_handler(state=ClientState.NameDetails)
async def name_details(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['name_details'] = message.text
    await ClientState.NameProject.set()
    await message.answer("Отправтье наименование проекта")


#Заполнение имени проекта для отчёта производства и сохранение отчёта в таблицу
@dp.message_handler(state=ClientState.NameProject)
async def name_project(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['name_project'] = message.text
        work_information['name'] = execute_read_query(connection_users, "SELECT name FROM users where chat_id = " + str(message.chat.id))[0]
    await write_in_production(message, work_information)
    await state.finish()
    await ClientState.InputReport.set()
    await message.answer("Данные отправлены", reply_markup=keyboards.reports_block)


@dp.message_handler(state=ClientState.OperationSpoilageNames)
async def operation_spoilage_name(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['name_operation'] = message.text
    await message.answer("Укажите причину возникеновения брака")
    await ClientState.ChoiceReasonSpoilage.set()


@dp.message_handler(state=ClientState.ChoiceReasonSpoilage)
async def choice_reason_spoilage(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['reason'] = message.text
    await message.answer("Отправьте наименование проекта")
    await ClientState.NameSpoilageProject.set()


@dp.message_handler(state=ClientState.NameSpoilageProject)
async def name_spoilage_project(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['name_project'] = message.text
    await message.answer("Отправьте вес в граммах")
    await ClientState.VesSpoilage.set()


@dp.message_handler(state=ClientState.VesSpoilage)
async def ves_spoilage(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['ves'] = message.text
    await message.answer("Прикрепите фотографию")
    await ClientState.GetPhotoSpoilage.set()


@dp.message_handler(state=ClientState.GetPhotoSpoilage, content_types=['photo'])
async def get_photo_spoilage(message: Message, state: FSMContext):
    await message.photo[-1].download(destination_file=directory + "/" + execute_read_query(connection_users, "SELECT name FROM users where chat_id = " + str(message.chat.id))[0] + "_photo.jpg")
    photo_link, file_path = Get_link_photo(message)
    async with state.proxy() as work_information:
        work_information['link_photo'] = photo_link
        work_information['name'] = execute_read_query(connection_users, "SELECT name FROM users where chat_id = " + str(message.chat.id))[0]
    await write_in_spoilage(message, work_information)
    os.remove(file_path)
    await state.finish()
    await ClientState.InputReport.set()
    await message.answer("Данные отправлены", reply_markup=keyboards.reports_block)


#Выбор врмени заполнения ухода
@dp.message_handler(state=ClientState.FinishWork)
async def finish_work(message: Message, state: FSMContext):
    if message.text == "Взять текущее":
        await Get_Time_Auto(message, "Уход")
        await message.answer("Время отправлено", reply_markup=keyboards.come_in_block)
        await ClientState.Prihod.set()
    elif message.text == "Указать вручную":
        await ClientState.InputFinishDate.set()
        await message.answer("Отправьте дату в формате ДД.ММ.ГГГГ")


#Ручное заполнение даты для ухода
@dp.message_handler(state=ClientState.InputFinishDate)
async def input_finish_date(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['date'] = message.text
    await ClientState.InputFinishTime.set()
    await message.answer("Теперь отправьте время в формате ЧЧ:ММ")


#Ручное заполнение времени для ухода
@dp.message_handler(state=ClientState.InputFinishTime)
async def input_finish_time(message: Message, state: FSMContext):
    async with state.proxy() as work_information:
        work_information['time'] = message.text
    await write_time_manually(message, "Уход", work_information)
    await ClientState.Prihod.set()
    await message.answer("Время отправлено", reply_markup=keyboards.come_in_block)


async def main():
    await query_db(connection_users, table_users)
    await query_db(connection_users, table_state)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    start_polling(dp, skip_updates=True)
