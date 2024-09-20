
document.addEventListener('DOMContentLoaded', () => {
  // Receber os dados transformados do HTML, que por sua vez recebeu da View
  const chartData = document.getElementById('chart-data');
  const data = JSON.parse(chartData.textContent);
  const ctx = document.getElementById("myChart");

  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.dates,
      datasets: [
        {
          data: data.max_container_counts,
          lineTension: 0,
          backgroundColor: "transparent",
          borderColor: "#007bff",
          borderWidth: 5,
          pointBackgroundColor: "#007bff",
        },
      ],
    },
    options: {
      scales: {
        y: {
          grid: {
            color: "rgba(14,14,14,0.7)",
          },
          ticks: {
            color: "rgb(14,14,14)",
            // stepSize: 10, //
          },
        },
        x: {
          grid: {
            color: "rgba(14,14,14,0.7)",
          },
          ticks: {
            color: "#0e0e0e",
          },
        },
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: "#333",
          titleColor: "#fdfdfd",
          bodyColor: "#fdfdfd",
          borderColor: "#007bff",
          borderWidth: 2,
          caretSize: 13,
          bodyFont: {
            size: 17,
          },
          callbacks: {
            label: function (context) {
              return '  ' + context.raw;
            }
          },
        },
      },
    },
  });
});