import time
import requests

def check_proxy(proxy_url, test_url="https://www.google.com", timeout=60):
    """
    Проверяет работоспособность прокси и измеряет время отклика.

    :param proxy_url: URL прокси-сервера в формате "http://user:password@host:port"
    :param test_url: URL, который будет запрашиваться для проверки прокси
    :param timeout: Таймаут для запроса, в секундах
    """
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    
    print(f"Проверяем прокси: {proxy_url}")
    start_time = time.time()

    try:
        # Выполняем GET-запрос через указанный прокси
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        elapsed_time = time.time() - start_time

        # Проверяем статус ответа
        if response.status_code == 200:
            print(f"Подключение успешно! Время отклика: {elapsed_time:.2f} сек.")
            print(f"Ваш IP через прокси: {response.headers.get('X-Forwarded-For', 'не определён')}")
        else:
            print(f"Прокси отвечает, но запрос завершился с ошибкой. Код ответа: {response.status_code}")
    except requests.exceptions.ProxyError:
        print("Ошибка: Прокси-сервер недоступен или данные авторизации неверны.")
    except requests.exceptions.ConnectTimeout:
        print("Ошибка: Истекло время ожидания подключения к прокси.")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка: {e}")

# Указанные данные прокси
proxy_url = "http://a7rnKw:vypf1W@194.32.251.253:8000"

# Запуск проверки
check_proxy(proxy_url)

