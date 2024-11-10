// Selecionar todos os botões "Adicionar IP"
const swapIpButtons = document.querySelectorAll('.swap-ip-btn');

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
    const ipv4Pattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipv4Pattern.test(ip);
}

// Função para abrir o modal para adicionar IP
function openIpModal(containerName, interfaceList) {
    const modalTitle = document.getElementById('modalLabel');
    const saveButton = document.getElementById('saveIpAction');
    const ipAddressInput = document.getElementById('ipAddress');

    // Configura título e botão do modal
    modalTitle.textContent = `Adicionar IPv4 ao container ${containerName}`;
    saveButton.textContent = 'Adicionar IPv4';

    // Exibe o campo para adicionar IPv4
    document.getElementById('ipAddressContainer').style.display = 'block';

    // Popula o seletor de interfaces com as opções
    const interfaceSelect = document.getElementById('interface');
    interfaceSelect.innerHTML = '';
    interfaceList.forEach(iface => {
        const option = document.createElement('option');
        option.value = iface;
        option.textContent = iface;
        interfaceSelect.appendChild(option);
    });

    // Exibe o modal usando o MDBootstrap
    const ipModal = new mdb.Modal(document.getElementById('modalIpActions'));
    ipModal.show();

    // Armazena os dados do container para envio posterior
    saveButton.onclick = () => addIpAddress(containerName);
}

// Função para enviar a solicitação de adicionar IPv4 ao servidor
function addIpAddress(containerName) {
    const selectedInterface = document.getElementById('interface').value;
    const ipAddress = document.getElementById('ipAddress').value;

    if (!ipAddress || !validationIpv4(ipAddress)) {
        alert('Por favor, digite um IPv4 válido!');
        return;
    }

    showLoadingOverlay();

    fetch(`/containers/swap-ipv4/${containerName}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': window.CSRF_TOKEN
        },
        body: JSON.stringify({
            interface: selectedInterface,
            ip_address: ipAddress,
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        mdb.Modal.getInstance(document.getElementById('modalIpActions')).hide();
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Ocorreu um erro ao processar a solicitação.');
    })
    .finally(() => hideLoadingOverlay());
}

// Configura os botões para abrir o modal com as interfaces corretas
swapIpButtons.forEach(button => {
    button.addEventListener('click', function() {
        const containerName = this.getAttribute('data-container-name');
        const interfaces = this.getAttribute('data-interfaces').split(',');
        openIpModal(containerName, interfaces);
    });
});
