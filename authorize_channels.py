import os
import json
import pickle
import tkinter as tk
from tkinter import filedialog
from google_auth_oauthlib.flow import InstalledAppFlow


# Получение и сохранение токена
def save_token(client_id_json, token_file):
    """Получение токена для канала и сохранение его."""
    flow = InstalledAppFlow.from_client_secrets_file(
        client_id_json, scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )

    credentials = flow.run_local_server(port=0)

    # Сохранение токенов
    with open(token_file, 'wb') as token:
        pickle.dump(credentials, token)

    print(f"Токен для {client_id_json} сохранен в {token_file}")


# Загрузка сохраненного токена
def load_token(token_file):
    """Загружает токен из файла, если он существует."""
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            return pickle.load(token)
    return None


# Функция для обработки всех каналов
def process_channels(config_file, token_directory):
    """Обрабатывает каналы, получает для каждого токен и сохраняет его."""
    with open(config_file, 'r') as file:
        config = json.load(file)

    for project in config:
        client_id_json = project["client_id_json"]
        channel_name = project["channel_name"]
        
        # Имя файла для хранения токена
        token_file = os.path.join(token_directory, f"{channel_name}_token.pkl")
        
        # Если токен для канала уже существует, пропускаем
        if not os.path.exists(token_file):
            print(f"Получение токена для канала {channel_name}...")
            save_token(client_id_json, token_file)
        else:
            print(f"Токен для канала {channel_name} уже существует.")


# Функция для выбора пути к файлу и папке
def select_file_and_folder():
    # Создаем главное окно для tkinter (оно не будет отображаться)
    root = tk.Tk()
    root.withdraw()

    # Окно выбора файла конфигурации
    config_file = filedialog.askopenfilename(
        title="Выберите файл конфигурации JSON", 
        filetypes=[("JSON Files", "*.json")]
    )

    # Окно выбора папки для хранения токенов
    token_directory = filedialog.askdirectory(
        title="Выберите папку для хранения токенов"
    )

    return config_file, token_directory


if __name__ == '__main__':
    # Запрашиваем у пользователя файл конфигурации и папку для токенов
    config_file, token_directory = select_file_and_folder()

    # Проверяем, что пользователь выбрал файлы
    if not config_file or not token_directory:
        print("Не выбран файл конфигурации или папка для токенов. Завершаем.")
    else:
        # Создание папки для токенов, если её нет
        if not os.path.exists(token_directory):
            os.makedirs(token_directory)
        
        # Обработка всех каналов
        process_channels(config_file, token_directory)
