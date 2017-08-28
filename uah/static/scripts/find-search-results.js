$("#search-bar").change(function() {
    let $keywords = $(this).val().toLowerCase();
    $(".inventory-item").each(function() {
        $(this).toggle(!$keywords.length || $(".item-name", this).text().toLowerCase().includes($keywords));
    });
});
