var SrtCallbacks = {}
var SrtGotObj;
var SrtCall;

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
    open = function (uri) {
        return SrtCall('open', uri);
    }
    SrtGotObj = function (pkg) {
        console.log(JSON.stringify(pkg));
    }
})();
