from backend.src.web_scraping import validate_url, set_driver, find_xpath, search, save_history, analise

import pytest
from unittest.mock import patch, MagicMock

def test_validate_url_valida():
    assert validate_url("https://google.com") is None

def test_validate_url_vazia():
    assert validate_url("") == 1

def test_validate_url_sem_http():
    assert validate_url("google.com") == 1


@patch("backend.src.web_scraping.webdriver.Chrome")
@patch("backend.src.web_scraping.ChromeDriverManager")
@patch("backend.src.web_scraping.webdriver.chrome.service.Service")
def test_set_driver_chrome(mock_service, mock_manager, mock_driver):
    mock_manager.return_value.install.return_value = "/fake/path"

    driver = set_driver("chrome")

    assert driver is not None
    mock_driver.assert_called_once()

def test_set_driver_invalido():
    driver = set_driver("safari")
    assert driver is None


@patch("backend.src.web_scraping.WebDriverWait")
def test_find_xpath_sucesso(mock_wait):
    mock_driver = MagicMock()

    mock_element = MagicMock()
    mock_driver.find_elements.return_value = [mock_element]
    mock_driver.execute_script.return_value = "//div[1]"

    xpath = find_xpath("teste", mock_driver)

    assert xpath == "//div[1]"


@patch("backend.src.web_scraping.WebDriverWait")
def test_find_xpath_nenhum(mock_wait):
    mock_driver = MagicMock()
    mock_driver.find_elements.return_value = []

    xpath = find_xpath("teste", mock_driver)

    assert xpath is None


@patch("backend.src.web_scraping.WebDriverWait")
def test_search_sucesso(mock_wait):
    mock_driver = MagicMock()
    mock_element = MagicMock()
    mock_element.text = "valor encontrado"
    mock_driver.find_element.return_value = mock_element
    result = search(mock_driver, "//div")

    assert result == "valor encontrado"


@patch("backend.src.web_scraping.WebDriverWait")
def test_search_erro(mock_wait):
    mock_driver = MagicMock()
    mock_driver.find_element.side_effect = Exception("erro")
    result = search(mock_driver, "//div")

    assert result is None

@patch("builtins.open")
def test_save_history(mock_open):
    save_history("http://teste.com", "123")
    mock_open.assert_called_once()
    handle = mock_open()
    handle.write.assert_called()


@patch("backend.src.web_scraping.send_email")
@patch("backend.src.web_scraping.search")
@patch("backend.src.web_scraping.find_xpath")
@patch("backend.src.web_scraping.set_driver")
def test_analise_fluxo_basico(mock_driver, mock_find, mock_search, mock_email):
    mock_driver_instance = MagicMock()
    mock_driver.return_value = mock_driver_instance
    mock_find.return_value = "//div"
    mock_search.side_effect = ["10", "20"]  # simula mudança

    analise(
        url="https://teste.com",
        driver_name="chrome",
        rep_time=0.001,
        delay=0,
        refresh=False,
        email="test@test.com",
        title="Teste",
        value="10"
    )

    assert mock_email.called
    mock_driver_instance.quit.assert_called()
