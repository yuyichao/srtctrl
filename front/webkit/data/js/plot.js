(function () {
    function lines_limit(lines) {
        var min = Infinity;
        var max = -Infinity;
        var tmp;
        for (var i in lines) {
            tmp = Math.max.apply(this, lines[i]);
            if (tmp > max)
                max = tmp;
            tmp = Math.min.apply(this, lines[i]);
            if (tmp < min)
                min = tmp;
        }
        return [min, max];
    }
    function num_to_label(limits) {
        var min = parseFloat(limits[0]);
        var max = parseFloat(limits[1]);
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
            n = Math.min(5 - n, -dn);
            return [min.toFixed(n), max.toFixed(n)];
        }
        if (n <= 6) {
            return [min.toFixed(0), max.toFixed(0)];
        }
        n = Math.max(n - dn, 0);
        n = Math.min(n, 3);
        return [min.toExponential(n), max.toExponential(n)];
    }
    $.fn.extend({
        plot_region: function () {
            var ele = $(this.filter('canvas')[0]);
            var plot_width;
            var plot_height;
            var font_height;
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
                    if (!$.isArray(data))
                        return;
                    lines[name] = data;
                    if (!redraw_timeout) {
                        setTimeout(function () {
                            redraw_timeout = undefined;
                            redraw();
                        }, 100);
                    }
                },
                set_xlimit: function (min, max) {
                    min = parseFloat(min);
                    max = parseFloat(max);
                    if (!(isFinite(min) && isFinite(max)))
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
                font_height = plot_height / 10;
                axis_size.x = plot_width / 10;
                var x = ele.css('font-size', font_height).measureText({
                    text: '8888'
                });
                if (x.width > axis_size.x) {
                    font_height = font_height * axis_size.x / x.width;
                    x = ele.css('font-size', font_height).measureText({
                        text: '8888'
                    });
                }
                axis_size.x = x.width;
                axis_size.y = x.height * 5 / 4;
                font_height = x.height;
            }
            function redraw() {
                var x_labels;
                var y_labels;
                var y_limit;
                if (redraw_timeout) {
                    clearTimeout(redraw_timeout);
                    redraw_timeout = undefined;
                }
                if ($.isEmptyObject(lines))
                    return;
                if ('x' in limits) {
                    x_labels = num_to_label(limits.x);
                }
                if ('y' in limits) {
                    y_limit = limits.y;
                } else {
                    y_limit = lines_limit(lines);
                }
                if (!(isFinite(y_limit[0]) && isFinite(y_limit[1])))
                    return;
                ele.clearCanvas();
                y_labels = num_to_label(y_limit);
                redraw_axis(ele, axis_size, plot_height, plot_width,
                            x_labels, y_labels);
                for(var l in lines) {
                    var line = lines[l];
                    var len = line.length;
                    var draw = {};
                    if (!len > 1)
                        continue;
                    for (var i in line) {
                        i = parseInt(i);
                        draw['x' + (i + 1)] = convert_x(
                            i / (len - 1), axis_size, plot_height, plot_width);
                        draw['y' + (i + 1)] = convert_y(
                            (line[i] - y_limit[0]) / (y_limit[1] - y_limit[0]),
                            axis_size, plot_height, plot_width);
                    }
                    draw = $.extend({
                        strokeStyle: "#000",
                        strokeWidth: 1
                    }, draw);
                    ele.drawLine(draw);
                }
            }
            ele.autorefresh(function () {
                resize();
                redraw();
            });
            return res;
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
                          (plot_width - axis_size.x * 2) * x);
    }
    function convert_y(y, axis_size, plot_height, plot_width) {
        return Math.round(axis_size.y +
                          (plot_height - axis_size.y * 2) * (1 - y));
    }
})();
