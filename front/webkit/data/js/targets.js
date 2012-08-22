$(function () {
    var targets_list = [{
        label: 'Mars',
        args: {
            name: 'mars'
        }
    }, {
        label: 'Moon',
        args: {
            name: 'moon'
        }
    }, {
        label: 'Sun',
        args: {
            name: 'sun'
        }
    }];
    for (var i = -30;i < 100;i += 5) {
        targets_list.push({
            label: 'G' + i.toFixed(),
            args: {
                name: 'galactic',
                args: [i, 0]
            }
        });
    }
    function draw_target(az, el, target, setting) {
        var xy = sky_map_azel({
            az: az,
            el: el
        });
        var r_radius = setting.font_height / 3;
        if (r_radius < 1)
            r_radius = 1;
        var radius;
        if (setting.hover) {
            radius = r_radius * 1.5;
        } else {
            radius = r_radius;
        }
        var arc = {
            fillStyle: "black",
            x: xy.x,
            y: xy.y,
            radius: radius
        };
        if (setting.hover) {
            $.extend(arc, {
                fillStyle: "red",
                strokeStyle: "black",
                strokeWidth: radius / 3
            });
        }
        $(this).drawArc(arc);
        var text = {
            fillStyle: 'black',
            x: xy.x + r_radius * 2,
            y: xy.y,
            text: target.label
        };
        var text_size = $(this).measureText(text);
        text.x += text_size.width / 2;
        if (setting.hover) {
            $.extend(text, {
                fillStyle: 'red'
            });
        }
        $(this).drawText(text);
    }
    function register_target(target) {
        var success_conn;
        var az = -100;
        var el = -100;
        SrtSend.alarm('track', 'target_track_' + target.label, $.extend({
            station: station
        }, target.args))
        success_conn = SrtIFace.connect(
            "alarm-success::track", function (name, nid, success) {
                if (nid != 'target_track_' + target.label)
                    return;
                SrtIFace.disconnect(success_conn);
                success_conn = 0;
                if (!success)
                    return;
                SrtIFace.connect(
                    "alarm::track", function (name, nid, alarm) {
                        if (nid != 'target_track_' + target.label)
                            return;
                        az = alarm.az;
                        el = alarm.el;
                        redraw_sky_map();
                    });
                add_sky_map({
                    redraw: function (setting) {
                        draw_target.call(this, az, el, target, setting);
                    },
                    remap: function (write_remap, setting) {
                        var xy = sky_map_azel({
                            az: az,
                            el: el
                        });
                        xy.x = Math.round(xy.x);
                        xy.y = Math.round(xy.y);
                        var radius = setting.font_height * (2 / 3);
                        if (radius < 2) {
                            radius = 2;
                        } else {
                            radius = Math.round(radius);
                        }
                        for (var x = -radius;x <= radius;x++) {
                            for (var y = -radius;y < radius;y++) {
                                if (x * x + y * y <= radius * radius) {
                                    write_remap(xy.x + x, xy.y + y);
                                }
                            }
                        }
                        var text = {
                            x: xy.x + radius,
                            y: xy.y,
                            text: target.label
                        };
                        var text_size = $(this).measureText(text);
                        text.y -= text_size.height / 2;
                        for (var x = 0;x <= text_size.width;x++) {
                            for (var y = 0;y <= text_size.height;y++) {
                                write_remap(text.x + x, text.y + y);
                            }
                        }
                    },
                    click: function () {
                    }
                });
            });
    }
    var station;
    function register_all() {
        var name = SrtIFace.get_name();
        var station_conn = SrtIFace.connect(
            "config", function (field, key, value) {
                if (field != name || key != 'station')
                    return;
                station = value;
                SrtIFace.disconnect(station_conn);
                for (var i in targets_list) {
                    register_target(targets_list[i]);
                }
            });
        SrtSend.config(name, 'station');
    }
    try {
        register_all();
    } catch (e) {
    }
});
