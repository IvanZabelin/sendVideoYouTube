import os
import pytz
from datetime import datetime, timedelta
from googleapiclient.http import MediaFileUpload
from app.oauth_helper import get_authenticated_service
import requests
import socket
from urllib.parse import urlparse

def set_proxy(proxies):
    """
    Устанавливает прокси для HTTP, HTTPS и SOCKS-прокси.
    """
    if proxies:
        # Обрабатываем строку прокси для SOCKS
        if 'http' in proxies or 'https' in proxies:
            os.environ['HTTP_PROXY'] = proxies.get('http', '')
            os.environ['HTTPS_PROXY'] = proxies.get('https', '')
        if 'proxy' in proxies:
            proxy_url = proxies['proxy']
            # Парсим URL прокси (например, "socks5://78.137.88.129:1080")
            parsed_proxy = urlparse(proxy_url)
            if parsed_proxy.scheme == 'socks5':
                try:
                    import socks
                    from urllib.request import setproxies
                    socket.socket = socks.socksocket  # Замена сокета на SOCKS
                    socks.set_default_proxy(socks.SOCKS5, parsed_proxy.hostname, parsed_proxy.port)
                    print(f"Используется SOCKS5 прокси: {parsed_proxy.hostname}:{parsed_proxy.port}")
                except ImportError:
                    print("Ошибка: библиотека PySocks не установлена для работы с SOCKS.")
                    raise
            else:
                print(f"Не поддерживаемый прокси-тип: {parsed_proxy.scheme}. Используйте 'socks5'.")
                raise ValueError("Только SOCKS5 поддерживаются.")
    else:
        print("Прокси не используется.")


def test_proxy_connection(proxies):
    """
    Проверяет доступность прокси, выполняя запрос.
    """
    try:
        response = requests.get("https://www.google.com", proxies=proxies, timeout=10)
        response.raise_for_status()
        print("Прокси работает.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при подключении через прокси: {e}")


def upload_video(
        channel_name,
        video_file_path,
        title,
        description,
        tags,
        privacy_status="private",
        publish_time=None,
        token_directory=None,
        proxies=None,
):
    """
    Загружает видео на указанный аккаунт YouTube.
    """
    # Установить переменные окружения для прокси, если указано
    set_proxy(proxies)

    # Преобразуем путь к видео в абсолютный путь, если это относительный путь
    video_file_path = os.path.abspath(video_file_path)

    # Убедимся, что файл существует
    if not os.path.exists(video_file_path):
        print(f"Ошибка: файл не найден {video_file_path}")
        return

    print(f"Загружаем видео: {video_file_path} на канал {channel_name}...")

    # Получаем путь к токену
    token_file = os.path.join(token_directory, f'{channel_name}_token.pkl')

    # Проверяем существование файла токена
    if not os.path.exists(token_file):
        print(f"Ошибка: токен для канала {channel_name} не найден!")
        return

    youtube = get_authenticated_service(channel_name, token_file)

    # Проверка и обработка времени публикации
    if publish_time:
        try:
            # Парсим время публикации как московское время
            timezone_moscow = pytz.timezone('Europe/Moscow')
            publish_time_local = datetime.strptime(publish_time, "%Y-%m-%dT%H:%M:%S")
            publish_time_moscow = timezone_moscow.localize(publish_time_local)

            # Преобразуем в UTC
            publish_time_utc = publish_time_moscow.astimezone(pytz.utc).replace(microsecond=0)
            now = datetime.now(pytz.utc)

            # Проверяем, что время публикации не меньше чем через 15 минут
            if publish_time_utc < now + timedelta(minutes=15):
                print("Ошибка: время публикации должно быть не менее чем через 15 минут.")
                return

            # Преобразуем в строку ISO-формата
            publish_time = publish_time_utc.isoformat()
        except ValueError as e:
            print(f"Ошибка формата времени публикации: {e}")
            return

    # Настройка медиафайла
    media = MediaFileUpload(
        video_file_path, chunksize=-1, resumable=True, mimetype='video/*')

    # Формируем тело запроса
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags.split(","),
            "categoryId": "22"  # Например, категория "People & Blogs"
        },
        "status": {
            "privacyStatus": privacy_status  # "private" для отложенной публикации
        }
    }

    if privacy_status == "private" and publish_time:
        body["status"]["publishAt"] = publish_time

    # Выполнение загрузки
    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )
        response = request.execute()
        print(f"Видео успешно загружено! ID: {response['id']}")
    except Exception as e:
        print(f"Ошибка при загрузке видео {video_file_path}: {e}")
