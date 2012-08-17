$(function () {
    $.input_dialog("#npoint-button", [{
        name: "x_step",
        label: "Step width(x)",
        type: "text"
    }, {
        name: "y_step",
        label: "Step width(y)",
        type: "text"
    }, {
        name: "x_half",
        label: "Steps numbers(x)",
        type: "text"
    }, {
        name: "y_half",
        label: "Steps numbers(y)",
        type: "text"
    }], [{
        label: "Run"
    }]);
});
