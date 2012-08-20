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
                Back.IFace.start("python", {fname: fname});
            } else {
                Back.IFace.start("zwicky_cmd", {fname: fname});
            }
        }
    }, {
        label: "Cancel"
    }], {
        title: "Run Script"
    });
    $('#quit-button').click(function (ev) {
        Back.IFace.quit();
        return true;
    });
    $('#refresh-button').click(function (ev) {
        window.top.location.reload();
        return true;
    });
});
