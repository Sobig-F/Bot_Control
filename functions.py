from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from bs4 import BeautifulSoup
from requests import get
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta
from settings import sheet, month, name_operation, SAMPLE_SPREADSHEET_ID, directory, service_d, folder_id
from database import execute_read_query, connection_users, query_db
from keyboards import reports_block


def get_now_date_and_time(chat_id):
    page = get('https://time100.ru/Kazan')
    soup = BeautifulSoup(page.text, "html.parser")
    time = soup.find('span', class_ = "time").text
    data = soup.find('h3', class_ = "display-date monospace").text.split(' ')
    date = data[1] + "." + month[data[2]] + "." + data[3]
    name = execute_read_query(connection_users, "SELECT name FROM users WHERE chat_id=" + str(chat_id))[0]
    list_body = [date, time, name]
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


async def get_state(name, interval):
    result = {}
    data = get_now_date_and_time()[0].split('.')
    interval_data = datetime(int(data[3]), int(month[data[2]]), int(data[1])) - timedelta(interval - 1)
    for i in name_operation:
        count = execute_read_query(connection_users, 'SELECT COUNT(work) FROM state WHERE date > ' + str(interval_data.strftime("%d-%m-%Y")) + ' AND work = "' + str(i) + '" AND id IN(SELECT id FROM users WHERE name = "' + name + '")')[0]
        ves = execute_read_query(connection_users, 'SELECT SUM(ves) FROM state WHERE date > ' + str(interval_data.strftime("%d-%m-%Y")) + ' AND work = "' + str(i) + '" AND id IN(SELECT id FROM users WHERE name = "' + name + '")')[0]
        if count == None:
            count = 0
        if ves == None:
            ves = 0
        result[i] = [count, ves]
    if interval == 1:
        message = "Ваш результат за сегодня:\n\n"
    elif str(interval)[-1] == "1":
        message = "Ваш результат за " + str(interval) + " день:\n\n"
    elif str(interval)[-1] in ["2", "3", "4"]:
        message = "Ваш результат за " + str(interval) + " дня:\n\n"
    else:
        message = "Ваш результат за " + str(interval) + " дней:\n\n"
    for i in name_operation:
        message += "<b>" + str(i) + "</b>" + ":\n" + "->количество: " + str(result[i][0]) + "\n" + "->вес: " + str(result[i][1]) + "\n\n"
    return message


async def Generate_state(message: Message):
    if message.text == "За сегодня":
        interval = 1
    elif message.text == "За неделю":
        interval = 7
    elif message.text == "За месяц (30 дней)":
        interval = 30
    else:
        interval = int(message.text)
    text = get_state(execute_read_query(connection_users, "SELECT name FROM users where chat_id = " + str(message.chat.id))[0], interval)
    await message.answer(text, reply_markup=reports_block, parse_mode="HTML")


async def Get_Time_Auto(message: Message, action):
    list_body = get_now_date_and_time(message.chat.id)
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
    await query_db(connection_users, "INSERT INTO state (id, date, work, ves) VALUES ('" + str(id_user) + "', '" + str(date) + "', '" + str(name_operation) + "', '" + str(ves) + "')")


async def write_in_spoilage(message: Message, work_information: FSMContext):
    date = work_information._data.get('date')
    name_operation = work_information._data.get('name_operation')
    reason = work_information._data.get('reason')
    name_project = work_information._data.get('name_project')
    ves = work_information._data.get('ves')
    link_photo = work_information._data.get('link_photo')
    name = work_information._data.get('name')
    range_update = "Брак производства!A2"
    body = {
            "values" : [
                [date, name, name_operation, name_project, ves, link_photo, reason]
            ]
        }
    await append_data(data=[SAMPLE_SPREADSHEET_ID, range_update, body])


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
    name = str(get_now_date_and_time(message.chat.id)[0:2])[1:-1]
    file_path = directory + "/" + execute_read_query(connection_users, "SELECT name FROM users where chat_id = " + str(message.chat.id))[0] + "_photo.jpg"
    file_metadata = {
                'name': name,
                'parents': [folder_id]
            }
    media = MediaFileUpload(file_path, resumable=True)
    id_photo_in_drive = service_d.files().create(body=file_metadata, media_body=media, fields='id').execute()
    photo_link = "https://drive.google.com/file/d/" + id_photo_in_drive['id'] + "/view?usp=share_link"
    return photo_link, file_path