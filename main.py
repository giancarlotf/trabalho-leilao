from datetime import datetime
import web_scraping as ws

def setup():
    nome = input("Nome: ")

    if len(nome) < 3 or not nome.replace(" ", "").isalpha():
        ws.log("User/ERROR", "Nome inválido")
        return

    url = input("URL: ")

    if ws.validate_url(url):
        return

    xpath = None
    manual_xpath = input("XPath manual? (S/n): ")

    if manual_xpath in ("n", "N"):
        value = input("Value: ")
    elif manual_xpath in ("s", "S"):
        tag = input("Tag: ")
        attribute = input("Attribute: ")
        value = input("Value: ")
        xpath = f"//{tag}[@{attribute}='{value}']"
    else:
        return

    driver_name = "chrome"
    rep_time = 1

    if not isinstance(rep_time, (int, float)):
        ws.log("User/ERROR", "Tempo de atuação inválido")
        return

    delay = 10

    if not isinstance(delay, (int, float)):
        ws.log("User/ERROR", "Delay inválido")
        return

    refresh = True

    ws.log("User/INFO", f"Usuário: {nome}")
    ws.log("User/INFO", f"URL: {url}")

    if xpath:
        ws.log("User/INFO", f"XPath: {xpath}")
    else:
        ws.log("User/INFO", f"Valor inicial: {value}")

    ws.log("User/INFO", f"Driver selecionado: {driver_name}")
    ws.log("User/INFO", f"Tempo de atuação: {rep_time}")
    ws.log("User/INFO", f"Intervalo entre leituras: {delay}")

    ws.analise(url, driver_name, rep_time, delay, refresh, value=None, manual_xpath=xpath)

while True:
    setup()
