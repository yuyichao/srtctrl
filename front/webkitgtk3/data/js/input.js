(function () {
    $.extend({
        select_file: function () {
            var sel_file = null;
            var fc_dlg = UI.Gtk.FileChooserDialog(
                'Open ... ', null,
                UI.Gtk.FileChooserAction.OPEN,
                [UI.Gtk.STOCK_CANCEL, UI.Gtk.ResponseType.CANCEL,
                 UI.Gtk.STOCK_OPEN, UI.Gtk.ResponseType.OK]);
            fc_dlg.set_default_response(UI.Gtk.ResponseType.OK);
            resp = fc_dlg.run();
            if (resp == UI.Gtk.ResponseType.OK)
                sel_file =  fc_dlg.get_filename();
            fc_dlg.destroy();
            uri = UI.GLib.filename_to_uri(sel_file, null);
            return uri;
        }
    });
    var input_types = {
        text: function () {
            return $('<input class="ui-widget-content ui-corner-all"/>');
        },
        file: function () {
        }
    };
    $.extend({
        input_dialog: function (ele, entries, buttons) {
            ele = $(ele);
        }
    });
})();
