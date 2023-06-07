from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher
from bs4 import BeautifulSoup
from requests import get
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta
from settings import sheet, name_operation, SAMPLE_SPREADSHEET_ID, directory, service_d, folder_id, states
from database import execute_read_query, connection_users, query_db



def get_now_date_and_time():
    page = get('http://www.unn.ru/time/')
    soup = BeautifulSoup(page.text, "html.parser")
    time = soup.find('div', id="servertime").text[1:-3]
    page = get('http://www.датасегодня.рф')
    soup = BeautifulSoup(page.text, "html.parser")
    date = soup.find('p', id="digital_date").text
    list_body = [date, time]
    return list_body


async def append_data(data):
    sheet.values().append(
        spreadsheetId = data[0],
        range = data[1],
        valueInputOption = "USER_ENTERED",
        insertDataOption = "INSERT_ROWS",
        body = data[2]
    ).execute()
    return


async def get_state(message: Message, keyboard: ReplyKeyboardMarkup, state: State, chat_id):
    if message.text == "За сегодня":
        interval = 1
    elif message.text == "За неделю":
        interval = 7
    elif message.text == "За месяц (30 дней)":
        interval = 30
    else:
        interval = int(message.text)
    result = {}
    data = get_now_date_and_time()[0].split('.')
    interval_data = datetime(int(data[2]), int(data[1]), int(data[0])) - timedelta(interval - 1)
    for i in name_operation:
        count_production = execute_read_query(connection_users, 'SELECT COUNT(work) FROM state WHERE date > ' + str(interval_data.strftime("%d-%m-%Y")) + ' AND work = "' + str(i) + '" AND id IN(SELECT id FROM users WHERE chat_id = "' + str(chat_id) + '") AND report = "production"')[0]
        ves_production = execute_read_query(connection_users, 'SELECT SUM(ves) FROM state WHERE date > ' + str(interval_data.strftime("%d-%m-%Y")) + ' AND work = "' + str(i) + '" AND id IN(SELECT id FROM users WHERE chat_id = "' + str(chat_id) + '") AND report = "production"')[0]
        count_spoilage = execute_read_query(connection_users, 'SELECT COUNT(work) FROM state WHERE date > ' + str(interval_data.strftime("%d-%m-%Y")) + ' AND work = "' + str(i) + '" AND id IN(SELECT id FROM users WHERE chat_id = "' + str(chat_id) + '") AND report = "spoilage"')[0]
        ves_spoilage = execute_read_query(connection_users, 'SELECT SUM(ves) FROM state WHERE date > ' + str(interval_data.strftime("%d-%m-%Y")) + ' AND work = "' + str(i) + '" AND id IN(SELECT id FROM users WHERE chat_id = "' + str(chat_id) + '") AND report = "spoilage"')[0]        
        if count_production == None:
            count_production = 0
        if ves_production == None:
            ves_production = 0
        if count_spoilage == None:
            count_spoilage = 0
        if ves_spoilage == None:
            ves_spoilage = 0
        result[i] = [count_production, ves_production, count_spoilage, ves_spoilage]
    name = execute_read_query(connection_users, "SELECT name FROM users WHERE chat_id=" + str(chat_id))[0]
    if interval == 1:
        text = name + ", результат за сегодня:\n\n"
    elif str(interval)[-1] == "1":
        text = ", результат за " + str(interval) + " день:\n\n"
    elif str(interval)[-1] in ["2", "3", "4"]:
        text = name + ", результат за " + str(interval) + " дня:\n\n"
    else:
        text = name + ", результат за " + str(interval) + " дней:\n\n"
    for i in name_operation:
        text += "<b><i>" + str(i) + "</i></b>" + ":\n✅<i>Производство</i>\n" + "->количество: " + str(result[i][0]) + "\n" + "->вес: " + str(result[i][1]) + "\n❌<i>Брак</i>\n" + "->количество: " + str(result[i][2]) + "\n" + "->вес: " + str(result[i][3]) + "\n\n"
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    await state.set()


async def Get_Time_Auto(message: Message, action):
    list_body = get_now_date_and_time()
    list_body.append(execute_read_query(connection_users, "SELECT name FROM users WHERE chat_id=" + str(message.chat.id))[0])
    list_body.append(action)
    body = {"values": [list_body]}
    range_update = "Приход/Уход!A2"
    await append_data(data=[SAMPLE_SPREADSHEET_ID, range_update, body])
    

