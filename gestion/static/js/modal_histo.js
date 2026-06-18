document.addEventListener("DOMContentLoaded", () => {


    const modal = document.getElementById("dayModal");
    const modalTitle = document.getElementById("modalTitle");
    const modalBody = document.getElementById("modalBody");


    if(!modal) return;



    // ==========================
    // OUVRIR MODAL
    // ==========================

    window.openModal = function(title, content){

        modal.classList.add("show");

        modalTitle.innerHTML = title;

        modalBody.innerHTML = content;

        document.body.style.overflow = "hidden";

    };



    // ==========================
    // FERMER MODAL
    // ==========================

    window.closeModal = function(){

        modal.classList.remove("show");

        document.body.style.overflow = "";

    };



    // ==========================
    // FERMETURE OVERLAY
    // ==========================

    window.overlayClose = function(event){

        if(event.target.id === "dayModal"){

            closeModal();

        }

    };



    // ==========================
    // ESC POUR FERMER
    // ==========================

    document.addEventListener("keydown", (e)=>{

        if(e.key === "Escape"){

            closeModal();

        }

    });





    // ==========================
    // CLICK JOUR CALENDRIER
    // (fonctionne après AJAX)
    // ==========================

    document.addEventListener("click", async (e)=>{


        const day = e.target.closest(".calendar-click");


        if(!day) return;



        const date = day.dataset.date;


        if(!date) return;



        // sélection jour

        document.querySelectorAll(".calendar-click")
        .forEach(el=>{

            el.classList.remove("selected");

        });



        day.classList.add("selected");




        openModal(

            `📅 ${date}`,

            `
            <div class="text-center py-4">
                Chargement...
            </div>
            `

        );




        try{


            const response = await fetch(
                `/journal-details/?date=${date}`
            );



            const data = await response.json();




            let html = `


            <div class="day-kpis">


                <div class="day-kpi">

                    <small>💰 Revenus</small>

                    <strong>
                        ${data.total_revenu || 0} FCFA
                    </strong>

                </div>




                <div class="day-kpi">

                    <small>📱 Mobile Money</small>

                    <strong>
                        ${data.total_mobile || 0} FCFA
                    </strong>

                </div>





                <div class="day-kpi">

                    <small>💵 Espèces</small>

                    <strong>
                        ${data.total_cash || 0} FCFA
                    </strong>

                </div>





                <div class="day-kpi">

                    <small>💸 Dépenses</small>

                    <strong>
                        ${data.total_depense || 0} FCFA
                    </strong>

                </div>


            </div>


            `;




            if(!data.activites || data.activites.length === 0){



                html += `

                <div class="text-center text-muted py-4">

                    Aucune activité enregistrée ce jour.

                </div>

                `;



            }else{



                html += `

                <div class="activities-list">

                `;



                data.activites.forEach(a=>{


                    html += `


                    <div class="modal-item">


                        <div class="modal-item-header">


                            <div class="modal-client">

                                👤 ${a.client}

                            </div>



                            <div class="modal-total">

                                ${a.montant} FCFA

                            </div>


                        </div>




                        <div class="modal-service">

                            ${a.service}

                        </div>



                    </div>


                    `;


                });



                html += `</div>`;

            }




            modalBody.innerHTML = html;



        }catch(error){



            console.error(error);



            modalBody.innerHTML = `


            <div class="text-center text-danger py-4">

                ❌ Impossible de charger les données.

            </div>


            `;


        }



    });



});