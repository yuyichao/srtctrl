function srt_cal_size() {
    var body = $(window);
    var header = $("#header");
    var content = $("#content");
    var footer = $("#footer");
    var full_height = body.height();
    var head_height = header.height();
    var footer_height = footer.height();
    content.height(full_height - head_height - footer_height);
}

$(function () {
    srt_cal_size();
    $("#footer").resize(srt_cal_size);
    $("#header").resize(srt_cal_size);
    $(window).resize(srt_cal_size);
    $(".header-button").button();
    $("button").button();
    Back.Source.connect("event::move", function (src, evt, div) {
        div.text(evt.az + ", " + evt.el);
    }, $('#mvevent'));
    $('#quit-button').click(function (ev) {
        Back.Source.quit();
        return false;
    });
});

var add_dialog = (function () {
    var _dialog_list = [];
    var _close_except = function (id) {
        for (var i in _dialog_list) {
            var dialog;
            if (i == id) {
                continue;
            }
            dialog = _dialog_list[i].dialog;
            if (dialog.dialog("isOpen"))
                dialog.dialog("close");
        }
    };
    var _add_dialog = function (button, dialog, modal) {
        var id = _dialog_list.length;
        _dialog_list.push({
            button: button,
            dialog: dialog
        });
        dialog.dialog({
            autoOpen: false,
            modal: modal,
            open: function () {
                _close_except(id);
            }
        }).bind("clickoutside", function () {
            if (dialog.dialog("isOpen"))
                dialog.dialog("close");
        });
        button.click(function () {
            if (dialog.dialog("isOpen")) {
                dialog.dialog("close");
            } else {
                dialog.dialog("open");
            }
            return false;
        });
    };
    return _add_dialog;
})();
