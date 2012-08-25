(function () {
    function num_to_label(min, max) {
        var diff = (max - min) / 5;
        var n = Math.floor(Math.max(Math.log(Math.abs(min)),
                                    Math.log(Math.abs(min))) / Math.log(10));
        var dn = Math.floor(Math.log(Math.abs(diff)) / Math.log(10));
        if (n <= 0) {
            n = Math.max(n - dn, 0);
            n = Math.min(n, 3);
            return [min.toExponential(n), max.toExponential(n)];
        }
        if (n <= 4) {
            if (dn >= -1) {
                return [min.toFixed(1), max.toFixed(1)];
            }
            n = Math.max(n - dn, 5);
            return [min.toFixed(n), max.toFixed(n)];
        }
        if (n <= 6) {
            return [min.toFixed(0), max.toFixed(0)];
        }
        n = Math.max(n - dn, 0);
        n = Math.min(n, 3);
        return [min.toExponential(n), max.toExponential(n)];
    }
    $.extend({
        plot_region: function () {
            var ele = $(this.filter('canvas')[0]);
            var plot_width;
            var plot_height;
            var font_height;
            var sky_map;
            var redraw_timeout = undefined;
            var axis_size = {
                x: undefined,
                y: undefined
            };
            var lines = {};
            var limits = {};
            var res = {
                ele: ele,
                set_plot: function (name, data) {
                    if (!data) {
                        delete lines[name];
                        return;
                    }
                    if (!isArray(data))
                        return;
                    lines[name] = data;
                },
                set_xlimit: function (min, max) {
                    min = parseFloat(min);
                    max = parseFloat(max);
                    if (!isFinite(min) || !isFinite(max))
                        return;
                    limits.x = [min, max];
                },
                set_ylimit: function (min, max) {
                    min = parseFloat(min);
                    max = parseFloat(max);
                    if (!isFinite(min) || !isFinite(max))
                        return;
                    limits.y = [min, max];
                }
            };
            function resize() {
                plot_width = ele.width();
                plot_height = ele.height();
                font_height = plot_height / 15;
                axis_size.x = plot_width / 15;
                var x = ele.css('font-size', font_height).measureText({
                    text: '888888'
                });
                if (x.width > axis_size.x) {
                    font_height = font_height * axis_size.x / x.width;
                    x = ele.css('font-size', font_height).measureText({
                        text: '888888'
                    });
                }
                axis_size.x = x.width;
                axis_size.y = x.height * 5 / 4;
                font_height = x.height;
            }
            function redraw() {
                var x_labels;
                var y_labels;
                if ('x' in limits) {
                    x_labels = num_to_label(limits.x);
                }
            }
        }
    });
    function redraw_axis(ele, axis_size, plot_height, plot_width,
                         x_labels, y_labels) {
        ele.drawLine({
            strokeStyle: "#000",
            strokeWidth: 1,
            x1: axis_size.x,
            y1: axis_size.y,
            x2: axis_size.x,
            y2: plot_height - axis_size.y
        }).drawLine({
            strokeStyle: "#000",
            strokeWidth: 1,
            x1: axis_size.x,
            y1: plot_height - axis_size.y,
            x2: plot_width - axis_size.x,
            y2: plot_height - axis_size.y
        });
        if (x_labels) {
            if (x_labels[0])
                ele.drawText({
                    fillStyle: "black",
                    x: axis_size.x,
                    y: plot_height - axis_size.y / 2,
                    text: x_labels[0]
                });
            if (x_labels[1])
                ele.drawText({
                    fillStyle: "black",
                    x: plot_width - axis_size.x,
                    y: plot_height - axis_size.y / 2,
                    text: x_labels[1]
                });
        }
        if (y_labels) {
            if (y_labels[0])
                ele.drawText({
                    fillStyle: "black",
                    x: axis_size.x / 2,
                    y: plot_height - axis_size.y,
                    text: y_labels[0]
                });
            if (y_labels[1])
                ele.drawText({
                    fillStyle: "black",
                    x: axis_size.x / 2,
                    y: axis_size.y,
                    text: y_labels[1]
                });
        }
    }
    function convert_x(x, axis_size, plot_height, plot_width) {
        return Math.round(axis_size.x +
                          (plot_width - axis_size.x * 2) * (x / 360));
    }
    function convert_y(y, axis_size, plot_height, plot_width) {
        return Math.round(axis_size.y +
                          (plot_height - axis_size.y * 2) * (1 - y / 90));
    }
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
        }).click(function () {
            try {
                obj_list[hover].click();
            } catch (e) {
            }
        });
    });
})();
