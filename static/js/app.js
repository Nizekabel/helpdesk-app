// Attend que le document soit prêt avant de chercher les éléments de la page.
$(function () {
    // Demande une confirmation avant d'envoyer un formulaire destructif.
    $(document).on("submit", "form[data-confirm]", function (event) {
        if (!window.confirm($(this).attr("data-confirm"))) {
            event.preventDefault();
        }
    });

    // Récupère les cartes ; le script peut aussi être chargé sur les autres pages.
    const $ticketItems = $(".ticket-item");

    if (!$ticketItems.length) {
        return;
    }

    // Mémorise les champs et les retours visuels utilisés pendant le filtrage.
    const $search = $("#ticketSearch");
    const $status = $("#ticketStatus");
    const $priority = $("#ticketPriority");
    const $results = $("#ticketResults");
    const $emptyState = $("#ticketEmptyState");

    // Ignore les différences de casse et d'accents dans la recherche française.
    function normalizeSearchValue(value) {
        return value
            .toLocaleLowerCase("fr")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }

    // Combine le texte recherché, le statut et la priorité pour afficher les cartes correspondantes.
    function filterTickets() {
        const query = normalizeSearchValue($.trim($search.val()));
        const selectedStatus = $status.val();
        const selectedPriority = $priority.val();
        let visibleCount = 0;

        // Teste chaque carte et conserve le nombre de tickets visibles pour le compteur.
        $ticketItems.each(function () {
            const $ticket = $(this);
            const searchableText = normalizeSearchValue($ticket.text());
            const matchesQuery = !query || searchableText.includes(query);
            const matchesStatus = !selectedStatus || $ticket.data("status") === selectedStatus;
            const matchesPriority = !selectedPriority || $ticket.data("priority") === selectedPriority;
            const isVisible = matchesQuery && matchesStatus && matchesPriority;

            $ticket.toggleClass("d-none", !isVisible);
            visibleCount += isVisible ? 1 : 0;
        });

        // Met à jour le compteur accessible et signale quand aucun résultat ne correspond.
        $results.text(
            visibleCount + (visibleCount === 1 ? " ticket affiché" : " tickets affichés") +
            " sur " + $ticketItems.length
        );
        $emptyState.toggleClass("d-none", visibleCount !== 0);
    }

    // Actualise les résultats à chaque saisie et à chaque changement de filtre.
    $search.on("input", filterTickets);
    $status.add($priority).on("change", filterTickets);

    // Délègue le clic au conteneur pour gérer les boutons de détail des cartes.
    $("#ticketList").on("click", ".ticket-details-toggle", function () {
        const $button = $(this);
        const isExpanded = $button.attr("aria-expanded") === "true";
        const details = document.getElementById($button.attr("aria-controls"));

        // Ignore le bouton si son identifiant ne correspond à aucun panneau de détails.
        if (!details) {
            return;
        }

        // Synchronise l'état accessible, le libellé et les descriptions visibles.
        $button.attr("aria-expanded", String(!isExpanded));
        $button.text(
            isExpanded ? $button.data("show-label") : $button.data("hide-label")
        );
        $button.closest(".ticket-card").find(".ticket-description").toggleClass("d-none", !isExpanded);
        $(details).toggleClass("d-none", isExpanded);
    });

    // Affiche le nombre initial de résultats dès le chargement de la page.
    filterTickets();
});