$(function () {
    var command = $("#command");
    var command_prompt = $("#command-prompt");
    var footer = $("#footer");
    var comp_waiting = [];
    function comp_from_list(term, list, prefix) {
        var res = [];
        for (var i in list) {
            if (String.prototype.indexOf.call(list[i], term) === 0) {
                res.push([prefix, list[i]].join(''));
            }
        }
        res.sort(function (a, b) {
            return a.length - b.length;
        });
        res.splice(4);
        return res;
    };
    // SrtIFace.connect("query::cmds", function (name, name_list) {
    //     if (name != "cmds")
    //         return;
    //     comp_waiting.forEach(function (value, i) {
    //         value.response(comp_from_list(value.term, name_list,
    //                                       value.prefix));
    //     });
    //     comp_waiting = [];
    // });
    function add_wait_comp(term, response, prefix) {
        if (comp_waiting.length == 0) {
            SrtSend.query("cmds");
        }
        comp_waiting.push({
            prefix: prefix,
            term: term,
            response: response
        });
    }
    command.autocomplete({
        source: function (request, response) {
            var term = request.term.replace(/^[\s:]+|[\s:]+$/g, '');
            var time_cmd = term.split(/\s/g);
            var time = time_cmd.shift();
            if (SrtUtil.try_get_interval(time) === null) {
                add_wait_comp(time, response, '');
                return;
            }
            if (time_cmd.length == 0) {
                response([]);
                return;
            }
            add_wait_comp(time_cmd[0], response, [time, ' '].join(''));
            return;
        },
        position: {
            my: "left bottom",
            at: "left top",
            of: "#command",
            collision: "fit"
        },
        delay: 100,
    });
    function command_size() {
        command.width((footer.width() - command_prompt.width()) * 0.9);
    }
    $("#footer").resize(command_size);
    command_size();
});
