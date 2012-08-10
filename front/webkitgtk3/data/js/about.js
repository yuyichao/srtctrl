$(function () {
    $("#about-dialog").dialog({
        autoOpen: false,
        height: 200
    });
    $("#about-button").click(function () {
        var dialog = $("#about-dialog");
        if (dialog.dialog("isOpen")) {
            dialog.dialog("close");
        } else {
            dialog.dialog("open");
        }
        return false;
    });
});
