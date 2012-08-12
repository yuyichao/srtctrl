$(function () {
    var about_dialog_tabs = $("#about-dialog-tabs");
    var about_dialog = $("#about-dialog");
    var about_dialog_content = $("#about-dialog-content");
    var tabs = {
        copy: $("#about-dialog-tab-copy"),
        desc: $("#about-dialog-tab-description")
    };
    about_dialog_tabs.tabs({
        fx: {
            opacity: "toggle",
            duration: 200
        }
    });
    add_dialog($("#about-button"), about_dialog, true);
    function resize_about_dialog() {
        about_dialog_content.outerHeight(
            about_dialog.height()
        );
        about_dialog_tabs.outerHeight(
            about_dialog_content.height()
        );
        for (var tname in tabs) {
            var height;
            height = (about_dialog_tabs.height()
                      - $("#about-dialog-tabs-bar").outerHeight());
            tabs[tname].height(height);
        }
        return false;
    }
    $(".about-tab-buttons").click(function () {
        resize_about_dialog();
    });
    about_dialog.resize(resize_about_dialog);
});
