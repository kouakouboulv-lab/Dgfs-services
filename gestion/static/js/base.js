document.addEventListener("DOMContentLoaded", () => {

    const loader = document.getElementById("loader");

    // =========================
    // LOADER
    // =========================

    if (!sessionStorage.getItem("firstLoadDone")) {

        sessionStorage.setItem("firstLoadDone", "true");

        setTimeout(() => {

            loader.classList.add("loader-hide");

            setTimeout(() => {
                loader.style.display = "none";
            }, 500);

        }, 3000);

    } else {

        loader.style.display = "none";

    }

    // =========================
    // LOADER LORS DES CLICS
    // =========================

    document.querySelectorAll(".nav-link, .navbar-brand").forEach(link => {

        link.addEventListener("click", () => {

            loader.style.display = "flex";
            loader.classList.remove("loader-hide");

        });

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