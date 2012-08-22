var SrtCallbacks = {}
var SrtGotObj;
var SrtCall;
var SrtSend;
var SrtOS;
var SrtIFace;

function SrtObject(opt) {
    var setting = $.extend({
        signals: {}
    }, opt);
    var sig_id = 0;
    var all_connecters = {};
    var connecters = {};
    var signals = {};
    for (var sname in setting.signals) {
        var argc = parseInt(setting.signals[sname]);
        if (!(isFinite(argc) && argc >= 0))
            continue;
        sname = sname.replace(/_/g, '-');
        signals[sname] = argc;
    }
    for (var sname in signals)
        connecters[sname] = {};
    var obj = {
        connect: function (full_name, cb) {
            full_name = full_name.replace(/_/g, '-');
            var args = Array.prototype.slice.call(arguments, 2);
            var name = String.prototype.split.call(full_name, '::', 2);
            var detail = name[1];
            name = name[0];
            if (!name in signals)
                return undefined;
            var id = ++sig_id;
            var connecter = {
                name: name,
                detail: detail,
                args: args,
                cb: cb,
                id: id
            };
            connecters[name][id] = connecter;
            all_connecters[id] = name;
            return id;
        },
        disconnect: function (id) {
            var name = all_connecters[id];
            try {
                delete all_connecters[id];
                delete connecters[name][id];
            } catch (e) {
            }
        },
        emit: function (full_name) {
            full_name = full_name.replace(/_/g, '-');
            var name = String.prototype.split.call(full_name, '::', 2);
            var detail = name[1];
            name = name[0];
            if (!name in signals)
                return false;
            var args = Array.prototype.slice.call(arguments, 1,
                                                  1 + signals[name]);
            for (var i in connecters[name]) {
                var conn = connecters[name][i];
                if (!detail || detail === conn.detail) {
                    try {
                        conn.cb.apply(this, args.concat(conn.args));
                    } catch (e) {
                    }
                }
            }
        }
    };
    return obj;
}

/* Init SrtIFace */
(function () {
    var signals_def = {
        config: 3,
        cmd: 0,
        res: 5,
        alarm: 5,
        error: 2,
        alarm_success: 3,
        prop: 2,
        query: 2,
        signal: 3
    };
    SrtIFace = SrtObject({
        signals: signals_def
    });
})();

(function () {
    var cb_count = 0;
    SrtCall = function (type, args) {
        var res = null
        cb_count = (cb_count + 1) % 4000000000
        name = '_' + cb_count;
        SrtCallbacks[name] = function (a) {
            res = a;
        }
        alert(JSON.stringify({
            type: type,
            args: args,
            callback: 'SrtCallbacks.' + name
        }));
        delete SrtCallbacks[name];
        return res;
    }
    SrtOS = function () {
        return SrtCall('os', Array.prototype.slice.call(arguments));
    }
    open = function (uri) {
        return SrtCall('open', uri);
    }
    function _send(pkg) {
        return SrtCall('send', pkg);
    }
    SrtSend = {
        start: function (name, args) {
            _send({
                type: 'start',
                name: name,
                args: args,
                pwd: SrtOS('getcwd')
            });
        },
        float: function (f) {
            _send({
                type: 'float',
                float: f
            });
        },
        prop: function (name) {
            _send({
                type: 'prop',
                name: name
            });
        },
        query: function (name) {
            _send({
                type: 'query',
                name: name
            });
        },
        cmd: function (name, args, kwargs) {
            _send({
                type: 'cmd',
                name: name,
                args: args,
                kwargs: kwargs
            });
        },
        /* Skip Lock */
        quit: function () {
            _send({
                type: 'quit'
            });
        },
        alarm: function (name, nid, args) {
            _send({
                type: 'alarm',
                name: name,
                nid: nid,
                args: args
            });
        },
        config: function (field, name) {
            _send({
                type: 'config',
                field: field,
                name: name,
                notify: false
            });
        }
    };
    SrtGotObj = function (pkg) {
        switch (pkg.type) {
        case 'ping':
            _send({
                type: 'pong'
            });
            break;
        case 'quit':
            SrtCall('quit');
            break;
        case 'config':
            handle_config(pkg);
            break;
        case 'prop':
            handle_prop(pkg);
            break;
        case 'query':
            handle_query(pkg);
            break;
        case 'alarm':
            handle_alarm(pkg);
            break;
        case 'error':
            handle_error(pkg);
            break;
        case 'cmd':
            handle_cmd(pkg);
            break;
        case 'res':
            handle_res(pkg);
            break;
        case 'signal':
            handle_signal(pkg);
            break;
        }
    }
    function handle_config(pkg) {
    }
    function handle_prop(pkg) {
    }
    function handle_query(pkg) {
    }
    function handle_alarm(pkg) {
    }
    function handle_error(pkg) {
    }
    function handle_cmd(pkg) {
    }
    function handle_res(pkg) {
    }
    function handle_signal(pkg) {
        var name = pkg.name;
        if (!name)
            return;
        SrtIFace.emit('signal::' + name.replace(/_/g, '-'),
                     name, pkg.value, pkg.props);
    }
})();
