/* ================= NAVIGATION ================= */

async function goToDate() {

    const month = document.getElementById("monthSelect").value;
    const year = document.getElementById("yearSelect").value;

    const response = await fetch(
        `?mois=${month}&annee=${year}`,
        {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        }
    );

    const html = await response.text();

    console.log(html); // <-- AJOUTE ÇA

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");

    const newDashboard =
        doc.querySelector("#dashboard-content");

    console.log(newDashboard); // <-- AJOUTE ÇA

    document.querySelector("#dashboard-content").innerHTML =
        newDashboard.innerHTML;

    initCalendar();
    initChart();
    animateKPI();
}


/* ================= CALENDRIER ================= */

function initCalendar() {

    document.removeEventListener("click", calendarHandler);

    document.addEventListener("click", calendarHandler);

}


function calendarHandler(e){

    const day = e.target.closest(".calendar-click");

    if(!day) return;


    const date = day.dataset.date;


    if(!date) return;


    if(typeof openModal === "function"){

        openModal(date);

    }

}


/* ================= CHART ================= */

/* ================= CHART ================= */

let chartInstance = null;

function initChart() {

    const el = document.getElementById("chart-data");
    const canvas = document.getElementById("chart");

    if (!el || !canvas) return;

    const data = JSON.parse(el.textContent);

    if (chartInstance) {
        chartInstance.destroy();
    }

    const ctx = canvas.getContext("2d");

    chartInstance = new Chart(ctx, {

        type: "bar",

        data: {
            labels: data.labels,

            datasets: [

                // Dépenses (en bas)
                {
                    label: "Dépenses",
                    data: data.depenses,

                    backgroundColor: "#dc2626",
                    borderColor: "#b91c1c",
                    borderWidth: 1,

                    stack: "total",

                    borderRadius: 0,
                    borderSkipped: false,

                    categoryPercentage: 0.8,
                    barPercentage: 0.9,
                    maxBarThickness: 18
                },

                // Revenus (au-dessus)
                {
                    label: "Revenus",
                    data: data.revenus,

                    backgroundColor: "#2563eb",
                    borderColor: "#1d4ed8",
                    borderWidth: 1,

                    stack: "total",

                    borderRadius: 0,
                    borderSkipped: false,

                    categoryPercentage: 0.8,
                    barPercentage: 0.9,
                    maxBarThickness: 18
                }

            ]
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
                    position: "top",

                    labels: {
                        usePointStyle: true,
                        pointStyle: "rect",
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

                    stacked: true,
                    offset: true,

                    grid: {
                        display: false
                    },

                    ticks: {
                        color: "#64748b",
                        autoSkip: true,
                        maxRotation: 0,
                        minRotation: 0
                    }
                },

                y: {

                    stacked: true,
                    beginAtZero: true,

                    grid: {
                        color: "rgba(148,163,184,0.15)"
                    },

                    ticks: {
                        color: "#64748b",

                        callback(value) {
                            return value.toLocaleString() + " FCFA";
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

