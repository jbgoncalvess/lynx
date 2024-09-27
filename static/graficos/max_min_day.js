document.addEventListener('DOMContentLoaded', () => {
  // Receber os dados transformados do HTML, que por sua vez recebeu da View
  const mmd = document.getElementById('mmd_data');
  const data = JSON.parse(mmd.textContent);
  const ctx = document.getElementById("max_min_day");

  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.dates,
      datasets: [
        {
          label: 'Mínimo de Containers',
          data: data.min_container_counts,  // Dados de contêineres mínimos
          lineTension: 0,
          backgroundColor: "transparent",
          borderColor: "#ff0000",  // Cor da linha para o mínimo
          borderWidth: 2,
          pointBackgroundColor: "#ff0000",
        },
        {
          label: 'Máximo de Containers',
          data: data.max_container_counts,  // Dados de contêineres máximos
          lineTension: 0,
          backgroundColor: "transparent",
          borderColor: "#007bff",
          borderWidth: 3,
          pointBackgroundColor: "#007bff",
        },
      ],
    },
    options: {
      scales: {
        y: {
          grid: {
            color: "rgba(14,14,14,0.9)",
          },
          ticks: {
            color: "rgba(14,14,14,0.9)",
            // stepSize: 10, //
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
          display: true,  // Exibe a legenda
          position: 'top',  // Posição da legenda ('top', 'bottom', 'left', 'right')
          labels: {
            color: '#000',  // Cor do texto da legenda
            font: {
              size: 13,  // Tamanho da fonte
            },
            boxWidth: 10,  // Largura da caixa de cor da legenda
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
              return '  ' + context.raw + ' Containers';
            }
          },
        },
      },
    },
  });
});