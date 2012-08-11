$(function () {
    var resize_timeout = false;
    $("button").button();
    $(".header-button").button();
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
    function resize_wrapper() {
        if (resize_timeout !== false) {
            srt_cal_size();
            clearTimeout(resize_timeout);
        }
        resize_timeout = setTimeout(srt_cal_size, 200);
    }
    $("#footer").resize(resize_wrapper);
    $("#header").resize(resize_wrapper);
    $(window).resize(resize_wrapper);
    $(window).keydown(function (ev) {
        if (ev.keyCode == 116) {
            window.top.location.reload();
            return false;
        }
        return true;
    });
    resize_wrapper();
    // Back.Source.connect("event::move", function (src, evt, div) {
    //     div.text(evt.az + ", " + evt.el);
    // }, $('#mvevent'));
    $('#quit-button').click(function (ev) {
        Back.Source.quit();
        return false;
    });
    $('#refresh-button').click(function (ev) {
        window.top.location.reload();
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
            show: "blind",
            hide: "highlight",
            open: function () {
                _close_except(id);
            }
        });
        function open() {
            if (!dialog.dialog("isOpen")) {
                dialog.dialog("option", {
                    height: $(window).height() * 2 / 3,
                    width: $(window).width() * 2 / 3
                });
                dialog.dialog("open");
            }
        }
        if (modal) {
            dialog.bind("clickoutside", function () {
                if (dialog.dialog("isOpen")) {
                    dialog.dialog("close");
                }
            });
        }
        button.click(function () {
            if (dialog.dialog("isOpen")) {
                dialog.dialog("close");
            } else {
                open();
            }
            return false;
        });
    };
    return _add_dialog;
})();
