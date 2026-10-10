import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Данные для аккаунта (потом можно вынести в переменные)
FIRST_NAME = "Ivan"
LAST_NAME = "Petrov"
USERNAME = "ivanpetrov" + str(int(time.time()))  # уникальный логин
PASSWORD = "SuperPass123!"

print("Бот запущен...")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

service = Service(executable_path='/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

try:
    driver.get("https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp")
    print("Страница регистрации открыта")

    # Имя
    first_name = wait.until(EC.presence_of_element_located((By.NAME, "firstName")))
    first_name.send_keys(FIRST_NAME)
    print("Имя введено")

    # Фамилия
    last_name = driver.find_element(By.NAME, "lastName")
    last_name.send_keys(LAST_NAME)
    print("Фамилия введена")

    # Кнопка «Далее»
    next_btn = driver.find_element(By.XPATH, "//span[text()='Далее' or text()='Next']")
    next_btn.click()
    time.sleep(2)

    # Логин (username)
    username = wait.until(EC.presence_of_element_located((By.NAME, "Username")))
    username.send_keys(USERNAME)
    print("Логин введён")

    # Пароль
    password = driver.find_element(By.NAME, "Passwd")
    password.send_keys(PASSWORD)
    confirm = driver.find_element(By.NAME, "ConfirmPasswd")
    confirm.send_keys(PASSWORD)
    print("Пароль введён")

    # Кнопка «Далее»
    next_btn2 = driver.find_element(By.XPATH, "//span[text()='Далее' or text()='Next']")
    next_btn2.click()
    time.sleep(3)

    # Пытаемся нажать «Пропустить» (Skip) на экране телефона
    try:
        skip_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Пропустить') or contains(text(), 'Skip')]")
        skip_btn.click()
        print("Нажата кнопка 'Пропустить'")
    except:
        print("Кнопки 'Пропустить' нет — Google требует телефон")

    time.sleep(5)
    print("Текущий URL:", driver.current_url)

except Exception as e:
    print("Ошибка:", e)

finally:
    driver.quit()
    print("Бот завершил работу.")