import web_scraping as ws
from flask import Flask, request, jsonify
from flask_cors import CORS

# Inicializa a aplicação Flask (backend)
app = Flask(__name__)

# Permite que o frontend (ex: popup.js) se comunique com o backend
CORS(app)

# Classe responsável por armazenar e processar os dados recebidos do frontend
class datahandler:

    def __init__(self , data: dict):
        # Converte automaticamente o dicionário recebido (JSON) em atributos da classe
        self.__dict__.update(data)

    # Endpoint que recebe os dados enviados pelo frontend via requisição POST
    @app.route('/app/dados', methods=['POST'])
    def receive_data():

        # Obtém os dados enviados no formato JSON
        data_JSON = request.get_json()
        # Cria uma instância da classe com os dados recebidos
        data_instace = datahandler(**data_JSON)
        # Chama o método responsável por validar e iniciar o processo
        data_instace.setup()

    # Método responsável por validar os dados e preparar o scraping
    def setup(self):

        # Variável que armazenará o XPath (caso seja montado)
        xpath = None

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
        ws.log("User/INFO", f"Driver selecionado: chrome")
        ws.log("User/INFO", f"Tempo de operação: {self.operation}")
        ws.log("User/INFO", f"Intervalo entre leituras: {self.interval}")

        # Chamada da função principal de scraping
        ws.analise(self.url, "chrome", self.operation, self.interval, self.refresh, self.value, manual_xpath=xpath)     

# Inicializa o servidor Flask em modo de debug
if __name__ == '__main__':
    app.run(debug=True) 
