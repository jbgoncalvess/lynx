
document.addEventListener('DOMContentLoaded', () => {
    const ram = document.getElementById('ram_data');
    const data = JSON.parse(ram.textContent);
    const ctx = document.getElementById('ram').getContext('2d');
    // Configurações do gráfico de barras
    const ram_graph = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.container_names, // Exemplo de meses
            datasets: [{
                label: 'Uso de Memória RAM (MB)',
                data: data.ram_usages,  // Exemplo de dados
                backgroundColor: 'rgba(54, 162, 235, 0.7)',  // Cor das barras
                borderColor: 'rgba(54, 162, 235, 1)',  // Cor da borda das barras
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',  // Legenda no topo (pode ajustar para 'bottom', 'left', etc)
                    labels: {
                        color: '#000',  // Cor do texto da legenda
                        padding: 10  // Espaçamento ao redor da legenda
                    }
                },
                tooltip: {
                    backgroundColor: "#333",
                    titleColor: "#fdfdfd",
                    bodyColor: "#fdfdfd",
                    borderColor: "#3ed91b",
                    borderWidth: 2,
                    caretSize: 13,
                    bodyFont: {
                        size: 17,
                    },
                    callbacks: {
                        label: function (context) {
                            return '  ' + context.raw + '%';
                        }
                    },
                },
            },
            layout: {
                padding: {
                    top: 20,  // Espaçamento no topo do gráfico
                    right: 10,
                    bottom: 10,
                    left: 10
                }
            },
            scales: {
                y: {
                    beginAtZero: true,  // Começar o eixo Y no zero
                    min: 0,
                    max: 100,
                    grid: {
                        color: "rgba(14,14,14,0.8)",
                    },
                    ticks: {
                        color: "rgb(0,0,0)",
                        stepSize: 25  // Exibir números inteiros no eixo Y
                    },
                },

                x: {
                    grid: {
                        color: "rgba(14,14,14,0.8)",
                    },
                    ticks: {
                        color: "rgb(0,0,0)",
                        stepSize: 25  // Exibir números inteiros no eixo Y
                    },
                },
            }
        }
    });
});