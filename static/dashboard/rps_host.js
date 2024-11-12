document.addEventListener('DOMContentLoaded', () => {
  // Receber os dados transformados do HTML, que por sua vez recebeu da View
  const rhd = document.getElementById('rps_host_data');
  const data = JSON.parse(rhd.textContent);
  const ctx = document.getElementById("rps_host");

  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.times_host_rps,  // eixo X: Horas e minutos
      datasets: [
        {
          label: 'Requisições por Segundo (RPS)',
          data: data.rps_host,  // Dados do volume de conexões
          lineTension: 0.3,
          backgroundColor: "rgba(0, 123, 255, 0.5)",  // Preenchimento do gráfico de área
          borderColor: "#007bff",  // Cor da linha
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
              return '  ' + context.raw + ' Requisições';
            }
          },
        },
      },
    },
  });
});
