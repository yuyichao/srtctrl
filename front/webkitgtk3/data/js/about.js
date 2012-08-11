$(function () {
    var about_dialog_tabs = $("#about-dialog-tabs");
    var tabs = {
        copy: $("#about-dialog-tab-copy"),
        desc: $("#about-dialog-tab-description")
    };
    about_dialog_tabs.tabs();
    add_dialog($("#about-button"), $("#about-dialog"), true);
    $(".about-tab-buttons").click(function () {
        $("#about-dialog-tabs").resize();
    });
    $("#about-dialog-tabs").resize(function () {
        for (var tname in tabs) {
            var height;
            height = (about_dialog_tabs.height()
                      - tabs[tname].position().top
                      - tabs[tname].outerHeight()
                      + tabs[tname].height());
            tabs[tname].height(height);
        }
    });
});
