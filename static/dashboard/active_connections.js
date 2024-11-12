document.addEventListener('DOMContentLoaded', () => {
  // Receber os dados transformados do HTML, que por sua vez recebeu da View
  const acd = document.getElementById('active_connections_data');
  const data = JSON.parse(acd.textContent);
  const ctx = document.getElementById("active_connections");

  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.time_active_connections,  // eixo X: Horas e minutos
      datasets: [
        {
          label: 'Volume de Conexões Ativas',
          data: data.active_connections,  // Dados do volume de conexões
          lineTension: 0.3,
          backgroundColor: "rgba(0, 123, 255, 0.5)",  // Preenchimento do gráfico de área
          borderColor: "#007bff",
          borderWidth: 2,
          pointBackgroundColor: "#007bff",
          fill: true,  // Ativa o preenchimento abaixo da linha
        }
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,  // Começar o eixo Y no zero
          min: 0,
          grid: {
            color: "rgba(14,14,14,0.9)",
          },
          ticks: {
            color: "rgba(14,14,14,0.9)",
            stepSize: 5,
          },
        },
        x: {
          grid: {
            color: "rgba(14,14,14,0.9)",
          },
          ticks: {
            color: "rgba(14,14,14,0.9)",
          },
        },
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: '#000',
            font: {
              size: 13,
            },
            boxWidth: 10,
          },
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
              return '  ' + context.raw + ' Conexões';
            }
          },
        },
      },
    },
  });
});
