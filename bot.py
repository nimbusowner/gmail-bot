import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# Данные для аккаунта
FIRST_NAME = "Ivan"
LAST_NAME = "Petrov"
USERNAME = "ivanpetrov" + str(int(time.time()))
PASSWORD = "SuperPass123!"

print("Бот запущен...")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--lang=en-US")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

service = Service(executable_path='/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 25)


def save_debug(name):
    try:
        with open(name, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Сохранён " + name)
    except Exception as e:
        print("Не удалось сохранить " + name + ": " + str(e))


def click_next():
    """Находит и нажимает кнопку 'Next'."""
    time.sleep(2)
    next_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[.//span[contains(text(), 'Next') or contains(text(), 'Далее')]]")
    ))
    next_btn.click()
    print("Кнопка 'Next' нажата")
    time.sleep(3)


try:
    driver.get("https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp")
    print("Страница регистрации открыта")
    time.sleep(3)

    # Шаг 1: Имя и Фамилия
    first_name = wait.until(EC.presence_of_element_located((By.NAME, "firstName")))
    first_name.send_keys(FIRST_NAME)
    print("Имя введено")

    last_name = driver.find_element(By.NAME, "lastName")
    last_name.send_keys(LAST_NAME)
    print("Фамилия введена")

    save_debug("debug_1_name.html")
    click_next()

    # Шаг 2: Дата рождения и Пол (Экран "Basic information")
    print("Заполняем дату рождения и пол...")
    time.sleep(3)
    save_debug("debug_2_basic.html")

    # Выбираем месяц
    month_select = wait.until(EC.presence_of_element_located((By.ID, "month")))
    Select(month_select).select_by_value("5")  # Май (значения от 1 до 12)
    print("Месяц выбран")

    # Вводим день
    day_input = driver.find_element(By.ID, "day")
    day_input.send_keys("15")
    print("День введён")

    # Вводим год
    year_input = driver.find_element(By.ID, "year")
    year_input.send_keys("1990")
    print("Год введён")

    # Выбираем пол
    gender_select = driver.find_element(By.ID, "gender")
    Select(gender_select).select_by_value("1")  # 1 = Male, 2 = Female
    print("Пол выбран")

    click_next()

    # Шаг 3: Логин (Username)
    print("Пытаемся ввести логин...")
    time.sleep(3)
    save_debug("debug_3_username.html")

    username = wait.until(EC.presence_of_element_located((By.NAME, "Username")))
    username.send_keys(USERNAME)
    print("Логин введён")

    # Шаг 4: Пароль
    password = driver.find_element(By.NAME, "Passwd")
    password.send_keys(PASSWORD)
    confirm = driver.find_element(By.NAME, "ConfirmPasswd")
    confirm.send_keys(PASSWORD)
    print("Пароль введён")

    click_next()

    # Шаг 5: Пропуск телефона
    time.sleep(4)
    save_debug("debug_4_phone.html")
    try:
        skip_btn = driver.find_element(By.XPATH, "//button[contains(., 'Skip') or contains(., 'Пропустить')]")
        skip_btn.click()
        print("Нажата кнопка 'Пропустить'")
    except Exception:
        print("Кнопки 'Пропустить' нет — Google требует телефон")

    time.sleep(3)
    print("Финальный URL: " + driver.current_url)
    save_debug("debug_final.html")

except Exception as e:
    print("Ошибка: " + str(e)[:500])
    save_debug("debug_error.html")
    try:
        driver.save_screenshot("error.png")
        print("Скриншот ошибки сохранён")
    except Exception:
        pass

finally:
    driver.quit()
    print("Бот завершил работу.")