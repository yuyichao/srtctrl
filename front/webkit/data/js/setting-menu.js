$(function () {
    $.input_dialog("#system-config-button", [{
        name: "long",
        label: "Station Longitude",
        type: "text",
    }, {
        name: "lat",
        label: "Station Latitude",
        type: "text",
    }, {
        name: "alt",
        label: "Station Altitude",
        type: "text",
    }], [{
        label: "System Setting",
        callback: function (res) {
            var fname = res.fname;
            if ($.type(fname) != "string")
                return;
            if (fname.match(/\.py$/)) {
                SrtSend.start("python", {fname: fname});
            } else {
                SrtSend.start("zwicky_cmd", {fname: fname});
            }
        }
    }, {
        label: "Cancel"
    }], {
        title: "Run Script"
    });
    $('#quit-button').click(function (ev) {
        SrtSend.quit();
        return true;
    });
    $('#stow-quit-button').click(function (ev) {
        SrtSend.cmd('quit', [], {});
        return true;
    });
    $('#refresh-button').click(function (ev) {
        SrtCall('refresh');
        return true;
    });
});
