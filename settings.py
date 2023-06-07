import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from aiogram.dispatcher.filters.state import State, StatesGroup

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

admin_chat_id = 0 #id админа

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
    Choice_Employee_After_Prihod = State()
    Choice_Employee_After_Report = State()
    Choice_Interval_After_Prihod = State()
    Choice_Interval_After_Report = State()

states = {
    "UpdateName": ClientState.UpdateName,
    "Prihod": ClientState.Prihod,
    "TimeAndDate": ClientState.TimeAndDate,
    "InputTime": ClientState.InputTime,
    "InputReport": ClientState.InputReport,
    "InputDate": ClientState.InputDate,
    "ProductionReport": ClientState.ProductionReport,
    "OperationNames": ClientState.OperationNames,
    "ProjectsOutsideTasks": ClientState.ProjectsOutsideTasks,
    "ProjectsTasks": ClientState.ProjectsTasks,
    "FinishTimeOutsideTasks": ClientState.FinishTimeOutsideTasks,
    "NameProject": ClientState.NameProject,
    "NameDetails": ClientState.NameDetails,
    "SpoilageReport": ClientState.SpoilageReport,
    "OperationSpoilageNames": ClientState.OperationSpoilageNames,
    "ChoiceReasonSpoilage": ClientState.ChoiceReasonSpoilage,
    "NameSpoilageProject": ClientState.NameSpoilageProject,
    "VesSpoilage": ClientState.VesSpoilage,
    "GetPhotoSpoilage": ClientState.GetPhotoSpoilage,
    "FinishWork": ClientState.FinishWork,
    "InputFinishDate": ClientState.InputFinishDate,
    "InputFinishTime": ClientState.InputFinishTime,
    "Choice_Employee_After_Prihod": ClientState.Choice_Employee_After_Prihod,
    "Choice_Employee_After_Report": ClientState.Choice_Employee_After_Report,
    "Choice_Interval_After_Prihod": ClientState.Choice_Interval_After_Prihod,
    "Choice_Interval_After_Report": ClientState.Choice_Interval_After_Report
}

