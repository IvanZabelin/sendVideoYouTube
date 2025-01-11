import json
import os
from app.upload_video import upload_video, test_proxy_connection


def upload_videos_from_tasks(task_file, video_directory, token_directory):
    """
    Загружает видео на YouTube, используя задачи из JSON файла и настройки прокси.
    """
    # Загружаем список задач
    with open(task_file, 'r', encoding='utf-8') as file:
        tasks = json.load(file)

    # Выполняем задачи
    for task in tasks:
        print(f"Загружаем видео: {task['video_file_path']} на канал {task['channel_name']}...")

        # Формируем абсолютный путь к видео
        video_file_path = os.path.join(video_directory, task['video_file_path'])

        # Настройка прокси
        proxy = task.get('proxy')
        proxies = {"http": proxy, "https": proxy} if proxy else None

        # Проверяем прокси
        if proxies:
            try:
                test_proxy_connection(proxies)
            except Exception as e:
                print(f"Прокси для {task['channel_name']} недоступен: {e}")
                continue

        # Передаем путь к токенам и настройки прокси в функцию загрузки
        try:
            upload_video(
                channel_name=task['channel_name'],
                video_file_path=video_file_path,
                title=task['title'],
                description=task['description'],
                tags=task['tags'],
                privacy_status=task.get('privacy_status', 'private'),
                publish_time=task.get('publish_time'),  # Время публикации
                token_directory=token_directory,  # Добавляем путь к папке с токенами
                proxies=proxies  # Добавляем настройки прокси
            )
        except Exception as e:
            print(f"Ошибка при загрузке видео {task['video_file_path']}: {e}")
