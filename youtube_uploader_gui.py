import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import os
from app.upload_multiple_videos import upload_videos_from_tasks
from authorize_channels import process_channels
import requests
import json

def select_directory(title):
    """Функция для выбора папки."""
    directory = filedialog.askdirectory(title=title)
    if not directory:
        messagebox.showwarning("Ошибка", f"{title} не выбрана!")
        return None
    return directory

def select_file(title, file_types):
    """Функция для выбора файла."""
    file = filedialog.askopenfilename(title=title, filetypes=file_types)
    if not file:
        messagebox.showwarning("Ошибка", f"{title} не выбран!")
        return None
    return file

def start_upload():
    """Процесс загрузки видео."""
    video_directory = select_directory("Выберите папку с видео")
    if not video_directory:
        return

    token_directory = select_directory("Выберите папку с токенами")
    if not token_directory:
        return

    task_file = select_file("Выберите JSON-файл задач", [("JSON Files", "*.json")])
    if not task_file:
        return

    try:
        upload_videos_from_tasks(task_file, video_directory, token_directory)
        messagebox.showinfo("Успех", "Загрузка видео завершена!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

def start_authorization():
    """Процесс авторизации каналов."""
    config_file = select_file("Выберите файл конфигурации JSON", [("JSON Files", "*.json")])
    if not config_file:
        return

    token_directory = select_directory("Выберите папку для хранения токенов")
    if not token_directory:
        return

    try:
        process_channels(config_file, token_directory)
        messagebox.showinfo("Успех", "Авторизация каналов завершена!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

def configure_proxy():
    """Настройка прокси для каналов."""
    config_file = select_file("Выберите JSON-файл конфигурации", [("JSON Files", "*.json")])
    if not config_file:
        return

    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = json.load(file)

        for channel in config:
            channel_name = channel.get("channel_name")
            proxy = channel.get("proxy", "")

            new_proxy = simpledialog.askstring(
                "Настройка прокси",
                f"Введите прокси для канала {channel_name} (текущий: {proxy}):",
            )

            if new_proxy is not None:
                channel["proxy"] = new_proxy

        with open(config_file, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4, ensure_ascii=False)

        messagebox.showinfo("Успех", "Прокси для каналов обновлены!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

def create_authenticated_service_with_proxy(credentials, proxy_url):
    """Создание службы с использованием прокси."""
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }
    session = requests.Session()
    session.proxies.update(proxies)
    from googleapiclient.discovery import build
    from googleapiclient.http import HttpRequest
    from google.auth.transport.requests import Request

    transport = Request(session=session)
    return build(
        "youtube", "v3", credentials=credentials, requestBuilder=lambda *args, **kwargs: HttpRequest(transport, *args, **kwargs)
    )

# Создание основного окна
root = tk.Tk()
root.title("YouTube Video Uploader")
root.geometry("500x400")  # Устанавливаем размеры окна
root.configure(bg="#f0f0f0")  # Фон окна

# Заголовок
label = tk.Label(root, text="Выберите действие:", font=("Arial", 16), bg="#f0f0f0", fg="#333")
label.pack(pady=20)

# Фрейм для кнопок
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=20)

# Кнопки действий
btn_authorize = tk.Button(button_frame, text="Авторизовать каналы", command=start_authorization, width=30, bg="#4CAF50", fg="white", font=("Arial", 12), bd=0, padx=10, pady=5)
btn_authorize.grid(row=0, column=0, pady=10, padx=10)

btn_upload = tk.Button(button_frame, text="Загрузить видео", command=start_upload, width=30, bg="#2196F3", fg="white", font=("Arial", 12), bd=0, padx=10, pady=5)
btn_upload.grid(row=1, column=0, pady=10, padx=10)

# Запуск основного цикла
root.mainloop()
