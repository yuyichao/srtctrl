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
        type: "text",
        advanced: true,
        default: 1
    }, {
        name: "y_half",
        label: "Steps numbers(y)",
        type: "text",
        advanced: true,
        default: 1
    }], [{
        label: "Run"
    }], {
        title: "N Point Scan"
    });
});
