function escapeHTML(str) {
    return $('<div/>').text(str).html();
};
$(document).ready(function () {
    Back.Source.connect("event::move", function (src, evt, div) {
        console.log("length: " + arguments.length);
        console.log(src);
        console.log(evt);
        console.log(div);
        div.text(evt.toString());
    }, $('#mvevent'));
    $('#quit').click(function (ev) {
        Back.Source.quit();
    });
});
