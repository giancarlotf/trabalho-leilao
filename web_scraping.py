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
get_XPath =  """
            function getXPath(element) {
                if (element.id)
                    return '//*[@id="' + element.id + '"]';

                if (element.className)
                    return '//' + element.tagName.toLowerCase() + '[contains(normalize-space(.), "' + element.textContent.trim() + '")]';

                return null;
            }

            return getXPath(arguments[0]);
            """

# Script JavaScript para buscar o conteúdo de um elemento a partir de um XPath
search_XPath =  """
                function searchXPath(path) {
                    const element = document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    return element ? element.textContent : null;
                }

                return searchXPath(arguments[0]);
                """

# Função de log que exibe mensagens com horário e nível (INFO, ERROR, etc.)
def log(level, text):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{level}]: {text}")
    return

# Valida se a URL fornecida é válida
def validate_url(url: str):
    if not url or url == ("http://", "https://"):
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
            EC.presence_of_element_located((By.XPATH, f'//*[self::span or self::div or self::p][contains(normalize-space(.), "{value}")]'))
        )
        # Busca elementos que contenham o valor informado
        elements = driver.find_elements(By.XPATH, f'//*[self::span or self::div or self::p][contains(normalize-space(.), "{value}")]')

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
        return driver.execute_script(search_XPath, xpath)

    except Exception as e:
        log("Search/ERROR", e)
        return None

# Salva o histórico de valores encontrados em um arquivo
def save_history(url, value):
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(f"history.txt", "a", encoding="utf-8") as file:
        file.write(f"{now}; URL: {url}; {value}\n")

    return

# Função principal que monitora um elemento na página e detecta alterações
def analise(url:str, driver_name:str, rep_time:float, delay:float, refresh:bool, value:str=None, manual_xpath:str=None):
    """
    Monitora um valor em uma página web e detecta alterações.

    Args:
        url (str): URL da página
        driver_name (str): navegador utilizado
        rep_time (float): tempo total de execução (minutos)
        delay (float): intervalo entre verificações (segundos)
        refresh (bool): opção para recaregar a página
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
    id = 0
    last_value = None
    # Marca o tempo inicial        
    start_time = time.perf_counter()

    try:
        # Loop de monitoramento por tempo determinado        
        while time.perf_counter() - start_time < rep_time*60:
            # Atualiza a página se necessário        
            if refresh:
                driver.refresh()

            log("INFO", f"Execução [{id+1}]")
            # Obtém o valor atual do elemento        
            current_value = search(driver, xpath)

            if current_value is None:
                log("ERROR", "Elemento não encontrado")
                time.sleep(delay)
                continue

            current_value = current_value.strip()
            log("INFO", f"Atual: {current_value}")
            log("INFO", f"Último: {last_value}")

            # Primeira execução (salva valor inicial)        
            if last_value is None:
                save_history(url, current_value)
                log("INFO", "Valor salvo")
            # Detecta mudança de valor            
            elif current_value != last_value:
                message = f"""
                            Valor antigo: {last_value}
                            Valor novo: {current_value}
                            Data: {datetime.now()}
                            """

                # Futuro envio de notificação (ex: e-mail)        
                #enviar_email(email, title, message)
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
