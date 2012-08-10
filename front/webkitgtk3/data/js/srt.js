function escapeHTML(str) {
    return $('<div/>').text(str).html();
};
$(function () {
    $(".header-button").button();
    $("#about-dialog").dialog({
        autoOpen: false,
        // show: "blind",
        // hide: "explode",
        height: 140,
        modal: true
    });
    $("#about-button").click(function () {
        $("#about-dialog").dialog("open");
        return false;
    });

    Back.Source.connect("event::move", function (src, evt, div) {
        div.text(evt.toString());
    }, $('#mvevent'));
    $('#quit-button').click(function (ev) {
        Back.Source.quit();
        return false;
    });
});
