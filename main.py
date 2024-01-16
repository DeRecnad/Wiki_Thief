import tkinter as tk
from tkinter import ttk
from Copy_Corvax import get_specific_text
from Input_Fandom import edit_and_save_text
from proxy_auth_data import username, password
import pyperclip
import requests


def copy_and_update_links(entry1_value, entry2_value, use_single_entry):
    if use_single_entry:
        # Используем только entry1 для создания ссылки
        link1 = f'https://station14.ru/index.php?title={entry1_value}&action=edit'
        link2 = f'https://ss14andromeda13.fandom.com/ru/wiki/{entry1_value}?veaction=editsource'
    else:
        # Используем entry1 и entry2 для создания ссылки
        link1 = f'https://station14.ru/index.php?title={entry1_value}&action=edit'
        link2 = f'https://ss14andromeda13.fandom.com/ru/wiki/{entry2_value}?veaction=editsource'
        # Дополнительная логика для обработки ссылок

    filename = 'filename.txt'
    print("Получаем текст")
    get_specific_text(link1)
    print("Текст получен")

    # Обновляем текст на второй Вики-странице
    print("Начинаем вводить текст")
    edit_and_save_text(link2, filename, username, password)
    print("Ввод окончен")

    # Копируем ссылки в буфер обмена
    pyperclip.copy(f"Link 1: {link1}\nLink 2: {link2}")


def toggle_entry_fields(entry2_main_menu, settings_vars):
    # Включаем или выключаем поле в зависимости от состояния флажка
    state = tk.NORMAL if settings_vars['use_single_entry'].get() else tk.DISABLED
    entry2_main_menu.config(state=state)


def create_main_menu_tab(tab_control, settings_vars):
    main_menu_tab = ttk.Frame(tab_control)
    tab_control.add(main_menu_tab, text='Главное меню')

    entry1_main_menu = tk.Entry(main_menu_tab, width=30)
    entry1_main_menu.pack(pady=10)

    entry2_main_menu = tk.Entry(main_menu_tab, width=30, state=tk.DISABLED)
    entry2_main_menu.pack(pady=10)

    settings_vars['use_single_entry'].trace_add('write',
                                                lambda *args: toggle_entry_fields(entry2_main_menu, settings_vars))

    button_copy_and_update_main_menu = tk.Button(main_menu_tab, text="Копировать и обновить",
                                                 command=lambda: copy_and_update_links(entry1_main_menu.get(),
                                                                                       entry2_main_menu.get(),
                                                                                       not settings_vars[
                                                                                           'use_single_entry'].get()))
    button_copy_and_update_main_menu.pack(pady=10)


def create_settings_tab(tab_control, settings_vars):
    settings_tab = ttk.Frame(tab_control)
    tab_control.add(settings_tab, text='Настройки')

    # Добавляем флажок (Checkbutton) для выбора
    check_button = tk.Checkbutton(settings_tab, text="Использовать оба поля для ссылки",
                                  variable=settings_vars['use_single_entry'])
    check_button.pack(pady=10, side=tk.LEFT, anchor=tk.NW)


def main():
    window = tk.Tk()
    window.title("Копировать и обновить Вики-страницы")
    window.geometry("320x320")

    settings_vars = {
        'use_single_entry': tk.BooleanVar(),
        # Добавьте другие переменные по мере необходимости
    }

    tab_control = ttk.Notebook(window)

    create_main_menu_tab(tab_control, settings_vars)
    create_settings_tab(tab_control, settings_vars)

    tab_control.pack(expand=1, fill="both")
    window.mainloop()


if __name__ == "__main__":
    main()
