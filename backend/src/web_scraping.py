from src.send_gmail import send_email

from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Script JavaScript executado dentro do navegador para gerar automaticamente um XPath
get_XPath = """
            const getXPath = (element) => {
                if (element.id) {
                    return `//*[@id="${element.id}"]`
                }

                const parts = []

                while (element && element.nodeType === 1) {
                    let tag = element.tagName.toLowerCase()

                    if (element.className) {
                        const classes = element.className.trim().split(/\s+/)
                        const classCondition = classes.map(c => `contains(@class, "${c}")`).join(" and ")
                        parts.unshift(`${tag}[${classCondition}]`)
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

                    parts.unshift(`${tag}[${index}]`)
                    element = element.parentElement
                }

                return '//' + parts.join('/')
            }

            return getXPath(arguments[0]);
            """

# Função de log que exibe mensagens com horário e nível (INFO, ERROR, etc.)
def log(level, text):
    now = datetime.now().strftime("%H:%M:%S")
    log_text = f"[{now}] [{level}]: {text}"
    print(log_text)

    with open(f"log.txt", "a", encoding="utf-8") as file:
        file.write(log_text)

    return

# Valida se a URL fornecida é válida
def validate_url(url: str):
    if not url or url in ("http://", "https://"):
        log("URL/ERROR", "Informe uma URL válida")
        return 1
    if not url.startswith("http"):
        log("URL/ERROR", "A URL deve começar com http ou https")
        return 1

    return None

# Inicializa o navegador (Chrome, Edge ou Firefox) em modo headless
def set_driver(driver_name: str):
    services = {
        "chrome": (webdriver.chrome.service.Service, ChromeDriverManager, webdriver.Chrome),
        "edge": (webdriver.edge.service.Service, EdgeChromiumDriverManager, webdriver.Edge),
        "firefox": (webdriver.firefox.service.Service, GeckoDriverManager, webdriver.Firefox)
    }

    try: 
        # Seleciona o serviço, gerenciador e classe do driver
        service_class, driver_manager, driver_class = services[driver_name]
        service = service_class(driver_manager().install())

        # Configurações específicas para cada navegador
        if driver_name == "chrome":
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-blink-features=AutomationControlled")
        elif driver_name == "firefox":
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
        elif driver_name == "edge":
            options = webdriver.EdgeOptions()
            options.add_argument("--headless=new")
                    
        # Retorna o navegador configurado
        return driver_class(service=service, options=options)
    
    except Exception as e:
        log("Driver/ERROR", e)
        return

# Busca automaticamente um elemento com base em um valor de texto e gera um XPath
def find_xpath(value, driver):
    try:
        # Aguarda até que o elemento esteja presente na página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//*/text()[contains(., "{value}")]/parent::*'))
        )
        # Busca elementos que contenham o valor informado
        elements = driver.find_elements(By.XPATH, f'//*/text()[contains(., "{value}")]/parent::*')

        if not elements:
            return None
        # Caso encontre mais de um elemento, gera um aviso
        if len(elements) > 1:
            log("WARN", "Múltiplos elementos encontrados")

        # Executa o script JS para gerar o XPath do primeiro elemento encontrado        
        return driver.execute_script(get_XPath, elements[0])

    except Exception as e:
        log("XPath/ERROR", e)
        return None
                
# Busca o valor de um elemento utilizando XPath
def search(driver, xpath):
    try:
        # Aguarda o elemento aparecer        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        # Executa o script JS para obter o conteúdo do elemento        
        element = driver.find_element(By.XPATH, xpath)
        return element.text

    except Exception as e:
        log("Search/ERROR", e)
        return None

# Salva o histórico de valores encontrados em um arquivo
def save_history(url, value):
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(f"history.txt", "a", encoding="utf-8") as file:
        file.write(f"{now}; URL: {url}; Valor: {value}\n")

    return

# Função principal que monitora um elemento na página e detecta alterações
def analise(url:str, driver_name:str, rep_time:float, delay:float,
            refresh:bool, email:str, title:str, value:str=None, manual_xpath:str=None):
    """
    Monitora um valor em uma página web e detecta alterações.

    Args:
        url (str): URL da página
        driver_name (str): navegador utilizado
        rep_time (float): tempo total de execução (minutos)
        delay (float): intervalo entre verificações (segundos)
        refresh (bool): opção para recaregar a página
        email (str): email que receberá os valores
        title (str): nome do objeto buscado
        value (str): valor inicial a ser buscado
        manual_xpath (str): XPath a ser utilizado
    """

    # Inicializa o navegador        
    driver = set_driver(driver_name)

    if not driver:
        log("ERROR", "Falha ao iniciar driver")
        return

    log("DEBUG", f"Driver: {driver}")
    # Acessa a página        
    driver.get(url)
    # Define o XPath (manual ou automático)
    if manual_xpath:
        xpath = manual_xpath
    else:
        xpath = find_xpath(value, driver)

        if not xpath:
            log("ERROR", "XPath não encontrado")
            driver.quit()
            return

    log("DEBUG", f"XPath: {xpath}")
    log("INFO", "Iniciando análise...")
    run_id = 0
    last_value = None
    # Marca o tempo inicial        
    start_time = time.perf_counter()

    try:
        # Loop de monitoramento por tempo determinado        
        while time.perf_counter() - start_time < rep_time*60:
            # Atualiza a página se necessário        
            if refresh:
                driver.refresh()

            log("INFO", f"Execução [{run_id}]")
            run_id+=1
            # Obtém o valor atual do elemento        
            current_value = search(driver, xpath)

            if current_value is None:
                log("ERROR", "Elemento não encontrado")
                time.sleep(delay)
                continue

            current_value = current_value.strip()
            log("INFO", f"Valor atual: {current_value}")
            log("INFO", f"Valor antigo: {last_value}")

            # Primeira execução (salva valor inicial)        
            if last_value is None:
                last_value = current_value
                save_history(url, current_value)
                time.sleep(delay)
                continue
            # Detecta mudança de valor            
            elif current_value != last_value:
                message = f"""
                            Valor atual: {current_value}
                            Valor antigo: {last_value}
                            Data: {datetime.now()}
                            """       
                send_email(driver, email, title, message)
                save_history(url, current_value)
                log("INFO", "Novo valor salvo")
            else:
                log("INFO", "Sem mudanças no valor")

            # Atualiza o último valor        
            last_value = current_value
            # Aguarda antes da próxima leitura        
            time.sleep(delay)

    finally:
        # Garante que o navegador será fechado        
        driver.quit()
        return
