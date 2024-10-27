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
        const ipList = ips.split(',');
        openIpModal(containerName, 'remove-ip', interfaceList, ipList);
    });
});

// Função para exibir o overlay de carregamento
function showLoadingOverlay() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

// Função para esconder o overlay de carregamento
function hideLoadingOverlay() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// Função para validar se o IP é um IPv4 válido
function validationIpv4(ip) {
    const ipv4 = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipv4.test(ip);
}

// Variáveis globais para armazenar dados do modal
let currentContainerName = '';
let currentActionType = '';
let currentInterfaceList = [];
let currentIpList = [];

// Função para abrir o modal e preparar os dados para a ação de adicionar ou remover IP
function openIpModal(containerName, actionType, interfaceList, ipList = []) {
    const modalTitle = document.getElementById('modalLabel');
    const saveButton = document.getElementById('saveIpAction');
    const ipAddressInput = document.getElementById('ipAddressSwap');
    const ipAddressSelectContainer = document.getElementById('ipAddressSelectContainer');
    const ipTypeSelect = document.getElementById('ipTypeSelect');

    // Atualiza as variáveis globais com os valores atuais do modal
    currentContainerName = containerName;
    currentActionType = actionType;
    currentInterfaceList = interfaceList;
    currentIpList = ipList;

    // Muda o título e o texto do botão dependendo da ação (adicionar/remover)
    if (actionType === 'swap-ip') {
        modalTitle.textContent = `Trocar endereço IPv4 do container ${containerName}`;
        saveButton.textContent = 'Adicionar IPv4';
        ipAddressInput.style.display = 'block';
        ipAddressSelectContainer.style.display = 'none';
        ipTypeSelect.style.display = 'none';
    } else if (actionType === 'remove-ip') {
        modalTitle.textContent = `Remover IP do container ${containerName}`;
        saveButton.textContent = 'Remover IP';
        ipAddressInput.style.display = 'none';
        ipAddressSelectContainer.style.display = 'block';
        ipTypeSelect.style.display = 'block';
    }

    const interfaceSelect = document.getElementById('interface');
    interfaceSelect.innerHTML = '';

    // Adicionar as interfaces como opções no select
    [...new Set(interfaceList)].forEach(function(iface) {
        const option = document.createElement('option');
        option.value = iface;
        option.textContent = iface;
        interfaceSelect.appendChild(option);
    });

    // Caso seja uma ação de remoção de IP, popular o select de IPs
    if (actionType === 'remove-ip') {
        const ipSelect = document.getElementById('ipAddressSelect');
        ipSelect.innerHTML = '';

        ipList.forEach(function(ip) {
            const option = document.createElement('option');
            option.value = ip;
            option.textContent = ip;
            ipSelect.appendChild(option);
        });
    }

    const ipModal = new mdb.Modal(document.getElementById('modalIpActions'));
    ipModal.show();
}

// Adiciona o evento de clique no botão de salvar uma única vez após carregar a página
document.getElementById('saveIpAction').addEventListener('click', function() {
    const selectedInterface = document.getElementById('interface').value;
    const selectedIpType = document.getElementById('ipType').value;
    let ipAddress = '';

    if (currentActionType === 'remove-ip') {
        ipAddress = document.getElementById('ipAddressSelect').value;
    } else {
        ipAddress = document.getElementById('ipAddress').value;
    }

    if (!selectedInterface || (currentActionType === 'remove-ip' && !selectedIpType) || !ipAddress) {
        alert('Por favor, preencha todos os campos.');
        return;
    }

    console.log(selectedIpType)
    // Se não for um IPv4 na hora de trocar IP, já está errado
    if (!validationIpv4(ipAddress) && currentActionType === 'swap-ip') {
        alert(`Por favor, digite um ${selectedIpType} válido!`);
        return;
    }
    // Se não é adicionar IP, então é remover. Se IP for v4 e tipo v6 está errado
    if (validationIpv4(ipAddress) && selectedIpType === 'ipv6') {
        alert(`Por favor, escolha um endereço ${selectedIpType} condizente!`);
        return;
    }
    // Se for remover, IP for v6 e tipo v4, está errado também
    if (!validationIpv4(ipAddress) && selectedIpType === 'ipv4') {
        alert(`Por favor, escolha um endereço ${selectedIpType} condizente!`);
        return;
    }


    showLoadingOverlay();

    fetch(`/${currentActionType}/${currentContainerName}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify({
            interface: selectedInterface,
            ip_type: selectedIpType,
            ip_address: ipAddress
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        const ipModalElement = document.getElementById('modalIpActions');
        const ipModal = mdb.Modal.getInstance(ipModalElement); // Obtenha a instância atual do modal
        ipModal.hide(); // Fecha o modal
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Ocorreu um erro ao processar a solicitação.');
    })
    .finally(() => {
        hideLoadingOverlay();
    });
});