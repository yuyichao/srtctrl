$(function () {
    var command = $("#command");
    var command_prompt = $("#command-prompt");
    var footer = $("#footer");
    function comp_from_list(term, list) {
        var res = [];
        for (var i in list) {
            if (String.prototype.indexOf.call(list[i], term) === 0) {
                res.push(list[i]);
            }
        }
        return res;
    };
    command.autocomplete({
        minLength: 2,
        source: function (request, response) {
            //TODO
            var term = request.term;
            var list = ["move", "radio", "calib"];
            response(comp_from_list(term, list));
        },
        position: {
            my: "left bottom",
            at: "left top"
        }
    });
    function command_size() {
        command.width((footer.width() - command_prompt.width()) * 0.9);
    }
    add_resize_cb(command_size);
    command_size();
});
