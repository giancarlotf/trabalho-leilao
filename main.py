import web_scraping as ws
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class datahandler:

    def __init__(self , data: dict):

        self.__dict__.update(data)

    @app.route('/app/dados', methods=['POST'])
    def receive_data():

        data_JSON = request.get_json()
        data_instace = datahandler(**data_JSON)
        data_instace.setup()

    def setup(self):

        xpath = None

        if len(self.name) < 3 or not self.name.replace(" ", "").isalpha():
            ws.log("User/ERROR", "Nome inválido")
            return
        
        if ws.validate_url(self.url):
            return
        
        if not self.tag  or not self.attribute:
            self.tag = None
            self.attribute = None  
        else:
            xpath = f"//{self.tag}[@{self.attribute}='{self.value}']"

        if not isinstance(self.interval, (int, float)) or not self.interval:
            ws.log("User/ERROR", "Tempo de medição inválido")
            return
        
        if not isinstance(self.operation, (int, float)) or not self.operation:
            ws.log("User/ERROR", "Tempo de operação inválido")
            return
        
        ws.log("User/INFO", f"Usuário: {self.name}")
        ws.log("User/INFO", f"URL: {self.url}")

        if xpath:
            ws.log("User/INFO", f"XPath: {xpath}")
        else:
            ws.log("User/INFO", f"Valor inicial: {self.value}")             

        ws.log("User/INFO", f"Driver selecionado: chrome")
        ws.log("User/INFO", f"Tempo de operação: {self.operation}")
        ws.log("User/INFO", f"Intervalo entre leituras: {self.interval}")
        
        ws.analise(self.url, "chrome", self.operation, self.interval, self.refresh, self.value, manual_xpath=xpath)     

if __name__ == '__main__':
    app.run(debug=True) 
