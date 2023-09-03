from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.models import CharityProject

FORMAT = '%Y/%m/%d %H:%M:%S'
ROWCOUNT = 1000
COLUMNCOUNT = 10
SHEETS_VERSION = {'sheets': 'v4'}
DRIVE_VERSION = {'drive': 'v3'}
LOCALE = 'ru_RU'
SHEET_RANGE = 'A1:E30'


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover(SHEETS_VERSION)
    spreadsheet_body = {
        'properties': {'title': f'Отчет на {now_date_time}',
                       'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': 'Лист1',
                                   'gridProperties': {ROWCOUNT,
                                                      COLUMNCOUNT}}}]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover(DRIVE_VERSION)
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields='id'
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        charity_projects: list[CharityProject],
        wrapper_services: Aiogoogle
) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover(SHEETS_VERSION)

    table_values = [
        ['Отчет от', now_date_time],
        ['Рейтинг проектов по скорости сборов денежных средств.'],
        ['Название проекта', 'Продолжительность сборов ', 'Описание']
    ]
    for project in charity_projects:
        new_row = [str(project['project.name']),
                   str(project['project.close_date - project.create_date']),
                   str(project['project.description']),
                   ]
        table_values.append(new_row)

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=SHEET_RANGE,
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )

    return spreadsheet_id
