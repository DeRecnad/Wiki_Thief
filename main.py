import tkinter as tk
import requests
from bs4 import BeautifulSoup
import pyperclip
import pyautogui
import sys

from Copy_Corvax import get_specific_text
from Input_Fandom import edit_and_save_text
from proxy_auth_data import username, password

def copy_and_update_links():
    link1 = f'https://station14.ru/index.php?title={entry1.get()}&action=edit'
    link2 = f'https://ss14andromeda13.fandom.com/ru/wiki/{entry2.get()}?veaction=editsource'
    filename = 'filename.txt'

    # Получаем текст с первой Вики-страницы


    print("Получаем текст")
    get_specific_text(link1)
    print("Текст получен")


    # Обновляем текст на второй Вики-странице
    print("Начинаем вводить текст")
    edit_and_save_text(link2, filename, username, password)
    print("Ввод окончен")

    # Копируем ссылки в буфер обмена
    pyperclip.copy(f"Link 1: {link1}\nLink 2: {link2}")

def print_to_output(message):
    # Записываем сообщение в область вывода
    output_area.configure(state="normal")
    output_area.insert(tk.END, message + "\n")
    output_area.configure(state="disabled")

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        # Вывод в текстовое поле
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, string)
        self.text_widget.configure(state="disabled")

    def flush(self):
        pass


# Создаем основное окно
window = tk.Tk()
window.title("Копировать и обновить Вики-страницы")

# Устанавливаем размер окна
window.geometry("320x320")

# Устанавливаем положение окна в центре экрана
window.wm_geometry('320x320+100+100')

# Создаем текстовые поля
entry1 = tk.Entry(window, width=30)
entry2 = tk.Entry(window, width=30)

# Создаем кнопку
button_copy_and_update = tk.Button(window, text="Копировать и обновить",
                                   command=lambda: copy_and_update_links())

# Размещаем элементы на окне
entry1.pack(pady=10)
entry2.pack(pady=10)
button_copy_and_update.pack(pady=10)

# Создаем область вывода
output_area = tk.Text(window, height=10, width=50)
output_area.pack(side="bottom", fill="x")
output_area.configure(state="disabled")

# Запускаем главный цикл
window.mainloop()
