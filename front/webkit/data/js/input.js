(function () {
    function check_form(res) {
        var kwargs = {};
        for (var key in res) {
            if (res[key] === null)
                continue;
            kwargs[key] = res[key];
        }
        return kwargs;
    }
    $.extend({
        open_file: function (cur_file) {
            return SrtCall('file', {
                cur_file: cur_file,
                save: false
            });
        },
        save_file: function (cur_file) {
            return SrtCall('file', {
                cur_file: cur_file,
                save: true
            });
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
                    var val = input.val();
                    return val ? val : null;
                }
            };
        },
        boolean: function () {
            var widget = $('<div></div>');
            var input = $('<input type="checkbox"/>').css({
                float: 'left'
            });
            widget.append(input);
            return {
                widget: widget,
                val: function (a) {
                    if (arguments.length)
                        return input.prop('checked', a);
                    return input.prop('checked');
                }
            };
        },
        number: function (option) {
            var setting = $.extend({}, option);
            var input = $(
                '<input type="number" class="ui-widget-content ui-corner-all"/>'
            ).attr({
                min: setting.min,
                max: setting.max
            });
            return {
                widget: input,
                val: function (a) {
                    if (arguments.length)
                        return input.val(a);
                    var val = input.val();
                    if (!val)
                        return null;
                    val = parseFloat(val);
                    if (!isFinite(val))
                        return null;
                    if (val < setting.min)
                        return setting.min;
                    if (val > setting.max)
                        return setting.max;
                    return val;
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
                val: function (a) {
                    if (arguments.length)
                        return input.val(a);
                    var val = input.val();
                    return val ? val : null;
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
                val: function (a) {
                    if (arguments.length)
                        return input.val(a);
                    var val = input.val();
                    return val ? val : null;
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
    function set_to_default(ui_entry) {
        ui_entry.val(ui_entry.default);
    }
    function set_all_default(ui_entries) {
        for (var e_i in ui_entries) {
            set_to_default(ui_entries[e_i]);
        }
    }
    function save_to_srtstate(ui_entry) {
        SrtState(ui_entry.srt_state, ui_entry.val());
    }
    function save_all(ui_entries) {
        for (var e_i in ui_entries) {
            save_to_srtstate(ui_entries[e_i]);
        }
    }
    function recover_srtstate(ui_entry) {
        var val = SrtState(ui_entry.srt_state);
        if (val === undefined) {
            set_to_default(ui_entry);
            return;
        }
        ui_entry.val(val);
    }
    var id_count = 0;
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
                id: (++id_count).toFixed()
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
                    advanced: entry.advanced,
                    'default': entry.default,
                    srt_state: '_input_dialog_' + setting.id + '_' + entry.name
                }, new_input(entry.type, entry.option));
                recover_srtstate(ui_entry);
                if (entry.advanced) {
                    has_advanced = true;
                    ui_entry.block.css({display: "none"});
                    ui_entry.label.css({"font-weight": "bold"});
                }
                if (entry.tooltip)
                    ui_entry.block.attr({title: entry.tooltip});
                ui_entry.block.addClass("srt-entry-line");
                ui_entry.block.addClass("ui-helper-clearfix");
                ui_entry.label.css({float: "left"});
                ui_entry.widget.css({float: "right"});
                ui_entry.block.append(ui_entry.label);
                ui_entry.block.append(ui_entry.widget);
                ui_entries.push(ui_entry);
                ui_value_block.append(ui_entry.block);
            }
            var advanced_id;
            if (has_advanced) {
                function toggle_advance(show) {
                    if (!show) {
                        $(ui_buttons[advanced_id])
                            .button("option", "label", "Show More");
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
                        $(ui_buttons[advanced_id])
                            .button("option", "label", "Show Less");
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
                advanced_id = buttons.length;
                buttons.push({
                    label: "Show More",
                    autoclose: false,
                    callback: function () {
                        toggle_advance(!advanced_show);
                    }
                });
            }
            buttons.push({
                label: "Set To Default",
                autoclose: false,
                callback: function () {
                    set_all_default(ui_entries);
                    if (has_advanced)
                        toggle_advance(false);
                }
            });
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
                        res = check_form(res);
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
                title: setting.title,
                open: function () {
                    if (has_advanced)
                        toggle_advance(false);
                },
                close: function () {
                    save_all(ui_entries);
                }
            });
            return dialog;
        }
    });
})();
