import requests
from bs4 import BeautifulSoup


def get_specific_text(url, output_filename='filename.txt'):
    # Отправляем GET-запрос
    response = requests.get(url)
    target_tag = 'textarea'
    target_class = 'mw-editfont-monospace'

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Используем BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим конкретный тег с указанным классом
        target_element = soup.find(target_tag, class_=target_class)

        # Получаем текст из найденного элемента
        if target_element:
            text_content = target_element.get_text()

            # Сохраняем текст в файл
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(text_content)

            print(f"Текст сохранен в файл: {output_filename}")
        else:
            print(f"Элемент с тегом '{target_tag}' и классом '{target_class}' не найден.")
    else:
        # Если запрос не успешен, выводим сообщение об ошибке
        print(f"Ошибка {response.status_code}: Невозможно получить содержимое страницы.")

# Пример использования
url = 'https://station14.ru/index.php?title=%D0%93%D0%98%D0%9E%D0%A0&action=edit'
