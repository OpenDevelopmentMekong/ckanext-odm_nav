document.addEventListener("DOMContentLoaded", function(event) {
    $(".locale-date").each(function(index){
        try {
            $(this).text(new Date($(this).data('date')).toLocaleDateString());
        } catch(error){
            console.error(error);
        }
    });
});
