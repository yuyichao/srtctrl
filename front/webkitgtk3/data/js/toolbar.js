(function () {
    function show_menu(offset) {
        var menu = $(this);
        var width;
        menu.outerHeight(($(document).height() - offset.top) * .8);
        menu.offset({
            left: 0,
            top: 0
        });
        menu.css({
            visibility: "hidden",
            display: "block"
        });
        width = menu.outerWidth();
        offset.left = Math.min(offset.left, $(document).width() - width);
        menu.offset(offset);
    }
    $.extend({
        toolbar: function (entries) {
            var toolbar = $('<div></div>');
            var ui_entries = [];
            for (var e_i in entries) {
                var entry = entries[e_i];
                var ui_entry = {
                    button: $('<button></button>').text(entry.label).attr({
                        id: entry.id
                    }),
                };
                if ('submenu' in entry) {
                    ui_entry.submenu = $.menu(entry.submenu);
                    ui_entry.submenu.css({
                        display: 'none'
                    });
                    $('body').append(ui_entry.submenu);
                    ui_entry.button.bind("mouseenter mouseleave", {
                        ui_entry: ui_entry
                    }, function (event) {
                        var ui_entry = event.data.ui_entry;
                        var offset;
                        if (event.type == 'mouseleave') {
                            ui_entry.submenu.fadeOut(100);
                            return false;
                        }
                        offset = ui_entry.button.offset();
                        show_menu.call(ui_entry.submenu, {
                            top: offset.top + ui_entry.button.outerHeight(),
                            left: offset.left
                        });
                        return false;
                    });
                }
                buttonset.append(ui_entry.li.append(ui_entry.button));
            }
        }
    });
})();
