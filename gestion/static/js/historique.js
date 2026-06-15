/* ================= NAVIGATION ================= */

function goToDate() {

    const month = document.getElementById("monthSelect")?.value;
    const year = document.getElementById("yearSelect")?.value;

    if (!month || !year) return;

    const params = new URLSearchParams(window.location.search);

    params.set("mois", month);
    params.set("annee", year);

    window.location.search = params.toString();
}


/* ================= CALENDRIER ================= */

function initCalendar() {

    const days = document.querySelectorAll(".calendar-click");

    if (!days.length) return;

    days.forEach(day => {

        day.addEventListener("click", () => {

            const date = day.dataset.date;

            if (!date) return;

            // ⚠️ vient de ton autre JS (modal.js)
            if (typeof openModal === "function") {
                openModal(date);
            }

        });

    });
}


/* ================= CHART ================= */

let chartInstance = null;

function initChart() {
  
    const el = document.getElementById("chart-data");
    const canvas = document.getElementById("chart");

    if (!el || !canvas) return;

    const data = JSON.parse(el.textContent);
    console.log(typeof data);
    
    if (chartInstance) {
        chartInstance.destroy();
    }

    const ctx = canvas.getContext("2d");

    const gradientRevenue = ctx.createLinearGradient(0, 0, 0, 400);
    gradientRevenue.addColorStop(0, "rgba(37,99,235,0.35)");
    gradientRevenue.addColorStop(1, "rgba(37,99,235,0)");

    const gradientDepense = ctx.createLinearGradient(0, 0, 0, 400);
    gradientDepense.addColorStop(0, "rgba(220,38,38,0.30)");
    gradientDepense.addColorStop(1, "rgba(220,38,38,0)");

    chartInstance = new Chart(ctx, {

        type: "line",

        data: {
            labels: data.labels,

            datasets: [
                {
                    label: "Revenus",
                    data: data.revenus,

                    borderColor: "#2563eb",
                    backgroundColor: gradientRevenue,

                    fill: true,

                    borderWidth: 4,

                    tension: 0.4,

                    pointRadius: 5,
                    pointHoverRadius: 8,

                    pointBackgroundColor: "#2563eb",
                    pointBorderColor: "#fff",
                    pointBorderWidth: 2
                },

                {
                    label: "Dépenses",
                    data: data.depenses,

                    borderColor: "#dc2626",
                    backgroundColor: gradientDepense,

                    fill: true,

                    borderWidth: 4,

                    tension: 0.4,

                    pointRadius: 5,
                    pointHoverRadius: 8,

                    pointBackgroundColor: "#dc2626",
                    pointBorderColor: "#fff",
                    pointBorderWidth: 2
                }
            ]
        },

        options: {

            responsive: true,
            maintainAspectRatio: false,

            interaction: {
                intersect: false,
                mode: "index"
            },

            animation: {
                duration: 1500,
                easing: "easeOutQuart"
            },

            plugins: {

                legend: {
                    position: "top",

                    labels: {
                        usePointStyle: true,
                        pointStyle: "circle",
                        padding: 20,
                        font: {
                            size: 13,
                            weight: "bold"
                        }
                    }
                },

                tooltip: {

                    backgroundColor: "#0f172a",

                    padding: 12,

                    titleFont: {
                        size: 14
                    },

                    bodyFont: {
                        size: 13
                    },

                    callbacks: {
                        label(context) {
                            return (
                                context.dataset.label +
                                " : " +
                                context.parsed.y.toLocaleString() +
                                " FCFA"
                            );
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
                        color: "#64748b"
                    }
                },

                y: {

                    beginAtZero: true,

                    grid: {
                        color: "rgba(148,163,184,0.15)"
                    },

                    ticks: {
                        color: "#64748b",

                        callback(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });

}
/* ================= KPI ANIMATION ================= */

function animateKPI() {

    const cards = document.querySelectorAll(".kpi-card");

    if (!cards.length) return;

    cards.forEach((card, index) => {

        // état initial (avant animation)
        card.style.opacity = "0";
        card.style.transform = "translateY(30px) scale(0.96)";
        card.style.filter = "blur(6px)";

        // animation progressive (stagger)
        setTimeout(() => {

            card.style.transition = "all 0.6s cubic-bezier(0.16, 1, 0.3, 1)";

            card.style.opacity = "1";
            card.style.transform = "translateY(0) scale(1)";
            card.style.filter = "blur(0px)";

        }, index * 120);

    });
}

function updateDashboard(mois, annee) {

    fetch(`/api/dashboard?mois=${mois}&annee=${annee}`)
        .then(res => res.json())
        .then(data => {

            document.querySelector(".kpi-card.revenu .kpi-amount").textContent =
                data.kpi.revenu + " FCFA";

            document.querySelector(".kpi-card.depense .kpi-amount").textContent =
                data.kpi.depense + " FCFA";

            document.querySelector(".kpi-card.benefice .kpi-amount").textContent =
                data.kpi.benefice + " FCFA";
        });
}

/* ================= INIT ================= */

document.addEventListener("DOMContentLoaded", () => {

    initCalendar();
    initChart();
    animateKPI();

});

