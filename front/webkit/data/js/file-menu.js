$(function () {
    $.input_dialog("#run-script-button", [{
        name: "fname",
        label: "Script File",
        type: "open_file",
    }], [{
        label: "Run",
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
    $('#refresh-button').click(function (ev) {
        SrtCall('refresh');
        return true;
    });
});
