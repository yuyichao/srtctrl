$(function () {
    $("#npoint-dialog").dialog({
        autoOpen: false,
        height: 200
    });
    $("#npoint-button").click(function () {
        var dialog = $("#npoint-dialog");
        if (dialog.dialog("isOpen")) {
            dialog.dialog("close");
        } else {
            dialog.dialog("open");
        }
        return false;
    });
});
