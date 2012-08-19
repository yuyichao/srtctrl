(function () {
    var auto_refresh = [];
    function redraw(obj) {
        var ele = obj.ele;
        if (obj.resize) {
            clearTimeout(obj.resize);
            obj.resize = null;
        }
        ele.attr({
            width: ele.width(),
            height: ele.height()
        });
        for (var i in obj.cbs) {
            try {
                obj.cbs[i](ele);
            } catch (e) {
            }
        }
    }
    function new_figure(ele) {
        ele = $(ele);
        var res = {
            ele: ele,
            cbs: [],
            resize: null
        };
        ele.resize(function () {
            if (res.resize) {
                clearTimeout(res.resize);
            }
            res.resize = setTimeout(function () {
                res.resize = null;
                redraw(res);
            }, 100);
        });
        return res;
    }
    function push_canvas(ele, cb) {
        var obj;
        var id;
        ele = $(ele);
        if (!(id = ele.attr('auto-refresh'))) {
            id = auto_refresh.length;
            ele.attr('auto-refresh', id);
            obj = new_figure(ele);
            auto_refresh.push(obj);
        } else {
            obj = auto_refresh[id];
        }
        if ($.isFunction(cb)) {
            obj.cbs.push(cb);
        }
        redraw(obj);
    }
    $.fn.extend({
        autorefresh: function (cb) {
            var eles = $(this).filter('canvas');
            eles.each(function () {
                push_canvas(this, cb);
            });
            return $(this);
        }
    });
})();
