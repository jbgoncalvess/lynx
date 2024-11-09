// Função para exibir o overlay de carregamento
function showLoadingOverlay() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

// Função para esconder o overlay de carregamento
function hideLoadingOverlay() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// Função para exibir o modal de confirmação de exclusão
function showDeleteConfirmation(imageName) {
    document.getElementById('imageToDelete').textContent = imageName;

    // Exibe o modal
    let deleteModal = new mdb.Modal(document.getElementById('modalDeleteConfirmation'));
    deleteModal.show();

    // Define a ação do botão de confirmação
    document.getElementById('confirmDeleteButton').onclick = function () {
        deleteImage(imageName); // Envia a solicitação para excluir a imagem
    };
}

// Função para enviar a solicitação de exclusão ao back-end
function deleteImage(imageName) {
    showLoadingOverlay();
    fetch(`/delete-image/${imageName}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Imagem excluída com sucesso!");
            location.reload(); // Atualiza a página para refletir a exclusão
        } else {
            alert("Erro ao excluir a imagem.");
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    })
    .finally(() => hideLoadingOverlay());
}