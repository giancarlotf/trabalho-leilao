from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def send_email(driver, email, title, message):
    url = "https://mail.google.com/mail/u/0/#inbox?compose=new"
    driver.get(url)
    time.sleep(5)  # espera carregar

    try:
        # Campo "Para"
        to_field = driver.find_element(By.NAME, "to")
        to_field.send_keys(email)

        # Campo "Assunto"
        subject_field = driver.find_element(By.NAME, "subjectbox")
        subject_field.send_keys(title)

        # Corpo do email
        body = driver.find_element(By.XPATH, "//div[@aria-label='Corpo da mensagem']")
        body.send_keys(message)

        time.sleep(2)

        # Enviar
        body.send_keys(Keys.CONTROL, Keys.ENTER)

        print("Email enviado com sucesso")

    except Exception as e:
        print("Erro ao enviar email:", e)
