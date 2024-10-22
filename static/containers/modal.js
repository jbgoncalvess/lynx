document.addEventListener('DOMContentLoaded', function() {
    // Selecionar todos os botões "Adicionar IP" e "Remover IP"
    const addIpButtons = document.querySelectorAll('.adicionar-ip-btn');
    const removeIpButtons = document.querySelectorAll('.remover-ip-btn');

    // Manipular clique no botão de adicionar IP
    addIpButtons.forEach(button => {
        button.addEventListener('click', function() {
            const containerName = this.getAttribute('data-container-name');
            openIpModal(containerName, 'add');
        });
    });

    // Manipular clique no botão de remover IP
    removeIpButtons.forEach(button => {
        button.addEventListener('click', function() {
            const containerName = this.getAttribute('data-container-name');
            openIpModal(containerName, 'remove');
        });
    });

    // Função para abrir o modal e preparar os dados para a ação de adicionar ou remover IP
    function openIpModal(containerName, actionType) {
        const modalTitle = document.getElementById('modalLabel');
        const saveButton = document.getElementById('saveIpAction');

        // Muda o título e o texto do botão dependendo da ação (adicionar/remover)
        if (actionType === 'add') {
            modalTitle.textContent = `Adicionar IP ao container ${containerName}`;
            saveButton.textContent = 'Adicionar IP';
        } else if (actionType === 'remove') {
            modalTitle.textContent = `Remover IP do container ${containerName}`;
            saveButton.textContent = 'Remover IP';
        }

        // Mostrar o modal usando MDBootstrap
        const ipModal = new mdb.Modal(document.getElementById('modalIpActions'));
        ipModal.show();

        // Manipular o clique no botão de salvar no modal
        saveButton.addEventListener('click', function() {
            const selectedInterface = document.getElementById('interface').value;
            const selectedIpType = document.getElementById('ipType').value;
            const ipAddress = document.getElementById('ipAddress').value;

            // Verifica se os campos foram preenchidos
            if (!selectedInterface || !selectedIpType || !ipAddress) {
                alert('Por favor, preencha todos os campos.');
                return;
            }

            // Fazer a requisição via fetch para adicionar ou remover o IP
            fetch(`/containers/${containerName}/ip/${actionType}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    // Se você estiver usando CSRF no Django, adicione o token aqui
                    // 'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    interface: selectedInterface,
                    ip_type: selectedIpType,
                    ip_address: ipAddress
                })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);  // Exibir mensagem de sucesso ou erro
                ipModal.hide();  // Fechar o modal
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Ocorreu um erro ao processar a solicitação.');
                ipModal.hide();  // Fechar o modal em caso de erro também
            });
        });
    }
});
