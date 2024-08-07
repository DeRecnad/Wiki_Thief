def determine_wiki(url):
    """
    Заменяет значение параметра title на '***' в URL.

    :param url: Исходный URL
    :return: URL с параметром title замененным на '***'
    """
    # Разбираем URL
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Заменяем значение параметра title
    query_params['title'] = ['***']

    # Формируем новый URL с обновленными параметрами
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))

    return new_url


from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def create_template_url(template_phrase, empty_url):
    """
    Заменяет '***' в URL на заданную фразу.

    :param template_phrase: Фраза для замены
    :param empty_url: URL с '***' в качестве значения параметра title
    :return: Новый URL с замененной фразой
    """
    # Разбираем URL
    parsed_url = urlparse(empty_url)
    query_params = parse_qs(parsed_url.query)

    # Заменяем '***' на template_phrase
    query_params['title'] = [template_phrase]

    # Формируем новый URL с обновленными параметрами
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))

    return new_url


# Пример 1
link1 = "https://wiki14.ss220.club/index.php?title=%D0%A0%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D1%81%D1%82%D0%B2%D0%BE_%D0%BF%D0%BE_%D0%B2%D0%B7%D0%BB%D0%BE%D0%BC%D1%83&action=edit"
link2 = "http://aavikko.di9.ru/index.php?title=%D0%A0%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D1%81%D1%82%D0%B2%D0%BE_%D0%BF%D0%BE_%D0%B2%D0%B7%D0%BB%D0%BE%D0%BC%D1%83&action=edit"
phrase = "Шаблон:Frame"

link1_empt = determine_wiki(link1)
link2_empt = determine_wiki(link2)

print(f'link1 (пустой): {link1_empt}')
print(f'link2 (пустой): {link2_empt}')

new_link1 = create_template_url(phrase, link1_empt)
new_link2 = create_template_url(phrase, link2_empt)

print(f'Новая ссылка 1: {new_link1}')
print(f'Новая ссылка 2: {new_link2}')

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse



