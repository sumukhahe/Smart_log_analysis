document.addEventListener("DOMContentLoaded", function () {
  try {
    var ctx = document.getElementById("logChart").getContext("2d");

    var displayNormal = Math.max(1, normalCount);
    var displayAnomaly = Math.max(1, anomalyCount);

    new Chart(ctx, {
      type: "bar", // Change from "pie" to "bar"
      data: {
        labels: ["Normal Logs", "Anomaly Logs"],
        datasets: [
          {
            label: "Log Counts", // Add a label for the dataset
            data: [displayNormal, displayAnomaly],
            backgroundColor: ["#2ecc71", "#e74c3c"],
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true, // Ensure the y-axis starts at zero
          },
        },
        plugins: {
          title: {
            display: true,
            text: `Log Analysis: ${normalCount} Normal, ${anomalyCount} Anomalies`,
          },
        },
      },
    });
  } catch (error) {
    console.error("Chart rendering error:", error);
  }
});
