# logic.py

from Copy_Corvax import get_specific_text, find_template_links
from Input_Fandom import FandomEditor
from proxy_auth_data import username, password

instance = FandomEditor()

def check_links(entry1_value, entry2_value, settings_vars):
    use_single_entry = settings_vars.use_single_entry.get()
    transfer_descendants = settings_vars.transfer_descendants.get()

    if not entry1_value.startswith('https://'):
        entry1_value = entry1_value.strip()
    else:
        entry1_value = entry1_value.replace('https://station14.ru/edit/', '')
        entry1_value = entry1_value.replace('', '')
    if not use_single_entry:
        if not entry2_value.startswith('https://'):
            entry2_value = entry2_value.strip()
        else:
            entry2_value = entry2_value.replace('https://ss14andromeda13.fandom.com/ru/wiki/', '')
            entry2_value = entry2_value.replace('?action=edit', '')

    print(f"value1: {entry1_value}")
    print(f"value2: {entry2_value}")
    link1, link2 = rename_links(entry1_value, entry2_value, use_single_entry)
    print(f"link1: {link1}")
    print(f"link2: {link2}")
    check_count_links(link1, link2, use_single_entry, transfer_descendants)

def get_and_remove_last_link(file_path='templates_used.txt'):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if lines:
            last_link = lines[-1].strip()
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines[:-1])
            return last_link
        else:
            print(f'Файл {file_path} пуст. Нет ссылок для извлечения.')
            return None
    except Exception as e:
        print(f'Произошла ошибка при обработке файла: {e}')
        return None

def rename_links(entry1_value, entry2_value, use_single_entry):
    if not use_single_entry:
        link1 = f'https://station14.ru/edit/{entry1_value}'
        link2 = f'https://ss14andromeda13.fandom.com/ru/wiki/{entry1_value}?action=edit'
    else:
        link1 = f'https://station14.ru/edit/{entry1_value}'
        link2 = f'https://ss14andromeda13.fandom.com/ru/wiki/{entry2_value}?action=edit'
    return link1, link2

def process_links(link1, link2):
    filename = 'filename.txt'
    print("Получаем текст")
    get_specific_text(link1)
    print("Текст получен")

    print("Начинаем вводить текст")
    instance.edit_and_save_text(link2, filename, username, password)
    print("Ввод окончен")

def copy_and_update_links(link1, link2):
    process_links(link1, link2)

def check_count_links(link1, link2, use_single_entry, transfer_descendants):
    if transfer_descendants:
        count_templates_links = find_template_links(link1)
    else:
        count_templates_links = 0

    if count_templates_links == 'E520':
        print('Ошибка с получением данных или проблема с сайтом.')
    elif count_templates_links > 0:
        main1_link = link1
        main2_link = link2
        while count_templates_links != 0:
            link2 = get_and_remove_last_link()
            link1 = link2
            link1, link2 = rename_links(link1, link2, use_single_entry)
            process_links(link1, link2)
            count_templates_links -= 1
        process_links(main1_link, main2_link)
    else:
        copy_and_update_links(link1, link2)
