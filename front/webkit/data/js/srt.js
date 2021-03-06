$(function () {
    var resize_timeout = false;
    var body = $(window);
    var header = $("#header");
    var content = $("#content");
    var footer = $("#footer");
    var toolbar = $.toolbar([{
        label: "File",
        submenu: [{
            id: 'save-button',
            label: "Set Data File"
        }, {
            id: 'run-script-button',
            label: "Run Script"
        }, {
            id: 'refresh-button',
            label: "Refresh"
        }, {
            id: 'stow-quit-button',
            label: "Stow and Quit"
        }, {
            id: 'quit-button',
            label: "Force Quit"
        }]
    }, {
        label: "Commands",
        submenu: [{
            id: 'move-button',
            label: "Move"
        }, {
            id: 'set-freq-button',
            label: "Set Frequency"
        }, {
            id: 'take-data-button',
            label: "Start Taking Data"
        }, {
            id: 'stop-button',
            label: "Stop Taking Data"
        }, {
            id: 'calib-button',
            label: "Calibrate"
        }, {
            id: 'npoint-button',
            label: "N-Point Scan"
        }, {
            id: 'offset-button',
            label: "Set Offset"
        }, {
            id: 'stow-button',
            label: "Stow"
        }]
    }, {
        label: "Setting",
        submenu: [{
            id: 'system-config-button',
            label: "System Setting"
        }, {
            id: 'gui-config-button',
            label: "GUI Setting"
        }]
    }, {
        label: "Help",
        submenu: [{
            id: 'doc-button',
            label: "Document"
        }, {
            id: 'feedback-button',
            label: "Feedback"
        }, {
                id: 'about-button',
            label: "About"
        }]
    }]);
    $("#header").append(
        toolbar.addClass('ui-widget-header')
            .addClass('ui-corner-all')
            .width("100%"));
    function srt_cal_size() {
        content.height(body.height() - header.height() - footer.height() - 6);
    }
    function resize_wrapper() {
        if (resize_timeout !== false) {
            srt_cal_size();
            clearTimeout(resize_timeout);
        }
        resize_timeout = setTimeout(srt_cal_size, 200);
    }
    $(document).bind("contextmenu", function(e) {
        //TODO
        return false;
    });
    footer.resize(resize_wrapper);
    header.resize(resize_wrapper);
    body.resize(resize_wrapper);
    body.keydown(function (ev) {
        if (ev.keyCode == 116) {
            SrtCall('refresh');
            return false;
        }
        return true;
    });
    resize_wrapper();
    try {
        SrtIFace.connect("signal", function (src, name, value, props) {
            // update properties here
        });
    } catch (e) {
    }
});
