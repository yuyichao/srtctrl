$(function () {
    $.input_dialog("#npoint-button", [{
        name: "x_step",
        label: "Step width(x)",
        type: "text",
        default: 2
    }, {
        name: "y_step",
        label: "Step width(y)",
        type: "text",
        default: 2
    }, {
        name: "x_half",
        label: "Steps numbers(x)",
        type: "number",
        advanced: true,
        default: 1
    }, {
        name: "y_half",
        label: "Steps numbers(y)",
        type: "number",
        advanced: true,
        default: 1
    }, {
        name: "angle",
        label: "Angle of X Axis",
        type: "text",
        advanced: true,
        default: "0"
    }, {
        name: "count",
        label: "Count",
        type: "number",
        advanced: true,
        default: 1
    }, {
        name: "interval",
        label: "Interval",
        type: "text",
        advanced: true
    }], [{
        label: "Run",
        callback: function (res) {
            var kwargs = {};
            for (var key in res) {
                if (!res[key])
                    continue;
                kwargs[key] = res[key];
            }
            PyUtil.call(Back.IFace.cmd.npoint, [], kwargs);
        }
    }, {
        label: "Cancel"
    }], {
        title: "N Point Scan"
    });
});
