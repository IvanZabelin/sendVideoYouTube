import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


def get_authenticated_service(channel_name, token_file=None):
    """Возвращает аутентифицированный YouTube API сервис."""
    
    if token_file and os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            credentials = pickle.load(token)
    else:
        # Если токен не найден, создаем новый
        credentials = None
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json', SCOPES)
        credentials = flow.run_console()

        # Сохраняем токен для будущих запусков
        if token_file:
            with open(token_file, 'wb') as token:
                pickle.dump(credentials, token)

    # Создаем YouTube API клиент
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube
