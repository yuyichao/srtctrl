$(function () {
    $.input_dialog("#move-button", [{
        name: "name",
        label: "Target Name",
        type: "text",
        'default': 'azel'
    }, {
        name: "az",
        label: "Azimuth",
        tooltip: "Has no effect for some targets, e.g. Sun, Mars, Moon...",
        type: "text",
        'default': 0
    }, {
        name: "el",
        label: "Elevation",
        tooltip: "Has no effect for some targets, e.g. Sun, Mars, Moon...",
        type: "text",
        'default': 0
    }, {
        name: "offset_x",
        label: "Offset(x)",
        advanced: true,
        'default': 0
    }, {
        name: "offset_y",
        label: "Offset(y)",
        advanced: true,
        'default': 0
    }, {
        name: "time",
        label: "Time",
        type: "text",
        advanced: true
    }, {
        name: "track",
        label: "Track",
        type: "boolean",
        advanced: true,
        'default': true
    }], [{
        label: "Move",
        callback: function (res) {
            if (!res.az)
                res.az = 0;
            if (!res.el)
                res.el = 0;
            res.args = [res.az, res.el];
            if (!res.offset_x)
                res.offset_x = 0;
            if (!res.offset_y)
                res.offset_y = 0;
            res.offset = [res.offset_x, res.offset_y];
            SrtSend.cmd('move', [], res);
        }
    }, {
        label: "Cancel"
    }], {
        title: "Move"
    });
    $.input_dialog("#set-freq-button", [{
        name: "freq",
        label: "Center Frequency",
        type: "number",
        'default': 1420.4
    }, {
        name: "mode",
        label: "Mode",
        type: "number",
        option: {
            min: 1,
            max: 5
        },
        'default': 1
    }], [{
        label: "Set",
        callback: function (res) {
            SrtSend.cmd('set_freq', [], res);
        }
    }, {
        label: "Cancel"
    }], {
        title: "Set Frequency"
    });
    $.input_dialog("#calib-button", [{
        name: "count",
        label: "Count",
        type: "number",
        'default': 1,
        advanced: true
    }], [{
        label: "Calibrate",
        callback: function (res) {
            SrtSend.cmd('calib', [], res);
        }
    }, {
        label: "Cancel"
    }], {
        title: "Calibrate"
    });
    $.input_dialog("#offset-button", [{
        name: "az",
        label: "Azimuth",
        type: "text",
        'default': 0
    }, {
        name: "el",
        label: "Elevation",
        type: "text",
        'default': 0
    }], [{
        label: "Set",
        callback: function (res) {
            SrtSend.cmd('set_offset', [], res);
        }
    }, {
        label: "Cancel"
    }], {
        title: "Set Offset"
    });
    $.input_dialog("#npoint-button", [{
        name: "x_step",
        label: "Step width(x)",
        advanced: true,
        type: "text",
        'default': 2
    }, {
        name: "y_step",
        label: "Step width(y)",
        advanced: true,
        type: "text",
        'default': 2
    }, {
        name: "x_count",
        label: "Steps count(x)",
        type: "number",
        option: {
            min: 1
        },
        'default': 3
    }, {
        name: "y_count",
        label: "Steps count(y)",
        type: "number",
        option: {
            min: 1
        },
        'default': 3
    }, {
        name: "angle",
        label: "Angle of X axis",
        type: "text",
        advanced: true,
        'default': "0"
    }, {
        name: "count",
        label: "Count",
        type: "number",
        option: {
            min: 1
        },
        advanced: true,
        'default': 1
    }, {
        name: "interval",
        label: "Interval",
        type: "text",
        advanced: true
    }], [{
        label: "Run",
        callback: function (res) {
            SrtSend.cmd('npoint', [], res);
        }
    }, {
        label: "Cancel"
    }], {
        title: "N Point Scan"
    });
    $('#stow-button').click(function () {
        SrtSend.cmd('reset', [], {});
        return false;
    });
    $('#take-data-button').click(function () {
        SrtCall('take-data', true);
        return false;
    });
    $('#stop-button').click(function () {
        SrtCall('take-data', false);
        return false;
    });
});
