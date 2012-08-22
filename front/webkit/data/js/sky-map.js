var add_sky_map;
var redraw_sky_map;
var sky_map_azel;

(function () {
    var hover = undefined;
    var obj_list = [];
    var obj_map = {};
    var map_width;
    var map_height;
    var font_height;
    var sky_map;
    var redraw_timeout = undefined;
    var mouse_pos = {
        x: undefined,
        y: undefined
    }
    var axis_size = {
        x: undefined,
        y: undefined
    };
    sky_map_azel = function (azel) {
        return {
            x: az_to_x(azel.az),
            y: el_to_y(azel.el)
        };
    };
    // Map size, font size, axis size...
    function resize() {
        map_width = sky_map.width();
        map_height = sky_map.height();
        font_height = map_height / 25;
        axis_size.x = map_width / 20;
        var x = sky_map.css('font-size', font_height).measureText({
            text: '888888'
        });
        if (x.width > axis_size.x) {
            font_height = font_height * axis_size.x / x.width;
            x = sky_map.css('font-size', font_height).measureText({
                text: '888888'
            });
        }
        axis_size.x = x.width;
        axis_size.y = x.height * 5 / 4;
        font_height = x.height;
    }
    var v_axis_seps = [10, 15, 30, 45, 90];
    var h_axis_seps = [10, 20, 30, 45, 60, 90, 180, 360];
    function redraw_axis() {
        var h_sep = 360 / Math.max(map_width / axis_size.x - 2, 0) * 2;
        var v_sep = 90 / Math.max(map_height / axis_size.y - 2, 0) * 2;
        for (var i in h_axis_seps) {
            if (h_sep < h_axis_seps[i]) {
                h_sep = h_axis_seps[i];
                break;
            }
        }
        for (var i in v_axis_seps) {
            if (v_sep < v_axis_seps[i]) {
                v_sep = v_axis_seps[i];
                break;
            }
        }
        sky_map.drawLine({
            strokeStyle: "#000",
            strokeWidth: 1,
            x1: axis_size.x,
            y1: axis_size.y,
            x2: axis_size.x,
            y2: map_height - axis_size.y
        });
        sky_map.drawLine({
            strokeStyle: "#000",
            strokeWidth: 1,
            x1: axis_size.x,
            y1: map_height - axis_size.y,
            x2: map_width - axis_size.x,
            y2: map_height - axis_size.y
        });
        for (var h_axis = 0;h_axis <= 360;h_axis += h_sep) {
            var axis_x = az_to_x(h_axis);
            sky_map.drawLine({
                strokeStyle: "#bcf",
                strokeWidth: 1,
                x1: axis_x,
                y1: axis_size.y,
                x2: axis_x,
                y2: map_height - axis_size.y
            }).drawText({
                fillStyle: "black",
                x: axis_x,
                y: map_height - axis_size.y / 2,
                text: h_axis.toFixed()
            });
        }
        for (var v_axis = 0;v_axis <= 90;v_axis += v_sep) {
            var axis_y = el_to_y(v_axis);
            sky_map.drawLine({
                strokeStyle: "#bcf",
                strokeWidth: 1,
                x1: axis_size.x,
                y1: axis_y,
                x2: map_width - axis_size.x,
                y2: axis_y
            }).drawText({
                fillStyle: "black",
                x: axis_size.x / 2,
                y: axis_y,
                text: v_axis.toFixed()
            });
        }
    }
    function az_to_x(az) {
        return axis_size.x + (map_width - axis_size.x * 2) * (az / 360);
    }
    function el_to_y(el) {
        return axis_size.y + (map_height - axis_size.y * 2) * (1 - el / 90);
    }
    function redraw_all() {
        if (!sky_map)
            return;
        if (redraw_timeout) {
            clearTimeout(redraw_timeout);
            redraw_timeout = undefined;
        }
        sky_map.clearCanvas();
        redraw_axis();
        for (var i in obj_list) {
            redraw_point(i);
        }
    }
    function redraw_point(i) {
        try {
            obj_list[i].redraw.call(sky_map, {
                font_height: font_height,
                hover: i === hover
            });
        } catch (e) {
        }
    }

    function write_map(id, x, y) {
        if (!(x >= 0 && x < map_width && y >= 0 && y < map_height))
            return;
        obj_map[x * map_height + y] = id;
    }
    function remap_all() {
        if (!sky_map)
            return;
        obj_map = {};
        for (var i in obj_list) {
            remap_point(i);
        }
        hover = undefined;
        if (!check_hover())
            redraw_all();
    }
    function remap_point(i) {
        try {
            obj_list[i].remap.call(undefined, function (x, y) {
                write_map(i, x, y);
            }, {
                font_height: font_height
            });
        } catch (e) {
        }
    }
    /**
     * return true when redraw
     **/
    function check_hover() {
        var new_hover;
        var x = mouse_pos.x;
        var y = mouse_pos.y;
        if (!(x >= 0 && x < map_width && y >= 0 && y < map_height)) {
            new_hover = undefined;
        } else {
            new_hover = obj_map[x * map_height + y];
        }
        if (hover === new_hover)
            return false;
        hover = new_hover;
        redraw_all();
        return true;
    }
    add_sky_map = function (obj) {
        var id = obj_list.length;
        obj = $.extend({
            remap: null,
            redraw: null
        }, obj);
        obj_list.push(obj);
        remap_point(id);
        if (!check_hover())
            redraw_point(id);
    };
    redraw_sky_map = function () {
        if (redraw_timeout)
            return;
        redraw_timeout = setTimeout(function () {
            var redraw_timeout = undefined;
            redraw_all();
        }, 100);
    };
    $(function () {
        sky_map = $("#sky-map");
        sky_map.autorefresh(function () {
            resize();
            remap_all();
        }).mousemove(function (event) {
            mouse_pos.x = event.offsetX;
            mouse_pos.y = event.offsetY;
            check_hover();
        }).mouseleave(function (event) {
            mouse_pos.x = undefined;
            mouse_pos.y = undefined;
            check_hover();
        });
    });
})();
