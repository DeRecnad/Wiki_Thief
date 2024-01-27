import tkinter as tk
from tkinter import ttk
from logic import check_links

class SettingsVars:
    def __init__(self):
        self.use_single_entry = tk.IntVar()
        self.use_templates = tk.IntVar()
        # Добавьте другие переменные по мере необходимости

def toggle_entry_fields(entry2_main_menu, settings_vars):
    # Включаем или выключаем поле в зависимости от состояния флажков
    state = tk.NORMAL if settings_vars.use_single_entry.get() else tk.DISABLED
    entry2_main_menu.config(state=state)

def create_main_menu_tab(tab_control, settings_vars):
    main_menu_tab = ttk.Frame(tab_control)
    tab_control.add(main_menu_tab, text='Главное меню')

    entry1_main_menu = tk.Entry(main_menu_tab, width=30)
    entry1_main_menu.pack(pady=10)

    entry2_main_menu = tk.Entry(main_menu_tab, width=30, state=tk.DISABLED)
    entry2_main_menu.pack(pady=10)

    settings_vars.use_single_entry.trace_add('write',
                                            lambda *args: toggle_entry_fields(entry2_main_menu, settings_vars))

    settings_vars.use_templates.trace_add('write',
                                          lambda *args: None)

    button_copy_and_update_main_menu = tk.Button(main_menu_tab, text="Копировать и обновить",
                                                 command=lambda: check_links(entry1_main_menu.get(),
                                                                             entry2_main_menu.get(),
                                                                             settings_vars))
    button_copy_and_update_main_menu.pack(pady=10)

def create_settings_tab(tab_control, settings_vars):
    settings_tab = ttk.Frame(tab_control)
    tab_control.add(settings_tab, text='Настройки')

    check_button1 = tk.Checkbutton(settings_tab, text="Использовать оба поля для ссылки",
                                   variable=settings_vars.use_single_entry)
    check_button1.place(x=0, y=0)

    check_button2 = tk.Checkbutton(settings_tab, text="Использовать шаблоны",
                                   variable=settings_vars.use_templates)
    check_button2.place(x=0, y=25)

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
    main()
