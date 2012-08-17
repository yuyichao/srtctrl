(function () {
    $.extend({
        open_file: function (cur_file) {
            var sel_file = null;
            var fc_dlg = UI.Gtk.FileChooserDialog(
                'Open ... ', null,
                UI.Gtk.FileChooserAction.OPEN,
                [UI.Gtk.STOCK_OPEN, UI.Gtk.ResponseType.OK,
                 UI.Gtk.STOCK_CLEAR, UI.Gtk.ResponseType.CLOSE,
                 UI.Gtk.STOCK_CANCEL, UI.Gtk.ResponseType.CANCEL]);
            fc_dlg.set_default_response(UI.Gtk.ResponseType.OK);
            if (cur_file)
                fc_dlg.set_filename(cur_file);
            resp = fc_dlg.run();
            if (resp == UI.Gtk.ResponseType.OK) {
                sel_file =  fc_dlg.get_filename();
            } else if (resp == UI.Gtk.ResponseType.CANCEL) {
                sel_file = cur_file;
            }
            fc_dlg.destroy();
            return sel_file;
        },
        save_file: function (cur_file) {
            var sel_file = null;
            var fc_dlg = UI.Gtk.FileChooserDialog(
                'Save ... ', null,
                UI.Gtk.FileChooserAction.SAVE,
                [UI.Gtk.STOCK_SAVE, UI.Gtk.ResponseType.OK,
                 UI.Gtk.STOCK_CLEAR, UI.Gtk.ResponseType.CLOSE,
                 UI.Gtk.STOCK_CANCEL, UI.Gtk.ResponseType.CANCEL]);
            fc_dlg.set_default_response(UI.Gtk.ResponseType.OK);
            if (cur_file)
                fc_dlg.set_filename(cur_file);
            resp = fc_dlg.run();
            if (resp == UI.Gtk.ResponseType.OK) {
                sel_file =  fc_dlg.get_filename();
            } else if (resp == UI.Gtk.ResponseType.CANCEL) {
                sel_file = cur_file;
            }
            fc_dlg.destroy();
            return sel_file;
        }
    });
    var input_types = {
        text: function () {
            var input = $('<input class="ui-widget-content ui-corner-all"/>');
            return {
                widget: input,
                val: function (a) {
                    if (arguments.length)
                        return input.val(a);
                    return input.val();
                }
            };
        },
        open_file: function () {
            var input = $('<input class="ui-widget-content ui-corner-all"/>');
            input.click(function () {
                input.val($.open_file(input.val()));
            });
            return {
                widget: input,
                val: function () {
                    if (arguments.length)
                        return input.val(a);
                    return input.val();
                }
            };
        },
        save_file: function () {
            var input = $('<input class="ui-widget-content ui-corner-all"/>');
            input.click(function () {
                input.val($.save_file(input.val()));
            });
            return {
                widget: input,
                val: function () {
                    if (arguments.length)
                        return input.val(a);
                    return input.val();
                }
            };
        }
    };
    function new_input(type, option) {
        if (type in input_types)
            return input_types[type](option);
        return input_types.text(option);
    }
    function max_label_width(ui_entries) {
        var max_width = 0;
        for (var i in ui_entries)
            max_width = Math.max(max_width, ui_entries[i].label.outerWidth());
        return max_width;
    }
    $.extend({
        input_dialog: function (dialog_button, entries, buttons, option) {
            var dialog;
            var advanced_show = false;
            var has_advanced = false;
            var ui_entries = [];
            var ui_buttons = [];
            var ui_content = $('<div></div>');
            var ui_button_block = $('<div></div>');
            var ui_value_block = $('<div></div>');
            var setting = $.extend({}, {
                title: "",
            }, option);
            ui_button_block.addClass("srt-input-buttons");
            ui_button_block.addClass("ui-helper-clearfix");
            ui_value_block.addClass("srt-input-values");
            ui_content.addClass("srt-input-content");
            for (var e_i in entries) {
                var entry = entries[e_i];
                var ui_entry = $.extend({
                    name: entry.name,
                    label: $('<div></div>').text(entry.label),
                    block: $('<div></div>'),
                    type: entry.type,
                    option: entry.option,
                    advanced: entry.advanced
                }, new_input(entry.type, entry.option));
                if (entry.default) {
                    ui_entry.val(entry.default);
                }
                if (entry.advanced) {
                    has_advanced = true;
                    ui_entry.block.css({display: "none"});
                    ui_entry.label.css({"font-weight": "bold"});
                }
                ui_entry.block.addClass("srt-entry-line");
                ui_entry.block.addClass("ui-helper-clearfix");
                ui_entry.label.css({float: "left"});
                ui_entry.widget.css({float: "right"});
                ui_entry.block.append(ui_entry.label);
                ui_entry.block.append(ui_entry.widget);
                ui_entries.push(ui_entry);
                ui_value_block.append(ui_entry.block);
            }
            if (has_advanced) {
                buttons.push({
                    label: "Show More",
                    autoclose: false,
                    callback: function () {
                        if (advanced_show) {
                            $(this).button("option", "label", "Show More");
                            advanced_show = false;
                            for (var e_i in ui_entries) {
                                if (ui_entries[e_i].advanced) {
                                    ui_entries[e_i].block.css({
                                        display: "none"
                                    });
                                }
                            }
                            label_resize();
                        } else {
                            $(this).button("option", "label", "Hide Less");
                            advanced_show = true;
                            for (var e_i in ui_entries) {
                                if (ui_entries[e_i].advanced) {
                                    ui_entries[e_i].block.css({
                                        display: "block"
                                    });
                                }
                            }
                            label_resize();
                        }
                    }
                });
            }
            for (var b_i in buttons) {
                var button = $('<button></button>')
                    .text(buttons[b_i].label)
                    .button()
                    .click({
                        button: buttons[b_i]
                    }, function (evt) {
                        var button = evt.data.button;
                        var res = {};
                        for (var e_i in ui_entries) {
                            var entry = ui_entries[e_i];
                            res[entry.name] = entry.val();
                        }
                        if (button.callback) {
                            button.callback.call(this, res);
                        }
                        if (!("autoclose" in button) || button.autoclose) {
                            dialog.dialog("close");
                        }
                    })
                    .css({float: "right"});
                ui_buttons.push(button);
                ui_button_block.append(button);
            }
            ui_content.append(ui_value_block);
            ui_content.append(ui_button_block);
            ui_content.resize(function () {
                var content_width = ui_content.width();
                var content_height = ui_content.height();
                ui_value_block.outerWidth(content_width - 2);
                ui_button_block.outerWidth(content_width - 2);
                ui_value_block.outerHeight(content_height - 5
                                           - ui_button_block.outerHeight());
            });
            ui_value_block.resize(function () {
                var value_width = ui_value_block.width();
                var label_width = max_label_width(ui_entries);
                for (var i in ui_entries) {
                    ui_entries[i].block.outerWidth(value_width - 2);
                    ui_entries[i].widget.outerWidth(ui_entries[i].block.width()
                                                    - 10 - label_width);
                }
            });
            function label_resize() {
                var label_width = max_label_width(ui_entries);
                for (var i in ui_entries) {
                    ui_entries[i].widget.outerWidth(ui_entries[i].block.width()
                                                    - 10 - label_width);
                }
            }
            for (var i in ui_entries) {
                ui_entries[i].label.resize(label_resize);
            }
            dialog = ui_content.popup(dialog_button, {
                background: "lightCyan",
                title: setting.title
            });
            return dialog;
        }
    });
})();
