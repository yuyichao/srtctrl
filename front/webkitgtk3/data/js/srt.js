function escapeHTML(str) {
    return $('<div/>').text(str).html();
};
$(document).ready(function () {
    Back.Source.connect("event::move", function (src, evt, div) {
        div.text(evt.toString());
    }, $('#mvevent'));
    $('#quit').click(function (ev) {
        Back.Source.quit();
    });
});
