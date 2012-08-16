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
    function add_dialog(button, dialog, modal) {
        var id = dialog_list.length;
        dialog_list.push({
            button: button,
            dialog: dialog
        });
        dialog.dialog({
            autoOpen: false,
            modal: modal,
            show: "blind",
            hide: "highlight",
            open: function () {
                close_except(id);
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
    };
    $.fn.extend({
        popup: function (button, option) {
            var setting = $.extend({}, {
                modal: false
            }, option);
            var ele = $(this).detach();
            var content = $("<div></div>");
            var dialog = $("<div></div>");
            dialog.attr({
                title: ele.attr("title")
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
            add_dialog($(button), dialog, setting.modal);
        }
    });
})();
