import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

directory = str(os.path.dirname(__file__))

Password = ""

TOKEN = "" #токен бота
            
folder_id = '' #id папки для фото на гугл диске

SERVICE_ACCOUNT_FILE = directory + '/credentials.json' #заменить файл credentials.py

SAMPLE_SPREADSHEET_ID = '' #id таблицы из ссылки
                        
SCOPES_t = ['https://www.googleapis.com/auth/spreadsheets']

SCOPES_d = ['https://www.googleapis.com/auth/drive']

credentials_t = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_t)

credentials_d = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_d)

service_t = build('sheets', 'v4', credentials=credentials_t)
sheet = service_t.spreadsheets()

service_d = build('drive', 'v3', credentials=credentials_d)

name_operation = ["Литьё пластика", "Изготовление матрицы", "Изготовление мастер модели", "3D печать", "Мех.обработка"]

month = {
    "января": "01",
    "февраля": "02",
    "марта": "03",
    "апреля": "04",
    "мая": "05",
    "июня": "06",
    "июля": "07",
    "августа": "08",
    "сентября": "09",
    "октября": "10",
    "ноября": "11",
    "декабря": "12",
}

