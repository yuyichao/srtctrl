$(function () {
    $(".header-button").button();
    Back.Source.connect("event::move", function (src, evt, div) {
        div.text(evt.az + ", " + evt.el);
    }, $('#mvevent'));
    $('#quit-button').click(function (ev) {
        Back.Source.quit();
        return false;
    });
});
