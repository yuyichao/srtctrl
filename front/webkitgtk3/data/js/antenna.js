$(function () {
    var az = 0;
    var el = 0;
    try {
        if (Back.SrtState.antenna_move) {
            Back.IFace.slave.disconnect(Back.SrtState.antenna_move);
        }
        Back.SrtState.antenna_move = Back.IFace.slave.connect(
            "signal::move", function (src, name, value, props) {
                az = value[0];
                el = value[1];
                redraw_sky_map();
            });
    } catch (e) {
    }
    add_sky_map({
        redraw: function (setting) {
            var xy = sky_map_azel({
                az: az,
                el: el
            });
            $(this).drawLine({
                strokeStyle: "#00f",
                strokeWidth: 2,
                x1: xy.x - setting.font_height,
                y1: xy.y,
                x2: xy.x + setting.font_height,
                y2: xy.y
            });
            $(this).drawLine({
                strokeStyle: "#00f",
                strokeWidth: 2,
                x1: xy.x,
                y1: xy.y - setting.font_height,
                x2: xy.x,
                y2: xy.y + setting.font_height
            });
        }
    });
});
