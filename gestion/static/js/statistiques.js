document.addEventListener("DOMContentLoaded", () => {

    // ================= RECUPERATION DONNEES =================

    const labels = window.chartLabels || [];
    const data = window.chartData || [];

    // ================= GRAPHIQUE REVENUS =================

    const canvas = document.getElementById("revenusChart");

    if (canvas) {

        const ctx = canvas.getContext("2d");

        // ===== Gradient =====
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, "rgba(37, 99, 235, 0.45)");
        gradient.addColorStop(1, "rgba(37, 99, 235, 0.02)");

        new Chart(ctx, {
            type: "line",

            data: {
                labels: labels,
                datasets: [{
                    label: "Revenus",
                    data: data,

                    borderColor: "#2563eb",
                    backgroundColor: gradient,

                    borderWidth: 3,
                    tension: 0.45,
                    fill: true,

                    pointRadius: 3,
                    pointHoverRadius: 7,
                    pointBackgroundColor: "#fff",
                    pointBorderColor: "#2563eb",
                    pointBorderWidth: 2
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                animation: {
                    duration: 1200,
                    easing: "easeOutQuart"
                },

                interaction: {
                    intersect: false,
                    mode: "index"
                },

                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: "#6b7280",
                            font: {
                                size: 12,
                                weight: "500"
                            }
                        }
                    },

                    tooltip: {
                        backgroundColor: "rgba(17, 24, 39, 0.95)",
                        padding: 12,
                        titleColor: "#fff",
                        bodyColor: "#e5e7eb",
                        displayColors: false,

                        callbacks: {
                            label: function (context) {
                                return `${context.parsed.y.toLocaleString()} FCFA`;
                            }
                        }
                    }
                },

                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: "#9ca3af"
                        }
                    },

                    y: {
                        beginAtZero: true,

                        grid: {
                            color: "rgba(156, 163, 175, 0.15)"
                        },

                        ticks: {
                            color: "#9ca3af",
                            callback: value =>
                                value.toLocaleString() + " FCFA"
                        }
                    }
                }
            }
        });
    }

    // ================= MODE SOMBRE =================

    const darkBtn = document.getElementById("darkModeBtn");

    if (darkBtn) {

        const darkMode = localStorage.getItem("darkMode");

        if (darkMode === "true") {
            document.body.classList.add("dark-mode");
        }

        darkBtn.addEventListener("click", (e) => {

            e.preventDefault();

            document.body.classList.toggle("dark-mode");

            localStorage.setItem(
                "darkMode",
                document.body.classList.contains("dark-mode")
            );

        });

    }

});


// ================= ANIMATION DES VALEURS =================

function animateValue(element, endValue) {

    let startValue = 0;
    const duration = 1500;

    const stepTime = Math.max(
        10,
        Math.floor(duration / (endValue || 1))
    );

    const timer = setInterval(() => {

        startValue += Math.ceil((endValue || 0) / 100);

        if (startValue >= endValue) {
            startValue = endValue;
            clearInterval(timer);
        }

        element.textContent =
            startValue.toLocaleString() + " FCFA";

    }, stepTime);
}


// ================= INIT STAT ANIMATION =================

document.querySelectorAll(".stat-value").forEach(el => {

    const value = parseInt(
        el.textContent.replace(/\D/g, "")
    );

    if (!isNaN(value)) {

        el.textContent = "0 FCFA";
        animateValue(el, value);
    }

});


// ================= ANIMATION DES CARTES =================

const observer = new IntersectionObserver(entries => {

    entries.forEach(entry => {

        if (entry.isIntersecting) {
            entry.target.classList.add("show-card");
        }

    });

}, {
    threshold: 0.15
});


document.querySelectorAll(".card-pro").forEach(card => {

    card.classList.add("hidden-card");
    observer.observe(card);

});