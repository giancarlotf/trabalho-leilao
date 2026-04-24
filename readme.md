# 📊 Monitor de Página Web

Script em Python que monitora mudanças em elementos de uma página usando Selenium e envia alertas por e-mail.

---

## 🚀 Funcionalidades

* Monitoramento automático de elementos
* Detecção de mudanças em tempo real
* Geração automática de XPath
* Envio de e-mail ao detectar alterações
* Histórico de valores salvos

---

## 🛠️ Tecnologias

* Python
* Selenium
* WebDriver Manager

---

## 📦 Instalação

```bash
git clone https://github.com/seu-usuario/seu-projeto.git
cd seu-projeto
pip install -r requirements.txt
```

---

## ▶️ Como usar

Exemplo básico:

```python
from monitor import analise

analise(
    url="https://exemplo.com",
    driver_name="chrome",
    rep_time=10,
    delay=5,
    refresh=True,
    email="seuemail@email.com",
    title="Monitoramento de preço",
    value="R$"
)
```

---

## ⚙️ Parâmetros

| Parâmetro    | Descrição                         |
| ------------ | --------------------------------- |
| url          | URL da página                     |
| driver_name  | Navegador (chrome, firefox, edge) |
| rep_time     | Tempo total (minutos)             |
| delay        | Intervalo entre verificações      |
| refresh      | Recarregar página                 |
| email        | Email para alerta                 |
| title        | Nome do monitoramento             |
| value        | Texto para buscar                 |
| manual_xpath | XPath manual                      |

---

## 📁 Estrutura do projeto

```
.
├── src/
├── log.txt
├── history.txt
└── README.md
```

---

## 🧠 Como funciona

1. Abre a página com Selenium
2. Encontra o elemento (XPath automático ou manual)
3. Monitora mudanças no valor
4. Se mudar → envia e-mail
5. Salva histórico

---

## 📌 Observações

* O script roda em modo headless (sem abrir navegador)
* Pode haver variação dependendo do site

---

## 🤝 Contribuição

Pull requests são bem-vindos!

---

## 📄 Licença

MIT
