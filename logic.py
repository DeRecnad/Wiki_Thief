from Copy_Corvax import get_specific_text, write_data_to_file
from Input_Fandom import edit_and_save_text
from proxy_auth_data import username, password


def check_links(entry1_value, entry2_value, use_single_entry):
    # Проверяем, введено ли название страницы в первом окне
    if not entry1_value.startswith('https://'):
        # Если название страницы, то сохраняем его
        entry1_value = entry1_value.strip()
    else:
        entry1_value = entry1_value.replace('https://station14.ru/index.php?title=', '')
        entry1_value = entry1_value.replace('&action=edit', '')
    if not use_single_entry:
        # Проверяем, введено ли название страницы во втором окне
        if not entry2_value.startswith('https://'):
            # Если название страницы, то сохраняем его
            entry2_value = entry2_value.strip()
        else:
            entry2_value = entry2_value.replace('https://ss14andromeda13.fandom.com/ru/wiki/', '')
            entry2_value = entry2_value.replace('?action=edit', '')

    link1, link2 = rename_links(entry1_value, entry2_value, use_single_entry)
    check_count_links(link1, link2, use_single_entry)


def get_and_remove_last_link(file_path='templates_used.txt'):
    try:
        # Читаем все строки из файла
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Проверяем, есть ли ссылки в файле
        if lines:
            # Извлекаем последнюю ссылку
            last_link = lines[-1].strip()

            # Перезаписываем файл без последней строки
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
    if use_single_entry:
        # Используем только entry1 для создания ссылки
        link1 = f'https://station14.ru/index.php?title={entry1_value}&action=edit'
        link2 = f'https://ss14andromeda13.fandom.com/ru/wiki/{entry1_value}?action=edit'
    else:
        # Используем entry1 и entry2 для создания ссылки
        link1 = f'https://station14.ru/index.php?title={entry1_value}&action=edit'
        link2 = f'https://ss14andromeda13.fandom.com/ru/wiki/{entry2_value}?action=edit'
        # Дополнительная логика для обработки ссылок
    return link1, link2


def process_links(link1, link2):
    filename = 'filename.txt'
    print("Получаем текст")
    get_specific_text(link1)
    print("Текст получен")

    # Обновляем текст на второй Вики-странице
    print("Начинаем вводить текст")
    edit_and_save_text(link2, filename, username, password)
    print("Ввод окончен")

def copy_and_update_links(link1, link2):
    process_links(link1, link2)

def check_count_links(link1, link2, use_single_entry):
    count_templates_links = write_data_to_file(link1)

    if count_templates_links == 'E520':
        print('Дружок, либо беда с инетом, либо корвух дудосят')
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
