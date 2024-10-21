
// Mostra o overlay
function showLoadingOverlay() {
        document.getElementById('loading-overlay').style.display = 'flex'; // Mostra o overlay
    }

// Esconde o overlay
function hideLoadingOverlay() {
        document.getElementById('loading-overlay').style.display = 'none';
    }


document.addEventListener('DOMContentLoaded', function() {
    // Função para iniciar, parar ou reiniciar containers
    function handleContainerAction(buttonClass, urlBase) {
        document.querySelectorAll(buttonClass).forEach(button => {
            button.addEventListener('click', function() {
                const containerName = this.getAttribute('data-container-name');

                // Se qualquer botão for ativado, eu ja exibo a tela de carregamento
                showLoadingOverlay();
                fetch(`/${urlBase}/${containerName}/`, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);  // Mostra a mensagem retornada (sucesso ou erro)
                })
                .catch(error => {
                    console.error('Erro:', error);
                })
                .finally(() => {
                    hideLoadingOverlay();  // Sempre esconder o overlay, independentemente do resultado
                });
            });
        });
    }

    // Chama a função para cada ação de container
    handleContainerAction('.start-container-btn', 'start-container');  // Botões de iniciar container
    handleContainerAction('.stop-container-btn', 'stop-container');    // Botões de parar container
    handleContainerAction('.restart-container-btn', 'restart-container');  // Botões de reiniciar container
});