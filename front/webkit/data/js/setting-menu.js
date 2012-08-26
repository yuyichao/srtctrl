$(function () {
    var name = SrtIFace.get_name();
    var station;
    SrtIFace.connect(
        "config", function (field, key, value) {
            if (field != name || key != 'station')
                return;
            if (!station) {
                station = value.slice();
                create_sys_config();
            }
            station = value;
        });
    SrtSend.config(name, 'station');
    function create_sys_config() {
        $.input_dialog("#system-config-button", [{
            name: "lon",
            label: "Station Longitude",
            type: "text",
            'default': station[0]
        }, {
            name: "lat",
            label: "Station Latitude",
            type: "text",
            'default': station[1]
        }, {
            name: "alt",
            label: "Station Altitude",
            type: "text",
            'default': station[2]
        }], [{
            label: "Apply",
            callback: function (res) {
                var lon = SrtComm('guess_angle', res.lon);
                var lat = SrtComm('guess_angle', res.lat);
                var alt = SrtComm('guess_angle', res.alt);
                if (!isFinite(lon)) {
                    lon = station[0];
                }
                if (!isFinite(lat)) {
                    lat = station[1];
                }
                if (!isFinite(alt)) {
                    alt = station[2];
                }
                SrtSend.set_config(name, 'station', [lon, lat, alt]);
            }
        }, {
            label: "Cancel"
        }], {
            id: 'system-config',
            title: "System Setting"
        });
    }
    $.input_dialog("#gui-config-button", [{
        name: "sky_map_time",
        label: "Sky Map Time",
        type: "text",
        'default': 0
    }], [{
        label: "Apply",
        callback: function (res) {
            SetMapTime(res.sky_map_time);
        }
    }, {
        label: "Cancel"
    }], {
        id: 'system-config',
        title: "System Setting"
    });
});
