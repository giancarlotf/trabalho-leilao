"""
Módulo de monitoramento de elementos web usando Selenium.

Este script acessa uma página, identifica um elemento 
e monitora mudanças no seu conteúdo ao longo do tempo. Caso haja alteração, um e-mail
é enviado e o histórico é registrado.

Dependências:
- selenium
- webdriver_manager
- módulo interno: send_email
"""

from src.send_gmail import send_email
from datetime import datetime
import time

from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


# =========================
# SCRIPT JS PARA GERAR XPATH
# =========================
get_XPath = """
const getXPath = (element) => {
    if (element.id) {
        return //*[@id="${element.id}"]
    }

    const parts = []

    while (element && element.nodeType === 1) {
        let tag = element.tagName.toLowerCase()

        if (element.className) {
            const classes = element.className.trim().split(/\\s+/)
            const classCondition = classes.map(c => contains(@class, "${c}")).join(" and ")
            parts.unshift(${tag}[${classCondition}])
            break
        }

        let index = 1
        let sibling = element

        while (sibling.previousElementSibling) {
            sibling = sibling.previousElementSibling
            if (sibling.tagName === element.tagName) {
                index++
            }
        }

        parts.unshift(${tag}[${index}])
        element = element.parentElement
    }

    return '//' + parts.join('/')
}

return getXPath(arguments[0]);
"""


# =========================
# UTILITÁRIOS
# =========================
def log(level: str, text: str):
    """
    Registra mensagens no console e em arquivo.

    Args:
        level (str): nível do log (INFO, ERROR, DEBUG, etc.)
        text (str): mensagem a ser exibida
    """
    now = datetime.now().strftime("%H:%M:%S")
    log_text = f"[{now}] [{level}]: {text}"

    print(log_text)

    with open("log.txt", "a", encoding="utf-8") as file:
        file.write(f"{log_text}\n")


def validate_url(url: str):
    """
    Valida se a URL fornecida é válida.

    Args:
        url (str): URL a ser validada

    Returns:
        int | None: retorna 1 se inválida, None se válida
    """
    if not url or url in ("http://", "https://"):
        log("URL/ERROR", "Informe uma URL válida")
        return 1

    if not url.startswith("http"):
        log("URL/ERROR", "A URL deve começar com http ou https")
        return 1

    return None


# =========================
# DRIVER
# =========================
def set_driver(driver_name: str):
    """
    Inicializa um navegador em modo headless.

    Args:
        driver_name (str): 'chrome', 'firefox' ou 'edge'

    Returns:
        webdriver instance ou None em caso de erro
    """
    services = {
        "chrome": (webdriver.chrome.service.Service, ChromeDriverManager, webdriver.Chrome),
        "edge": (webdriver.edge.service.Service, EdgeChromiumDriverManager, webdriver.Edge),
        "firefox": (webdriver.firefox.service.Service, GeckoDriverManager, webdriver.Firefox)
    }

    try:
        service_class, driver_manager, driver_class = services[driver_name]
        service = service_class(driver_manager().install())

        # Configuração por navegador
        if driver_name == "chrome":
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")

        elif driver_name == "firefox":
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")

        elif driver_name == "edge":
            options = webdriver.EdgeOptions()
            options.add_argument("--headless=new")

        return driver_class(service=service, options=options)

    except Exception as e:
        log("Driver/ERROR", e)
        return None


# =========================
# XPATH E BUSCA
# =========================
def find_xpath(value: str, driver):
    """
    Encontra automaticamente um XPath baseado em texto visível.

    Args:
        value (str): texto a ser buscado
        driver: instância do webdriver

    Returns:
        str | None: XPath encontrado ou None
    """
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f'///text()[contains(., "{value}")]/parent::')
            )
        )

        elements = driver.find_elements(
            By.XPATH, f'///text()[contains(., "{value}")]/parent::'
        )

        if not elements:
            return None

        if len(elements) > 1:
            log("WARN", "Múltiplos elementos encontrados")

        return driver.execute_script(get_XPath, elements[0])

    except Exception as e:
        log("XPath/ERROR", e)
        return None


def search(driver, xpath: str):
    """
    Busca o texto de um elemento via XPath.

    Args:
        driver: webdriver
        xpath (str): XPath do elemento

    Returns:
        str | None: texto do elemento ou None
    """
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

        element = driver.find_element(By.XPATH, xpath)
        return element.text

    except Exception as e:
        log("Search/ERROR", e)
        return None


# =========================
# HISTÓRICO
# =========================
def save_history(url: str, value: str):
    """
    Salva o histórico de valores monitorados.

    Args:
        url (str): URL monitorada
        value (str): valor capturado
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("history.txt", "a", encoding="utf-8") as file:
        file.write(f"{now}; URL: {url}; Valor: {value}\n")


# =========================
# FUNÇÃO PRINCIPAL
# =========================
def analise(
    url: str,
    driver_name: str,
    rep_time: float,
    delay: float,
    refresh: bool,
    email: str,
    title: str,
    value: str = None,
    manual_xpath: str = None
):
    """
    Monitora um elemento em uma página web e detecta alterações.

    Fluxo:
    1. Abre o navegador
    2. Define o XPath (manual ou automático)
    3. Monitora o valor ao longo do tempo
    4. Envia alerta por e-mail em caso de mudança

    Args:
        url (str): URL da página
        driver_name (str): navegador ('chrome', 'firefox', 'edge')
        rep_time (float): tempo total de execução em minutos
        delay (float): intervalo entre verificações (segundos)
        refresh (bool): recarregar página a cada ciclo
        email (str): destinatário do alerta
        title (str): título do monitoramento
        value (str, opcional): texto base para encontrar elemento
        manual_xpath (str, opcional): XPath fornecido manualmente
    """

    driver = set_driver(driver_name)

    if not driver:
        log("ERROR", "Falha ao iniciar driver")
        return

    driver.get(url)

    # Define XPath
    if manual_xpath:
        xpath = manual_xpath
    else:
        xpath = find_xpath(value, driver)

        if not xpath:
            log("ERROR", "XPath não encontrado")
            driver.quit()
            return

    log("INFO", "Iniciando análise...")

    run_id = 0
    last_value = None
    start_time = time.perf_counter()

    try:
        while time.perf_counter() - start_time < rep_time * 60:

            if refresh:
                driver.refresh()

            log("INFO", f"Execução [{run_id}]")
            run_id += 1

            current_value = search(driver, xpath)

            if current_value is None:
                log("ERROR", "Elemento não encontrado")
                time.sleep(delay)
                continue

            current_value = current_value.strip()

            # Primeira leitura
            if last_value is None:
                last_value = current_value
                save_history(url, current_value)
                time.sleep(delay)
                continue

            # Detecta mudança
            if current_value != last_value:
                message = f"""
Valor atual: {current_value}
Valor antigo: {last_value}
Data: {datetime.now()}
"""
                send_email(driver, email, title, message)
                save_history(url, current_value)
                log("INFO", "Mudança detectada e registrada")

            else:
                log("INFO", "Sem mudanças")

            last_value = current_value
            time.sleep(delay)

    finally:
        driver.quit()
