(function () {
    function max_z_index() {
        var max_z = 0;
        $('*').each(function () {
            var cur = parseInt($(this).css("z-index"));
            max_z = cur > max_z ? cur : max_z;
        });
        return max_z;
    }
    function show_menu(offset) {
        var menu = $(this);
        var width;
        menu.outerHeight(($(document).height() - offset.top) * .8);
        menu.css({
            visibility: "visible",
            display: "none"
        });
        menu.offset({
            left: 0,
            top: 0
        });
        menu.css({
            visibility: "hidden",
            display: "block"
        });
        width = menu.outerWidth();
        offset = {
            left: Math.min(offset.left, $(document).width() - width),
            top: offset.top
        };
        menu.offset(offset);
        menu.css({
            visibility: "visible",
            display: "none"
        });
        menu.css({"z-index": max_z_index() + 1});
        menu.fadeIn(100);
    }
    function clear_timeout(ui_entry) {
        if (ui_entry.close_timeout) {
            clearTimeout(ui_entry.close_timeout);
            ui_entry.close_timeout = null;
        }
        if (ui_entry.autoclose_timeout) {
            clearTimeout(ui_entry.close_timeout);
            ui_entry.close_timeout = null;
        }
    }
    function close_menu(ui_entry) {
        clear_timeout(ui_entry);
        if (ui_entry.open) {
            SrtCall('ref', -1);
        }
        ui_entry.open = false;
        ui_entry.submenu.fadeOut(100);
    }
    function open_menu(ui_entry) {
        clear_timeout(ui_entry);
        ui_entry.autoclose_timeout = setTimeout(function () {
            close_menu(ui_entry);
        }, 300000);
        if (ui_entry.open)
            return false;
        SrtCall('ref', 1);
        ui_entry.open = true;
        offset = ui_entry.button.offset();
        show_menu.call(ui_entry.submenu, {
            top: offset.top + ui_entry.button.outerHeight(),
            left: offset.left
        });
    }
    function menu_enter_leave(event) {
        var ui_entry = event.data.ui_entry;
        var offset;
        if (event.type == 'mouseleave') {
            ui_entry.close_timeout = setTimeout(function () {
                close_menu(ui_entry);
            }, 100);
        } else {
            open_menu(ui_entry);
        }
        return false;
    }
    $.extend({
        toolbar: function (entries) {
            var res;
            var toolbar = $('<div></div>');
            var ui_entries = [];
            for (var e_i in entries) {
                var entry = entries[e_i];
                var ui_entry = {
                    button: $('<button></button>').text(entry.label).attr({
                        id: entry.id
                    }),
                    id: entry.id
                };
                if ('submenu' in entry) {
                    ui_entry.submenu = $.menu(entry.submenu);
                    ui_entry.submenu.css({
                        display: 'none'
                    });
                    ui_entry.open = false;
                    ui_entry.close_timeout = null;
                    $('body').append(ui_entry.submenu);
                    ui_entry.button.bind("mouseenter mouseleave", {
                        ui_entry: ui_entry
                    }, menu_enter_leave);
                    ui_entry.submenu.children().bind("mouseenter mouseleave", {
                        ui_entry: ui_entry
                    }, menu_enter_leave);
                    ui_entry.submenu.find("*").click({
                        ui_entry: ui_entry
                    }, function (event) {
                        var ui_entry = event.data.ui_entry;
                        close_menu(ui_entry);
                        return true;
                    });
                }
                toolbar.append(ui_entry.button);
                ui_entries.push(ui_entry);
            }
            return toolbar.buttonset();
        }
    });
})();
