import tkinter as tk
from tkinter import filedialog, messagebox
from app.upload_multiple_videos import upload_videos_from_tasks
import os


def select_directory(title):
    """Функция для выбора папки с видео или токенами."""
    directory = filedialog.askdirectory(title=title)
    if not directory:
        messagebox.showwarning("Ошибка", f"Папка не выбрана!")
        return None
    return directory


def start_upload():
    # Выбираем папку с видео
    video_directory = select_directory("Выберите папку с видео")
    if not video_directory:
        return

    # Выбираем папку с токенами
    token_directory = select_directory("Выберите папку с токенами")
    if not token_directory:
        return
    
    task_file = filedialog.askopenfilename(
        title="Выберите JSON-файл задач",
        filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
    )
    if not task_file:
        messagebox.showwarning("Ошибка", "Файл задач не выбран!")
        return

    try:
        # Передаем пути к выбранным папкам в функцию загрузки
        upload_videos_from_tasks(task_file, video_directory, token_directory)
        messagebox.showinfo("Успех", "Загрузка видео завершена!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")


# Создание GUI
root = tk.Tk()
root.title("Загрузка видео на YouTube")

btn_upload = tk.Button(root, text="Выбрать папки и загрузить", command=start_upload)
btn_upload.pack(pady=20)

root.mainloop()
