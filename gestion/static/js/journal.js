document.addEventListener("DOMContentLoaded", () => {

    sendForm("form-activity");
    sendForm("form-depense");
    sendForm("form-paiement");

});


// ==========================
// SUBMIT AJAX
// ==========================
function sendForm(formId) {

    const form = document.getElementById(formId);

    if (!form) return;

    form.addEventListener("submit", async function (e) {

        e.preventDefault();

        const formData = new FormData(this);

        try {

            const response = await fetch("", {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const data = await response.json();

            if (data.success) {

                this.reset();

                // 🔥 mise à jour avec animation
                refreshData();

                console.log("Enregistré");
            }

        } catch (error) {
            console.error(error);
        }

    });

}


// ==========================
// ANIMATE COUNTER
// ==========================
function animateCounter(element, target, duration = 800) {

    if (!element) return;

    clearInterval(element._counter);

    let start = 0;
    const stepTime = 10;
    const steps = duration / stepTime;
    const increment = target / steps;

    element._counter = setInterval(() => {

        start += increment;

        if (start >= target) {
            start = target;
            clearInterval(element._counter);
        }

        element.textContent = `${Math.floor(start)} FCFA`;

    }, stepTime);
}


// ==========================
// REFRESH DATA
// ==========================
async function refreshData() {

    try {

        const response = await fetch(`/journal-stats/?date=${selectedDate}`, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        if (!response.ok) return;

        const data = await response.json();

        const revenus = document.getElementById("total-revenus");
        const depenses = document.getElementById("total-depenses");
        const mobile = document.getElementById("total-mobile");
        const especes = document.getElementById("total-especes");

        if (revenus) animateCounter(revenus, data.total || 0);
        if (depenses) animateCounter(depenses, data.depenses || 0);
        if (mobile) animateCounter(mobile, data.mobile_money || 0);
        if (especes) animateCounter(especes, data.especes || 0);

    } catch (error) {
        console.error("refreshData error:", error);
    }
}

function countUp(element, target, duration = 900) {

    if (!element) return;

    let start = 0;
    const stepTime = 10;
    const steps = duration / stepTime;
    const increment = target / steps;

    let current = 0;

    const timer = setInterval(() => {

        current += increment;

        if (current >= target) {
            current = target;
            clearInterval(timer);
        }

        element.textContent = Math.floor(current).toLocaleString();
    }, stepTime);
}

function animateStats() {

    countUp(document.getElementById("total-revenus"), window.__TOTAL_REVENUS__ || 0);
    countUp(document.getElementById("total-depenses"), window.__TOTAL_DEPENSES__ || 0);
    countUp(document.getElementById("total-mobile"), window.__TOTAL_MOBILE__ || 0);
    countUp(document.getElementById("total-especes"), window.__TOTAL_ESPECES__ || 0);

}