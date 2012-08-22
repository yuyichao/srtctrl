$(function () {
    var about_dialog_tabs = $("#about-dialog-tabs");
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
    about_dialog_tabs.popup("#about-button", {
        modal: true
    });
    function resize_about_dialog() {
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
    about_dialog_tabs.resize(resize_about_dialog);
});
