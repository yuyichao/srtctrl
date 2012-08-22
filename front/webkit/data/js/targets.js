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
        var radius = setting.font_height / 3;
        if (radius < 1)
            radius = 1;
        if (setting.hover)
            radius = radius * 2;
        var arc = {
            fillStyle: "black",
            x: xy.x,
            y: xy.y,
            radius: radius
        };
        if (setting.hover) {
            $.extend(arc, {
                strokeStyle: "blue",
                strokeWidth: radius / 3
            });
        }
        $(this).drawArc(arc);
        // TODO draw name
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
