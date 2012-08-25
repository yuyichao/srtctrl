$(function () {
    var azel = SrtState('heading_azel');
    if (!azel)
        azel = [-100, -100]
    try {
        SrtIFace.connect(
            "signal::heading", function (name, value, props) {
                azel = value;
                SrtState('heading_azel', azel);
                redraw_sky_map();
            });
    } catch (e) {
    }
    add_sky_map({
        redraw: function (setting) {
            var xy = sky_map_azel({
                az: azel[0],
                el: azel[1]
            });
            $(this).drawLine({
                strokeStyle: "#0f0",
                strokeWidth: 2,
                x1: xy.x - setting.font_height,
                y1: xy.y,
                x2: xy.x + setting.font_height,
                y2: xy.y
            });
            $(this).drawLine({
                strokeStyle: "#0f0",
                strokeWidth: 2,
                x1: xy.x,
                y1: xy.y - setting.font_height,
                x2: xy.x,
                y2: xy.y + setting.font_height
            });
        }
    });
});

$(function () {
    var azel = SrtState('move_azel');
    if (!azel)
        azel = [-100, -100]
    try {
        SrtIFace.connect(
            "signal::move", function (name, value, props) {
                azel = value;
                SrtState('move_azel', azel);
                redraw_sky_map();
            });
    } catch (e) {
    }
    add_sky_map({
        redraw: function (setting) {
            var xy = sky_map_azel({
                az: azel[0],
                el: azel[1]
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
