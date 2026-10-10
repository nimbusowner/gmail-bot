import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FIRST_NAMES = ["Ivan", "Petr", "Alex", "Dmitry", "Sergey", "Andrey", "Nikolay", "Maxim"]
LAST_NAMES = ["Petrov", "Ivanov", "Sidorov", "Smirnov", "Kuznetsov", "Popov", "Volkov", "Morozov"]


def generate_user_data():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    username = f"{first.lower()}{last.lower()}{random.randint(1000, 9999)}"
    password = f"Pass{random.randint(10000, 99999)}!"
    return first, last, username, password


def setup_driver():
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
    return driver


def save_debug(driver, name):
    try:
        with open(name, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception:
        pass


def click_next(wait):
    """Нажимает кнопку Next с несколькими попытками."""
    time.sleep(2)
    for xpath in [
        "//button[.//span[contains(text(), 'Next')]]",
        "//button[.//span[contains(text(), 'Далее')]]",
        "//button[contains(., 'Next')]",
        "//button[contains(., 'Далее')]",
    ]:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver_js_click(btn)
            time.sleep(3)
            return True
        except Exception:
            continue
    return False


def driver_js_click(element):
    """Кликает через JavaScript — надёжнее обычного клика."""
    from selenium.webdriver.remote.webelement import WebElement
    driver = element.parent
    driver.execute_script("arguments[0].click();", element)


def create_one_account(driver, first, last, username, password, index):
    wait = WebDriverWait(driver, 25)

    try:
        driver.get("https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp")
        time.sleep(3)

        # Имя и фамилия
        fn = wait.until(EC.presence_of_element_located((By.NAME, "firstName")))
        fn.send_keys(first)
        driver.find_element(By.NAME, "lastName").send_keys(last)
        print(f"  Имя/Фамилия: {first} {last}")
        if not click_next(wait):
            print("  !!! Не нашли кнопку Next (шаг 1) !!!")
            return None

        # Дата рождения
        time.sleep(3)
        month_field = wait.until(EC.element_to_be_clickable((By.ID, "month")))
        driver.execute_script("arguments[0].click();", month_field)
        time.sleep(1)
        month_opt = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-value='5']")))
        driver.execute_script("arguments[0].click();", month_opt)
        driver.find_element(By.ID, "day").send_keys("15")
        driver.find_element(By.ID, "year").send_keys("1990")
        print("  Дата рождения введена")

        # Пол
        gender_field = wait.until(EC.element_to_be_clickable((By.ID, "gender")))
        driver.execute_script("arguments[0].click();", gender_field)
        time.sleep(2)

        found = False
        for xpath in [
            "//li[@data-value='1']",
            "//div[@role='option'][@data-value='1']",
            "//li[contains(., 'Male')]",
            "//div[@role='option'][contains(., 'Male')]",
        ]:
            try:
                opt = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].click();", opt)
                print(f"  Пол выбран")
                found = True
                break
            except Exception:
                continue

        if not found:
            print("  !!! Не нашли опцию пола !!!")
            return None

        # Жмём Next после пола
        if not click_next(wait):
            print("  !!! Не нашли кнопку Next (шаг 2) !!!")
            save_debug(driver, f"debug_{index}_next_fail.html")
            return None
        print("  Шаг 2 пройден")

        # Логин
        time.sleep(3)
        print(f"  URL после пола: {driver.current_url}")

        try:
            un = wait.until(EC.presence_of_element_located((By.NAME, "Username")))
            un.send_keys(username)
            print(f"  Логин: {username}")
        except Exception:
            print("  !!! Google не показал поле Username (капча или бан) !!!")
            save_debug(driver, f"debug_{index}_username.html")
            return None

        # Пароль
        driver.find_element(By.NAME, "Passwd").send_keys(password)
        driver.find_element(By.NAME, "ConfirmPasswd").send_keys(password)
        print("  Пароль введён")
        if not click_next(wait):
            print("  !!! Не нашли кнопку Next (шаг 3) !!!")
            return None

        # Skip телефон
        time.sleep(5)
        save_debug(driver, f"debug_{index}_phone.html")
        print(f"  URL после пароля: {driver.current_url}")

        skipped = False
        for xpath in [
            "//button[contains(., 'Skip')]",
            "//button[contains(., 'Пропустить')]",
            "//button[.//span[contains(text(), 'Skip')]]",
            "//button[.//span[contains(text(), 'Пропустить')]]",
        ]:
            try:
                skip_btn = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].click();", skip_btn)
                print("  Нажата Skip")
                skipped = True
                time.sleep(3)
                break
            except Exception:
                continue

        if not skipped:
            print("  !!! Кнопки Skip нет — Google требует телефон !!!")
            return None

        time.sleep(3)
        if "myaccount.google.com" in driver.current_url:
            print(f"  ✅ АККАУНТ СОЗДАН: {username}@gmail.com : {password}")
            return {"email": f"{username}@gmail.com", "password": password}
        else:
            print(f"  ❌ Аккаунт не создан. URL: {driver.current_url}")
            return None

    except Exception as e:
        print(f"  Ошибка: {str(e)[:200]}")
        save_debug(driver, f"debug_{index}_error.html")
        return None


def main():
    COUNT = 5

    print("=" * 50)
    print(f"ЗАПУСК ЦИКЛА: {COUNT} аккаунтов (без SMS)")
    print("=" * 50)

    driver = setup_driver()
    created = []

    for i in range(COUNT):
        print(f"\n--- Попытка {i + 1}/{COUNT} ---")
        first, last, username, password = generate_user_data()
        result = create_one_account(driver, first, last, username, password, i + 1)
        if result:
            created.append(result)
        time.sleep(8)

    driver.quit()

    with open("accounts.txt", "w", encoding="utf-8") as f:
        for acc in created:
            f.write(f"{acc['email']}:{acc['password']}\n")

    print("\n" + "=" * 50)
    print(f"ИТОГО СОЗДАНО: {len(created)} из {COUNT}")
    print("=" * 50)


if __name__ == "__main__":
    main()