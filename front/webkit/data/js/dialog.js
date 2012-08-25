(function () {
    var dialog_list = [];
    function close_except(id) {
        var dialog;
        for (var i in dialog_list) {
            if (i == id)
                continue;
            dialog = dialog_list[i].dialog;
            if (dialog.dialog("isOpen"))
                dialog.dialog("close");
        }
    };
    $.extend({
        add_dialog: function (button, dialog, option) {
            var id = dialog_list.length;
            var autoclose_timeout = null;
            var setting = $.extend({}, {
                modal: false,
                open: null,
                background: "white"
            }, option);
            dialog_list.push({
                button: button,
                dialog: dialog
            });
            function clear_timeout() {
                if (autoclose_timeout) {
                    clearTimeout(autoclose_timeout);
                    autoclose_timeout = null;
                }
            }
            dialog.dialog({
                autoOpen: false,
                modal: setting.modal,
                show: "blind",
                hide: "highlight",
                open: function () {
                    clear_timeout();
                    autoclose_timeout = setTimeout(function () {
                        dialog.dialog('close');
                    }, 600000);
                    SrtCall('ref', 1);
                    close_except(id);
                    if (setting.open)
                        setting.open();
                },
                close: function () {
                    clear_timeout();
                    SrtCall('ref', -1);
                }
            }).parent().css({
                position: "absolute",
                background: setting.background
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
            if (setting.modal) {
                dialog.parent().bind("clickoutside", function () {
                    if (dialog.dialog("isOpen"))
                        dialog.dialog("close");
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
        }
    });
})();
(function () {
    $.fn.extend({
        popup: function (button, option) {
            var ele = $(this).detach();
            var content = $("<div></div>");
            var dialog = $("<div></div>");
            var setting = $.extend({}, {
                modal: false,
                open: null,
                title: ele.attr("title"),
                background: "white"
            }, option);
            dialog.attr({
                title: setting.title
            });
            dialog.css({
                display: "none",
                float: "left"
            });
            dialog.addClass("srt-popup-dialog");
            content.addClass("srt-popup-dialog-content");
            dialog.append(content);
            content.append(ele);
            function resize_dialog() {
                content.outerHeight(dialog.height());
                ele.outerHeight(content.height());
            }
            dialog.resize(resize_dialog);
            $("body").append(dialog);
            $.add_dialog($(button), dialog, {
                modal: setting.modal,
                open: setting.open,
                background: setting.background
            });
            return dialog;
        }
    });
})();
