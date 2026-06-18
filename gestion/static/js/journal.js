document.addEventListener("DOMContentLoaded", function(){


    sendForm("form-activity");

    sendForm("form-depense");

    sendForm("form-paiement");


});




// ==========================
// ENVOI AJAX FORMULAIRE
// ==========================

function sendForm(formId){


    const form = document.getElementById(formId);


    if(!form) return;



    form.addEventListener(
        "submit",
        async function(e){


            e.preventDefault();


            const formData = new FormData(this);



            try{


                const response = await fetch(
                    window.location.href,
                    {

                        method:"POST",

                        body:formData,


                        headers:{


                            "X-Requested-With":
                            "XMLHttpRequest"


                        }


                    }

                );



                const data = await response.json();



                console.log(
                    "Réponse serveur :",
                    data
                );



                if(data.success){


                    showToast(
                        "Enregistrement effectué avec succès ✅",
                        "success"
                    );

                    this.reset();

                    refreshTable();
                    refreshCalendar();

                    refreshData();

                }
                else{


                    showToast(
                        "Erreur! veillez renseigner PU ou Total",
                        "error"
                    );


                }



            }

            catch(error){


                console.error(
                    "Erreur AJAX :",
                    error
                );


                showToast(
                    "Erreur serveur",
                    "error"
                );


            }



        }

    );


}

// ==========================
// CREATION TOAST
// ==========================


function showToast(message,type="success"){



    const toast = document.createElement("div");



    toast.className =
        "toast-box " + type;



    toast.innerHTML = message;



    document.body.appendChild(toast);




    setTimeout(()=>{


        toast.classList.add(
            "hide"
        );


        setTimeout(()=>{


            toast.remove();


        },300);



    },2500);



}

// ==========================
// RAFRAICHIR LES DONNEES
// ==========================


async function refreshData(){


    try{


        const response = await fetch(
            "/journal-stats/",
            {

                headers:{


                    "X-Requested-With":
                    "XMLHttpRequest"


                }

            }

        );



        if(!response.ok)
            return;



        const data =
            await response.json();



        animateCounter(
            "total-revenus",
            data.total || 0
        );



        animateCounter(
            "total-depenses",
            data.depenses || 0
        );



        animateCounter(
            "total-mobile",
            data.mobile_money || 0
        );



        animateCounter(
            "total-especes",
            data.especes || 0
        );




    }

    catch(error){


        console.error(
            "Erreur refresh",
            error
        );


    }



}




// ==========================
// COMPTEUR ANIME
// ==========================


function animateCounter(id,value){


    const element =
        document.getElementById(id);



    if(!element)
        return;



    let start = 0;



    const duration = 700;



    const step =
        value / (duration / 20);



    clearInterval(
        element.timer
    );



    element.timer =
    setInterval(()=>{


        start += step;



        if(start >= value){


            start=value;


            clearInterval(
                element.timer
            );


        }



        element.textContent =
        Math.floor(start)
        .toLocaleString()
        +" FCFA";



    },20);



}

async function refreshTable(){

    try{


        const response = await fetch(
            window.location.href,
            {
                headers:{
                    "X-Requested-With":"XMLHttpRequest"
                }
            }
        );


        const html = await response.text();



        const parser = new DOMParser();


        const doc = parser.parseFromString(
            html,
            "text/html"
        );



        const nouveauTableau =
        doc.querySelector("#activity-table");



        const ancienTableau =
        document.querySelector("#activity-table");



        if(nouveauTableau && ancienTableau){

            ancienTableau.innerHTML =
            nouveauTableau.innerHTML;

        }



    }

    catch(error){

        console.error(
            "Erreur actualisation tableau :",
            error
        );

    }

}

// ==========================
// SUPPRESSION AJAX ACTIVITE
// ==========================

document.addEventListener(
    "click",
    async function(e){


        if(e.target.closest(".delete-activity")){


            e.preventDefault();



            const button =
            e.target.closest(".delete-activity");



            const url =
            button.dataset.url;



            if(!confirm("Supprimer cette activité ?"))
                return;




            try{


                const response =
                await fetch(
                    url,
                    {

                        method:"POST",

                        headers:{


                            "X-Requested-With":
                            "XMLHttpRequest",


                            "X-CSRFToken":
                            getCookie("csrftoken")


                        }


                    }

                );



                const data =
                await response.json();



                if(data.success){


                    showToast(
                        "Activité supprimée ✅"
                    );


                    refreshTable();

                    refreshCalendar();

                    refreshData();


                }



            }

            catch(error){


                console.error(
                    "Erreur suppression :",
                    error
                );


            }


        }


    }

);

// ==========================
// RAFRAICHIR CALENDRIER
// ==========================

async function refreshCalendar(){

    try{

        const response = await fetch(
            window.location.href,
            {
                headers:{
                    "X-Requested-With":"XMLHttpRequest"
                }
            }
        );


        const html = await response.text();


        const parser = new DOMParser();


        const doc = parser.parseFromString(
            html,
            "text/html"
        );


        const nouveauCalendrier =
        doc.querySelector("#calendar-container");


        const ancienCalendrier =
        document.querySelector("#calendar-container");



        if(nouveauCalendrier && ancienCalendrier){

            ancienCalendrier.innerHTML =
            nouveauCalendrier.innerHTML;


            reloadCalendarClick();

        }


    }

    catch(error){

        console.error(
            "Erreur actualisation calendrier :",
            error
        );

    }

}



// Récupérer CSRF Django

function getCookie(name){

    let cookieValue = null;


    if(document.cookie){

        const cookies =
        document.cookie.split(";");


        for(let cookie of cookies){


            cookie = cookie.trim();



            if(cookie.startsWith(name+"=")){


                cookieValue =
                decodeURIComponent(
                    cookie.substring(
                        name.length+1
                    )
                );

                break;

            }

        }

    }


    return cookieValue;

}


$(document).ready(function(){

    $('#service').select2({

        placeholder: "Rechercher un service",

        allowClear: true,

        width: '100%'

    });

});

