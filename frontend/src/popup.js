document.getElementById('dataForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Previne o envio padrão do formulário

    // 1. Coleta dos dados dos campos
    const name = document.getElementById('name').value.trim();
    const url = document.getElementById('url').value.trim();
    const email = document.getElementById('email').value.trim();
    const value = document.getElementById('valor').value.trim();
    const tag = document.getElementById('tag').value.trim();
    const interval = document.getElementById('interval').value.trim();
    const operation = document.getElementById('operation').value.trim();
    const title = document.getElementById('title').value.trim();
    const attribute = document.getElementById('attribute').value.trim();
    const isRefreshActive = document.getElementById('refresh').checked;

    //2. Criação do objeto de payload (dados a serem enviados)
    const dataPayload = {
        name: name,
        url: url,
        email: email,
        value: value,
        tag: tag,
        attribute: attribute,
        title: title,
        interval: interval,
        operation: operation,
        refresh: isRefreshActive 
    };

    // 3. Definição do endpoint (URL do seu servidor)
    const apiUrl = 'http://127.0.0.1:5000/api/dados'; 

    // 4. Exibição de estado de processamento
    const submitButton = document.getElementById('submitBtn');
    const statusElement = document.getElementById('statusMessage');
    
    submitButton.disabled = true;
    submitButton.innerHTML = 'Enviando...';
    statusElement.textContent = 'Enviando dados para o servidor...';
    statusElement.style.color = 'blue';

    try {
        // 5. Execução da requisição POST
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' // Informa que o corpo da requisição é JSON
            },
            body: JSON.stringify(dataPayload) // Converte o objeto JavaScript em string JSON
        });

    } catch (error) {
        // 7. Tratamento de erros de rede (ex: o servidor está fora do ar)
        console.error('Erro de rede ao conectar com o backend:', error);
        statusElement.textContent = '🔴 Erro de conexão. Verifique se o backend está online.';
        statusElement.style.color = 'red';
    } finally {
        // 8. Restaura o estado do botão, independentemente do resultado
        submitButton.disabled = false;
        submitButton.innerHTML = 'Salvar Serviço';
    }
});