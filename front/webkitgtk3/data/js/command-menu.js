$(function () {
    $.input_dialog("#npoint-button", [{
        name: "x_step",
        label: "Step width(x)",
        advanced: true,
        type: "text",
        default: 2
    }, {
        name: "y_step",
        label: "Step width(y)",
        advanced: true,
        type: "text",
        default: 2
    }, {
        name: "x_count",
        label: "Steps count(x)",
        type: "number",
        option: {
            min: 1
        },
        default: 3
    }, {
        name: "y_count",
        label: "Steps count(y)",
        type: "number",
        option: {
            min: 1
        },
        default: 3
    }, {
        name: "angle",
        label: "Angle of X axis",
        type: "text",
        advanced: true,
        default: "0"
    }, {
        name: "count",
        label: "Count",
        type: "number",
        option: {
            min: 1
        },
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
            PyUtil.call(Back.IFace.cmd.npoint, [], res);
        }
    }, {
        label: "Cancel"
    }], {
        title: "N Point Scan"
    });
});
