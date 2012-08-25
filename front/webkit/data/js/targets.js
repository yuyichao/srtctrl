var SetMapTime;

$(function () {
    var time = 0;
    var track = true;
    var TrackObj = SrtObject({
        signals: {
            'time': 0
        }
    });
    SetMapTime = function (_time) {
        var new_interval = SrtComm('guess_interval', _time);
        if (isFinite(new_interval)) {
            if (new_interval == time && track == true)
                return;
            time = new_interval;
            track = true;
            TrackObj.emit('time');
            return;
        }
        var new_interval = SrtComm('guess_interval', _time);
        if (isFinite(new_interval)) {
            if (new_interval == time && track == true)
                return;
            time = new_interval;
            track = true;
            TrackObj.emit('time');
            return;
        }
    };
    /**
     * Initialize the target list
     **/
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

    /**
     * Functions to draw and map a single target
     **/
    function draw_target(x, y, target, setting) {
        var r_radius = setting.font_height / 3;
        if (r_radius < 1)
            r_radius = 1;
        var radius;
        if (setting.hover) {
            radius = r_radius * 1.2;
        } else {
            radius = r_radius;
        }
        var arc = {
            fillStyle: "black",
            x: x,
            y: y,
            radius: radius
        };
        if (setting.hover) {
            $.extend(arc, {
                fillStyle: "red",
                strokeStyle: "black",
                strokeWidth: radius * .8
            });
        }
        $(this).drawArc(arc);
        var text = {
            fillStyle: 'black',
            x: x + r_radius * 2,
            y: y,
            text: target.label
        };
        var text_size = $(this).measureText(text);
        text.x += text_size.width / 2;
        if (setting.hover) {
            $.extend(text, {
                fillStyle: 'red',
                strokeStyle: 'red',
                strokeWidth: setting.font_height / 15
            });
        }
        $(this).drawText(text);
    }
    function map_target(x, y, target, write_remap, setting) {
        var radius = setting.font_height * (2 / 3);
        if (radius < 2) {
            radius = 2;
        } else {
            radius = Math.round(radius);
        }
        for (var dx = -radius;dx <= radius;dx++) {
            for (var dy = -radius;dy < radius;dy++) {
                if (dx * dx + dy * dy <= radius * radius) {
                    write_remap(x + dx, y + dy);
                }
            }
        }
        var text = {
            x: x + radius,
            y: y,
            text: target.label
        };
        var text_size = $(this).measureText(text);
        text.y -= text_size.height / 2;
        for (var dx = 0;dx <= text_size.width;dx++) {
            for (var dy = 0;dy <= text_size.height;dy++) {
                write_remap(text.x + dx, text.y + dy);
            }
        }
    }

    var station;
    function send_track_alarm(target) {
        SrtSend.alarm('track', 'target_track_' + target.label, $.extend({
            station: station
        }, target.args))
    }
    function register_target(target) {
        var az = -100;
        var el = -100;
        var xy = {};
        send_track_alarm(target);
        SrtIFace.connect(
            "alarm::track", function (name, nid, alarm) {
                if (nid != 'target_track_' + target.label)
                    return;
                az = alarm.az;
                el = alarm.el;
                var new_xy = sky_map_azel(alarm);
                if (new_xy.x - xy.x <= 1 && new_xy.y - xy.y <= 1) {
                    return;
                }
                xy = new_xy;
                redraw_sky_map();
            });
        add_sky_map({
            redraw: function (setting) {
                xy = sky_map_azel({
                    az: az,
                    el: el
                });
                draw_target.call(this, xy.x, xy.y, target, setting);
            },
            remap: function (write_remap, setting) {
                xy = sky_map_azel({
                    az: az,
                    el: el
                });
                map_target.call(this, xy.x, xy.y, target, write_remap, setting);
            },
            click: function () {
                SrtSend.cmd('move', [], target.args);
            }
        });
    }
    function register_all() {
        /**
         * This function call will complete until the backend gets a valid name
         * (or exit if it cannot get one)
         **/
        var name = SrtIFace.get_name();
        SrtIFace.connect(
            "config", function (field, key, value) {
                if (field != name || key != 'station')
                    return;
                if (!station) {
                    station = value;
                    for (var i in targets_list) {
                        register_target(targets_list[i]);
                    }
                } else {
                    station = value;
                    for (var i in targets_list) {
                        send_track_alarm(targets_list[i]);
                    }
                }
            });
        SrtSend.config(name, 'station');
    }
    try {
        register_all();
    } catch (e) {
    }
});
