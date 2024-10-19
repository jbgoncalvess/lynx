document.addEventListener('DOMContentLoaded', function() {
    // Função genérica para iniciar, parar ou reiniciar containers
    function handleContainerAction(buttonClass, urlBase) {
        document.querySelectorAll(buttonClass).forEach(button => {
            button.addEventListener('click', function() {
                const containerName = this.getAttribute('data-container-name');

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
                .catch(error => console.error('Erro:', error));
            });
        });
    }

    // Chama a função para cada ação de container
    handleContainerAction('.start-container-btn', 'start-container');  // Botões de iniciar container
    handleContainerAction('.stop-container-btn', 'stop-container');    // Botões de parar container
    handleContainerAction('.restart-container-btn', 'restart-container');  // Botões de reiniciar container
});
