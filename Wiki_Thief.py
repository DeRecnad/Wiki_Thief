import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading


class SettingsVars:
    def __init__(self):
        self.use_single_entry = tk.IntVar(value=1)
        self.use_templates = tk.IntVar(value=1)


def toggle_entry_fields(entry2_main_menu, settings_vars):
    state = tk.NORMAL if settings_vars.use_single_entry.get() else tk.DISABLED
    entry2_main_menu.config(state=state)


def create_main_menu_tab(tab_control, settings_vars):
    main_menu_tab = ttk.Frame(tab_control)
    tab_control.add(main_menu_tab, text='Главное меню')

    entry1_main_menu = tk.Entry(main_menu_tab, width=30)
    entry1_main_menu.pack(pady=10)

    entry2_main_menu = tk.Entry(main_menu_tab, width=30, state=tk.NORMAL)
    entry2_main_menu.pack(pady=10)

    settings_vars.use_single_entry.trace_add('write',
                                             lambda *args: toggle_entry_fields(entry2_main_menu, settings_vars))

    button_copy_and_update_main_menu = tk.Button(main_menu_tab, text="Копировать и обновить",
                                                 command=lambda: start_copy_and_update(entry1_main_menu.get(),
                                                                                       entry2_main_menu.get(),
                                                                                       settings_vars,
                                                                                       button_copy_and_update_main_menu))
    button_copy_and_update_main_menu.pack(pady=10)


def start_copy_and_update(link1, link2, settings_vars, button):
    button.config(state=tk.DISABLED)  # Блокируем кнопку

    # Вспомогательная функция для запуска в потоке
    def run_task():
        check_and_process_links(link1, link2, settings_vars)  # Запускаем обработку
        button.config(state=tk.NORMAL)  # Разблокируем кнопку после завершения

    # Запускаем новый поток для выполнения функции
    threading.Thread(target=run_task).start()



def update_chromedriver():
    try:
        # Устанавливаем ChromeDriver с помощью webdriver-manager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        # Закрываем драйвер после установки
        driver.quit()

        messagebox.showinfo("Успех", "ChromeDriver успешно обновлён!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось обновить ChromeDriver: {e}")


def create_settings_tab(tab_control, settings_vars):
    settings_tab = ttk.Frame(tab_control)
    tab_control.add(settings_tab, text='Настройки')

    check_button1 = tk.Checkbutton(settings_tab, text="Использовать оба поля для ссылки",
                                   variable=settings_vars.use_single_entry)
    check_button1.place(x=0, y=0)

    check_button2 = tk.Checkbutton(settings_tab, text="Использовать шаблоны",
                                   variable=settings_vars.use_templates)
    check_button2.place(x=0, y=25)

    # Кнопка для обновления ChromeDriver
    button_update_chromedriver = tk.Button(settings_tab, text="Обновить ChromeDriver",
                                           command=update_chromedriver)
    button_update_chromedriver.place(x=0, y=50)


def main():
    window = tk.Tk()
    window.title("Копировать и обновить Вики-страницы")
    window.geometry("320x320")

    settings_vars = SettingsVars()

    tab_control = ttk.Notebook(window)
    create_main_menu_tab(tab_control, settings_vars)
    create_settings_tab(tab_control, settings_vars)

    tab_control.pack(expand=1, fill="both")
    window.mainloop()


if __name__ == "__main__":
    from main import check_and_process_links  # Импортируем функцию здесь
    main()
