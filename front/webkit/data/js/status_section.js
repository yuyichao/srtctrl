(function () {
    var status_section_count;
    $.extend({
        status_section: function (option) {
            var setting = $.extend({}, option);
            var link = $('<a></a>').attr('href', '#').text(setting.title);
            var title = $('<h3></h3>').append(link);
            var content = $('<div></div>');
            var section = $('<div></div>').append(title).append(content);
            if (!'id' in setting)
                setting.id = (++status_section_count).toFixed();
            for (var i in setting.entries) {
            }
        }
    });
})();
