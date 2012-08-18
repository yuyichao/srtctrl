$(function () {
    var resize_timeout = false;
    $("#header").append(
        $.toolbar([{
            label: "File",
            submenu: [{
                id: 'refresh-button',
                label: "Refresh"
            }, {
                id: 'quit-button',
                label: "Quit"
            }]
        }, {
            label: "Commands",
            submenu: [{
                id: 'npoint-button',
                label: "N-Point Scan"
            }]
        }, {
            id: 'about-button',
            label: "About"
        }]).addClass('ui-widget-header')
            .addClass('ui-corner-all')
            .width("100%"));
    function srt_cal_size() {
        var body = $(window);
        var header = $("#header");
        var content = $("#content");
        var footer = $("#footer");
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
    $("#footer").resize(resize_wrapper);
    $("#header").resize(resize_wrapper);
    $(window).resize(resize_wrapper);
    $(window).keydown(function (ev) {
        if (ev.keyCode == 116) {
            window.top.location.reload();
            return false;
        }
        return true;
    });
    resize_wrapper();
    // Back.IFace.slave.connect("signal", function (src, name, value, props) {
    // });
    $('#quit-button').click(function (ev) {
        Back.IFace.quit();
        return true;
    });
    $('#refresh-button').click(function (ev) {
        window.top.location.reload();
        return true;
    });
});
