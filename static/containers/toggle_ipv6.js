// Selecionar todos os botões para habilitar/desabilitar IPv6
const ipv6ConfigButtons = document.querySelectorAll('.toggle-config-btn');

function showLoadingOverlay() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

// Função para esconder o overlay de carregamento
function hideLoadingOverlay() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// Manipular clique no botão de habilitar/desabilitar IPv6
ipv6ConfigButtons.forEach(button => {
    button.addEventListener('click', function() {
        const containerName = this.getAttribute('data-container-name');
        openIpv6Modal(containerName);
    });
});


function openIpv6Modal(containerName) {
    const modalTitle = document.getElementById('modalIpv6Label');
    modalTitle.textContent = `Configurar IPv6 no container ${containerName}`;

    // Atualiza o nome do container selecionado
    currentContainerName = containerName;

    // Exibe o modal de configuração de IPv6
    const ipv6Modal = new mdb.Modal(document.getElementById('modalIpv6Toggle'));
    ipv6Modal.show();
}

// Evento de clique no botão de salvar configuração IPv6
document.getElementById('saveIpv6ToggleAction').addEventListener('click', function() {
    const ipv6Action = document.getElementById('ipv6Toggle').value; // Captura ação de IPv6 (enable ou disable)
    console.log(ipv6Action)

    showLoadingOverlay(); // Mostra o overlay de carregamento

    fetch(`/toggle-ipv6/${currentContainerName}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': window.CSRF_TOKEN
        },
        body: JSON.stringify({
            action: ipv6Action
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message); // Exibe a mensagem do backend
        const ipv6ModalElement = document.getElementById('modalIpv6Toggle');
        const ipv6Modal = mdb.Modal.getInstance(ipv6ModalElement);
        ipv6Modal.hide(); // Fecha o modal após salvar as alterações
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Ocorreu um erro ao processar a solicitação.');
    })
    .finally(() => hideLoadingOverlay());
});
