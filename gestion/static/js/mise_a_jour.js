document.addEventListener("DOMContentLoaded", () => {

    // ================= CSRF =================
    function getCookie(name) {
        let cookieValue = null;

        document.cookie.split(";").forEach(c => {
            c = c.trim();
            if (c.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(
                    c.substring(name.length + 1)
                );
            }
        });

        return cookieValue;
    }

    // ================= DATE =================
    function getSelectedDate() {
        const dateInput = document.querySelector(".date-form input[type='date']");
        return dateInput ? dateInput.value : "";
    }

    // ================= TOAST =================
    function showToast(message, type = "success") {

        const toast = document.getElementById("toast");
        if (!toast) return;

        toast.className = `toast ${type}`;
        toast.textContent = message;

        toast.classList.add("show");

        clearTimeout(toast.timeout);

        toast.timeout = setTimeout(() => {
            toast.classList.remove("show");
        }, 3500);
    }
    // ================= VALIDATION =================
    function validateDateOrBlock() {
        const date = getSelectedDate();

        if (!date) {
            showToast("❌ Veuillez sélectionner une date");
            "error"
            return false;
        }

        return true;
    }

    // ================= AJAX GLOBAL =================
    document.addEventListener("submit", async (e) => {

        const form = e.target;
        if (!form.classList.contains("ajax-form")) return;

        e.preventDefault();

        const formData = new FormData(form);
        const action = formData.get("action");

        if (["add_activity", "add_depense", "save_paiement", "save_final"].includes(action)) {
            if (!validateDateOrBlock()) return;
        }

        try {
            const response = await fetch(window.location.href, {
                method: "POST",
                credentials: "same-origin",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken")
                }
            });

            const data = await response.json();

            if (!data.success) {
                showServerError(data.error);
                return;
            }

            handleAction(form, formData, data, action);

        } catch (err) {
            console.error(err);
            showToast("❌ Erreur de connexion");
        }
    });

    // ================= ERREURS =================
    function showServerError(error) {
        const map = {
            no_date: "❌ Sélectionnez une date",
            prix_unitaire_invalid: "❌ Prix invalide",
            montant_invalide: "❌ Montant invalide",
            empty_journal: "❌ Aucune donnée à enregistrer",
            invalid_date: "❌ Date invalide"
        };

        showToast(map[error] || "❌ Opération impossible");
    }

    // ================= ROUTER =================
    function handleAction(form, formData, data, action) {

        if (action === "add_activity") {
            addActivity(form, formData, data);
            refreshAll();
        }

        else if (action === "add_depense") {
            addDepense(form, formData, data);
            refreshAll();
        }

        else if (action === "delete_activity") {
            const tr = form.closest("tr");

            animateRemove(tr, () => {
                tr.remove();
                refreshAll();
            });
        }

        else if (action === "delete_depense") {
            const div = form.closest(".depense-item");

            animateRemove(div, () => {
                div.remove();
                refreshAll();
            });
        }

        else if (action === "save_paiement") {
            resetPaiementForm();
            refreshAll();
            showToast("✔ Paiements enregistrés");
        }

        else if (action === "save_final") {

            // 1. reset UI local
            resetPage();

            // 2. refresh depuis le serveur (source unique de vérité)
            refreshAll();

            // 3. reset date aussi (important pour éviter état bloqué)
            const dateInput = document.getElementById("journal-date");
            if (dateInput) dateInput.value = "";

            showToast("✔ Enregistrement terminé");
        }
    }

    // ================= RESET PAGE =================
    function resetPage() {

        clearUI();

        refreshKPI({
            total_activites: 0,
            total_depenses: 0,
            benefice: 0,
            mobile_money: 0,
            especes: 0
        });

        const activityForm = document.getElementById("activity-form");
        if (activityForm) activityForm.reset();

        resetPaiementForm();

        document.querySelectorAll(".total-line strong")
            .forEach(el => el.innerText = "0 FCFA");
    }

    // ================= RESET PAIEMENT =================
    function resetPaiementForm() {

        const fields = [
            "mobile_money",
            "especes"
        ];

        fields.forEach(name => {
            const input = document.querySelector(`input[name='${name}']`);
            if (input) input.value = "";
        });

    }

    // ================= CLEAR UI =================
    function clearUI() {
        const tbody = document.querySelector("#activiteTable tbody");
        const depenses = document.getElementById("depenses-container");

        if (tbody) tbody.innerHTML = "";
        if (depenses) depenses.innerHTML = "<div class='empty'>Aucune dépense</div>";
    }

    // ================= ANIMATION =================
    function animateRemove(el, callback) {
        if (!el) return;

        el.style.transition = "0.25s ease";
        el.style.opacity = "0";
        el.style.transform = "translateX(10px)";

        setTimeout(callback, 250);
    }

    // ================= ADD ACTIVITY =================
    function addActivity(form, formData, data) {

        const client = formData.get("client") || "Inconnu";
        const service = formData.get("service") || "";
        const prix = Number(formData.get("prix_unitaire") || 0);
        const qte = Number(formData.get("quantite") || 1);

        if (prix <= 0 || qte <= 0) {
            showToast("❌ Données invalides");
            return;
        }

        const tbody = document.querySelector("#activiteTable tbody");
        if (!tbody) return;

        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${client}</td>
            <td>${service}</td>
            <td>${prix * qte} FCFA</td>
            <td>
                <form method="POST" class="ajax-form">
                    <input type="hidden" name="action" value="delete_activity">
                    <input type="hidden" name="id" value="${data.data.id}">
                    <button type="submit">🗑</button>
                </form>
            </td>
        `;

        tbody.appendChild(tr);

        form.reset();
    }

    // ================= ADD DEPENSE =================
    function addDepense(form, formData, data) {

        const container = document.getElementById("depenses-container");
        if (!container) return;

        const empty = container.querySelector(".empty");
        if (empty) empty.remove();

        const motif = formData.get("motif") || "";
        const montant = Number(formData.get("montant_depense") || 0);

        if (montant <= 0) {
            showToast("❌ Montant invalide");
            return;
        }

        const div = document.createElement("div");
        div.className = "depense-item";

        div.innerHTML = `
            <span>${motif} : ${montant} FCFA</span>
            <form method="POST" class="ajax-form">
                <input type="hidden" name="action" value="delete_depense">
                <input type="hidden" name="id" value="${data.data.id}">
                <button type="submit">🗑</button>
            </form>
        `;

        container.appendChild(div);

        form.reset();
    }

    // ================= KPI =================
    function refreshKPI(data) {

        animateNumber(
            document.getElementById("total-activites"),
            data.nb_activites ?? 0
        );

        animateNumber(
            document.getElementById("total-depenses"),
            data.nb_depenses ?? 0
        );

        animateNumber(
            document.getElementById("mobile-money"),
            data.mobile_money ?? 0,
            " FCFA"
        );

        animateNumber(
            document.getElementById("especes"),
            data.especes ?? 0,
            " FCFA"
        );

        animateNumber(
            document.getElementById("benefice"),
            data.benefice ?? 0,
            " FCFA"
        );

        animateNumber(
            document.getElementById("total-activites-box"),
            data.total_activites ?? 0,
            " FCFA"
        );

        animateNumber(
            document.getElementById("total-depenses-box"),
            data.total_depenses ?? 0,
            " FCFA"
        );

        animateNumber(
            document.getElementById("benefice-box"),
            data.benefice ?? 0,
            " FCFA"
        );
    }

    // ================= KPI ANIMATION =================
    function animateNumber(el, target, suffix = "") {

        if (!el) return;

        const start = parseInt(el.dataset.value || 0);
        const end = parseInt(target || 0);

        const duration = 600;
        const startTime = performance.now();

        el.classList.add("kpi-update");

        function update(currentTime) {

            const progress = Math.min(
                (currentTime - startTime) / duration,
                1
            );

            const value = Math.floor(
                start + (end - start) * progress
            );

            el.textContent = value + suffix;

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                el.dataset.value = end;
                setTimeout(() => {
                    el.classList.remove("kpi-update");
                }, 250);
            }
        }

        requestAnimationFrame(update);
    }
    // ================= GLOBAL REFRESH (FIX IMPORTANT) =================
    function refreshAll() {

        const date = getSelectedDate(); // FIX customDate supprimé
        if (!date) return;

        fetch(`/api/mise-a-jour-stats/?date=${date}`)
            .then(res => res.json())
            .then(data => {

                refreshKPI(data);

                const tbody = document.querySelector("#activiteTable tbody");
                const container = document.getElementById("depenses-container");

                if (tbody) {
                    tbody.innerHTML = "";

                    (data.activites || []).forEach(a => {
                        const tr = document.createElement("tr");

                        tr.innerHTML = `
                            <td>${a.client}</td>
                            <td>${a.service}</td>
                            <td>${a.montant} FCFA</td>
                            <td>
                                <form method="POST" class="ajax-form">
                                    <input type="hidden" name="action" value="delete_activity">
                                    <input type="hidden" name="id" value="${a.id}">
                                    <button type="submit">🗑</button>
                                </form>
                            </td>
                        `;

                        tbody.appendChild(tr);
                    });
                }

                if (container) {
                    container.innerHTML = "";

                    (data.depenses || []).forEach(d => {
                        const div = document.createElement("div");
                        div.className = "depense-item";

                        div.innerHTML = `
                            <span>${d.motif} : ${d.montant} FCFA</span>
                            <form method="POST" class="ajax-form">
                                <input type="hidden" name="action" value="delete_depense">
                                <input type="hidden" name="id" value="${d.id}">
                                <button type="submit">🗑</button>
                            </form>
                        `;

                        container.appendChild(div);
                    });
                }
            })
            .catch(err => console.error(err));
    }

    
    $(document).ready(function(){

        $('#service').select2({

            placeholder: "Rechercher un service",

            allowClear: true,

            width: '100%'

        });

    });


});