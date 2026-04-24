import src.web_scraping as ws
from flask import Flask, request, jsonify
from flask_cors import CORS

# Inicializa a aplicação Flask (backend)
app = Flask(__name__)

# Permite que o frontend (ex: popup.js) se comunique com o backend
CORS(app)

# Classe responsável por armazenar e processar os dados recebidos do frontend
class datahandler:

    def __init__(self):
        self.data = None

    def receive_data(self, data):
        self.data = data

        for key in [
            "name", "url", "email", "tag", "attribute",
            "value", "interval", "operation", "title", "refresh"
        ]:
            setattr(self, key, data.get(key))

    # Método responsável por validar os dados e preparar o scraping
    def setup(self):
        driver_name = "chrome"
        
        # Variável que armazenará o XPath (caso seja montado)
        xpath = None
        self.interval = float(self.interval)
        self.operation = float(self.operation)

        # Validação do nome do usuário
        if len(self.name) < 3 or not self.name.replace(" ", "").isalpha():
            ws.log("User/ERROR", "Nome inválido")
            return

        # Validação da URL (função retorna valor em caso de erro)
        if ws.validate_url(self.url):
            return

        # Verifica se o usuário forneceu dados para montar o XPath
        if not self.tag  or not self.attribute:
            self.tag = None
            self.attribute = None  
        else:
            # Monta o XPath dinamicamente com base nos dados fornecidos
            xpath = f"//{self.tag}[@{self.attribute}='{self.value}']"

        # Validação do intervalo de leitura
        if not isinstance(self.interval, (int, float)) or not self.interval:
            ws.log("User/ERROR", "Tempo de medição inválido")
            return

        # Validação do tempo total de operação
        if not isinstance(self.operation, (int, float)) or not self.operation:
            ws.log("User/ERROR", "Tempo de operação inválido")
            return

        # Logs informativos sobre os dados recebidos
        ws.log("User/INFO", f"Usuário: {self.name}")
        ws.log("User/INFO", f"URL: {self.url}")

        # Exibe o XPath ou valor inicial dependendo da escolha do usuário
        if xpath:
            ws.log("User/INFO", f"XPath: {xpath}")
        else:
            ws.log("User/INFO", f"Valor inicial: {self.value}")             

        # Logs de configuração da execução
        ws.log("User/INFO", f"Driver selecionado: {driver_name}")
        ws.log("User/INFO", f"Tempo de operação: {self.operation}")
        ws.log("User/INFO", f"Intervalo entre leituras: {self.interval}")

        # Chamada da função principal de scraping
        ws.analise(self.url, driver_name, self.operation, self.interval,
                   self.refresh, self.email, self.title, self.value, manual_xpath=xpath)

data_handler = DataHandler()

@app.route('/api/data', methods=['POST'])
def receive_data():
    data_JSON = request.get_json()
    data_handler.receive_data(data_JSON)
    data_handler.setup()
    return {"status": "ok"}, 200

# Inicializa o servidor Flask em modo de debug
if __name__ == '__main__':
    app.run(debug=True) 