async def append_user(message: Message):
    new_id = None
    try:
        new_id = execute_read_query(connection_users, "SELECT MAX(id) FROM users")[0]
    except:
        print()
    if new_id == None:
        new_id = -1
    elif execute_read_query(connection_users, "SELECT MIN(id) FROM users")[0] != 0:
        new_id = execute_read_query(connection_users, "SELECT MIN(id) FROM users")[0] - 2
    await query_db(connection_users, "INSERT INTO users (id, chat_id, name) VALUES (" + str(new_id + 1) + ", " + str(message.chat.id) + ", '" + str(message.text) + "')")


async def write_in_production(message: Message, work_information: FSMContext):
    range_update = "Отчёт по производству!A2"
    date = work_information._data.get('date')
    name = work_information._data.get('name')
    name_operation = work_information._data.get('name_operation')
    name_project = work_information._data.get('name_project')
    ves = work_information._data.get('ves')
    start_time = work_information._data.get('start_time')
    name_details = work_information._data.get('name_details')
    finish_time = work_information._data.get('finish_time')
    id_user = execute_read_query(connection_users, "SELECT id FROM users where chat_id = " + str(message.chat.id))[0]
    body = {
            "values" : [
                [date, name, name_operation, name_project, ves, start_time, name_details, finish_time]
            ]
        }
    await append_data(data=[SAMPLE_SPREADSHEET_ID, range_update, body])
    if name_operation != "Задачи вне проектов":
        await query_db(connection_users, "INSERT INTO state (id, date, work, ves, report) VALUES ('" + str(id_user) + "', '" + str(date) + "', '" + str(name_operation) + "', '" + str(ves) + "', 'production')")


async def write_in_spoilage(message: Message, work_information: FSMContext):
    date = work_information._data.get('date')
    name_operation = work_information._data.get('name_operation')
    reason = work_information._data.get('reason')
    name_project = work_information._data.get('name_project')
    ves = work_information._data.get('ves')
    link_photo = work_information._data.get('link_photo')
    name = work_information._data.get('name')
    id_user = execute_read_query(connection_users, "SELECT id FROM users where chat_id = " + str(message.chat.id))[0]
    range_update = "Брак производства!A2"
    body = {
            "values" : [
                [date, name, name_operation, name_project, ves, link_photo, reason]
            ]
        }
    await append_data(data=[SAMPLE_SPREADSHEET_ID, range_update, body])
    await query_db(connection_users, "INSERT INTO state (id, date, work, ves, report) VALUES ('" + str(id_user) + "', '" + str(date) + "', '" + str(name_operation) + "', '" + str(ves) + "', 'spoilage')")


async def write_time_manually(message: Message, action, work_information: FSMContext):
    date = work_information._data.get('date')
    time = work_information._data.get('time')
    name = execute_read_query(connection_users, "SELECT name FROM users WHERE chat_id=" + str(message.chat.id))[0]
    range_update = "Приход/Уход!A2"
    body = {
            "values" : [
                [date, time, name, action]
            ]
        }
    await append_data(data=[SAMPLE_SPREADSHEET_ID, range_update, body])


def Get_link_photo(message: Message):
    name = str(get_now_date_and_time())[1:-1]
    file_path = directory + "/" + execute_read_query(connection_users, "SELECT name FROM users where chat_id = " + str(message.chat.id))[0] + "_photo.jpg"
    file_metadata = {
                'name': name,
                'parents': [folder_id]
            }
    media = MediaFileUpload(file_path, resumable=True)
    id_photo_in_drive = service_d.files().create(body=file_metadata, media_body=media, fields='id').execute()
    photo_link = "https://drive.google.com/file/d/" + id_photo_in_drive['id'] + "/view?usp=share_link"
    return photo_link, file_path


async def update_client_state(state: StatesGroup, chat_id):
    new_state = str(state).split(':')[1]
    if chat_id in execute_read_query(connection_users, "SELECT chat_id FROM client_states"):
        await query_db(connection_users, "UPDATE client_states SET state='" + new_state + "' WHERE chat_id=" + str(chat_id))
    else:
        await query_db(connection_users, "INSERT INTO client_states (chat_id, state) VALUES (" + str(chat_id) + ", '" + new_state + "')")


async def set_users_state(dp: Dispatcher):
    chat_id_list = execute_read_query(connection_users, "SELECT chat_id FROM client_states")
    for chat_id in chat_id_list:
        state = dp.current_state(chat=chat_id)
        await state.set_state(states[execute_read_query(connection_users, "SELECT state FROM client_states WHERE chat_id=" + str(chat_id))[0]])


def create_list_kb() -> ReplyKeyboardMarkup:
    name_list = execute_read_query(connection_users, "SELECT name FROM users")
    kb = []
    for name in name_list:
        kb.append([KeyboardButton(name)])
    dynamic_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return dynamic_kb