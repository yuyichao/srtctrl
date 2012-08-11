$(function () {
    var about_dialog_tabs = $("#about-dialog-tabs");
    var about_dialog = $("#about-dialog");
    var about_dialog_content = $("#about-dialog-content");
    var tabs = {
        copy: $("#about-dialog-tab-copy"),
        desc: $("#about-dialog-tab-description")
    };
    about_dialog_tabs.tabs();
    add_dialog($("#about-button"), about_dialog, true);
    $(".about-tab-buttons").click(function () {
        about_dialog.resize();
    });
    about_dialog.resize(function () {
        about_dialog_content.outerHeight(
            $(this).height()
        );
        return false;
    });
    about_dialog_tabs.resize(function () {
        for (var tname in tabs) {
            var height;
            height = (about_dialog_tabs.height()
                      - tabs[tname].position().top
                      - tabs[tname].outerHeight()
                      + tabs[tname].height());
            tabs[tname].height(height);
            console.log(tname);
            console.log(height);
        }
        return false;
    });
});
