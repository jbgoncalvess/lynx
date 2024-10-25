function showLoadingOverlay() {
        document.getElementById('loading-overlay').style.display = 'flex'; // Mostra o overlay
    }
// Esconde o overlay
function hideLoadingOverlay() {
        document.getElementById('loading-overlay').style.display = 'none';
    }

function validationIpv4(ip){
    const ipv4 = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipv4.test(ip);
}

document.addEventListener('DOMContentLoaded', function() {
    // Selecionar todos os botões "Adicionar IP" e "Remover IP"
    const swapIpButtons = document.querySelectorAll('.swap-ip-btn');
    const removeIpButtons = document.querySelectorAll('.remove-ip-btn');

    // Manipular clique no botão de adicionar IP
    swapIpButtons.forEach(button => {
        button.addEventListener('click', function() {
            const containerName = this.getAttribute('data-container-name');
            const interfaces = this.getAttribute('data-interfaces');
            const interfaceList = interfaces.split(',');
            openIpModal(containerName, 'swap-ip', interfaceList);
        });
    });

    // Manipular clique no botão de remover IP
    removeIpButtons.forEach(button => {
        button.addEventListener('click', function() {
            const containerName = this.getAttribute('data-container-name');
            const interfaces = this.getAttribute('data-interfaces');
            const ips = this.getAttribute('data-ips');
            const interfaceList = interfaces.split(',');
            const ipList = ips.split(',');  // Transformar os IPs em uma lista
            openIpModal(containerName, 'remove-ip', interfaceList, ipList);
        });
    });

    // Função para abrir o modal e preparar os dados para a ação de adicionar ou remover IP
    function openIpModal(containerName, actionType, interfaceList, ipList = []) {
        const modalTitle = document.getElementById('modalLabel');
        const saveButton = document.getElementById('saveIpAction');
        const ipAddressInput = document.getElementById('ipAddressSwap')
        const ipAddressSelectContainer = document.getElementById('ipAddressSelectContainer')
        const ipTypeSelect = document.getElementById('ipTypeSelect')

        // Muda o título e o texto do botão dependendo da ação (adicionar/remover)
        if (actionType === 'swap-ip') {
            modalTitle.textContent = `Trocar endereço IPv4 do container ${containerName}`;
            saveButton.textContent = 'Adicionar IPv4';
            ipAddressInput.style.display = 'block'; // Mostrar input para adicionar IP
            ipAddressSelectContainer.style.display = 'none'; // Ocultar select de remoção de IP
            ipTypeSelect.style.display = 'none';
        } else if (actionType === 'remove-ip') {
            modalTitle.textContent = `Remover IP do container ${containerName}`;
            saveButton.textContent = 'Remover IP';
            ipAddressInput.style.display = 'none'; // Mostrar input para adicionar IP
            ipAddressSelectContainer.style.display = 'block'; // Ocultar select de remoção de IP
            ipTypeSelect.style.display = 'block';
        }



        const interfaceSelect = document.getElementById('interface');

        interfaceSelect.innerHTML = '';

        interfaceList = [...new Set(interfaceList)]

        // Adicionar as interfaces como opções no select
        interfaceList.forEach(function(iface) {
            const option = document.createElement('option');
            option.value = iface;
            option.textContent = iface;
            interfaceSelect.appendChild(option);
        });
        console.log(ipAddressSelectContainer)
        console.log(ipAddressInput)

        // Caso seja uma ação de remoção de IP, também vamos popular o select de IPs
        if (actionType === 'remove-ip') {
            const ipSelect = document.getElementById('ipAddressSelect');  // Select de IPs no modal

            // Limpar o select de IPs antes de adicionar novas opções
            ipSelect.innerHTML = '';

            // Adicionar os IPs como opções no select
            ipList.forEach(function(ip) {
                const option = document.createElement('option');
                option.value = ip;
                option.textContent = ip;
                ipSelect.appendChild(option);
            });

            // Exibir o select de IPs (caso esteja escondido por padrão)
            document.getElementById('ipAddressSelectContainer').style.display = 'block';
        } else {
            // Esconder o select de IPs se estivermos adicionando um novo IP
            document.getElementById('ipAddressSelectContainer').style.display = 'none';
        }

        // Mostrar o modal usando MDBootstrap
        const ipModal = new mdb.Modal(document.getElementById('modalIpActions'));
        ipModal.show();

        // Manipular o clique no botão de salvar no modal
        saveButton.addEventListener('click', function() {
            const selectedInterface = document.getElementById('interface').value;
            const selectedIpType = document.getElementById('ipType').value;
            let ipAddress = '';

            // Se for uma ação de remoção, obter o IP selecionado no select de IPs
            if (actionType === 'remove-ip') {
                ipAddress = document.getElementById('ipAddressSelect').value;
            } else {
                // Se for uma ação de adição, pegar o IP digitado no campo de input
                ipAddress = document.getElementById('ipAddress').value;
            }

            // Verifica se os campos foram preenchidos
            if (!selectedInterface || !selectedIpType || !ipAddress) {
                alert('Por favor, preencha todos os campos.');
                return;
            }

            if (!(validationIpv4(ipAddress))) {
                alert('Por favor, digita um IPv4 certo!');
                return;
            }

            showLoadingOverlay()
            // Fazer a requisição via fetch para adicionar ou remover o IP
            fetch(`/${actionType}/${containerName}/`, {
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
            })
            .finally(()=>{
                hideLoadingOverlay()
            });
        });
    }
});
