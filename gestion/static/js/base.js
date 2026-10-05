document.addEventListener("DOMContentLoaded", () => {

    const loader = document.getElementById("loader");

    // =========================
    // LOADER
    // =========================

    if (loader) loader.style.display = "none";

    // =========================
    // LOADER LORS DES CLICS
    // =========================

    document.querySelectorAll(".nav-link, .navbar-brand").forEach(link => {

        if (link.classList.contains("active")) link.setAttribute("aria-current", "page");

    });

    // Make calendar cells usable with the keyboard, including refreshed cells.
    document.addEventListener("keydown", (event) => {
        const day = event.target.closest(".calendar-click[role='button']");
        if (day && (event.key === "Enter" || event.key === " ")) {
            event.preventDefault();
            day.click();
        }
    });

    // =========================
    // DECONNEXION APRES 1 HEURE D'INACTIVITE
    // =========================

    let inactivityTimer;

    function logoutUser() {
        window.location.href = "/accounts/logout/";
    }

    function resetInactivityTimer() {

        clearTimeout(inactivityTimer);

        inactivityTimer = setTimeout(logoutUser, 3600000); // 1 heure

    }

    [
        "mousemove",
        "mousedown",
        "click",
        "scroll",
        "keypress",
        "touchstart"
    ].forEach(event => {

        document.addEventListener(event, resetInactivityTimer, true);

    });

    resetInactivityTimer();

});
