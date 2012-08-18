(function () {
    $.extend({
        menu: function (entries) {
            var menu = $('<div></div>')
                .addClass('ui-helper-clearfix')
                .addClass('srt-menu');
            var buttonset = $('<ul></ul>');
            var ui_entries = [];
            for (var e_i in entries) {
                var entry = $.extend({
                    text_align: "left"
                }, entries[e_i]);
                var ui_entry = {
                    li: $('<li></li>'),
                    button: $('<button></button>').text(entry.label).attr({
                        id: entry.id
                    }).css({
                        'text-align': entry.text_align
                    }),
                };
                buttonset.append(ui_entry.li.append(ui_entry.button));
            }
            buttonset.buttonset().menu();
            return menu.append(buttonset);
        }
    });
})();
