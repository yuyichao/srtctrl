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
            return $('<input class="ui-widget-content ui-corner-all"/>');
        },
        open_file: function () {
            var input = $('<input class="ui-widget-content ui-corner-all"/>');
            input.click(function () {
                var $this = $(this);
                $this.val($.open_file($this.val()));
            });
            return input;
        },
        save_file: function () {
            var input = $('<input class="ui-widget-content ui-corner-all"/>');
            input.click(function () {
                var $this = $(this);
                $this.val($.save_file($this.val()));
            });
            return input;
        }
    };
    $.extend({
        input_dialog: function (ele, entries, buttons) {
            ele = $(ele);
        }
    });
})();
