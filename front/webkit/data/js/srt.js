$(function () {
    var resize_timeout = false;
    var body = $(window);
    var header = $("#header");
    var content = $("#content");
    var footer = $("#footer");
    $("#header").append(
        $.toolbar([{
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
                id: 'quit-button',
                label: "Quit"
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
            label: "Help",
            submenu: [{
                id: 'doc-button',
                label: "Document"
            }, {
                id: 'feedback-button',
                label: "Feedback"
            }, {
                id: 'dev-tool-button',
                label: "Develop Tool"
            }, {
                id: 'about-button',
                label: "About"
            }]
        }]).addClass('ui-widget-header')
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
            window.top.location.reload();
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
