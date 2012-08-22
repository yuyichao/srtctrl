$(function () {
    $('#feedback-button').click(function () {
        open('https://github.com/yuyichao/srtctrl/issues/new');
        return true;
    });
    $('#doc-button').click(function () {
        open('https://github.com/yuyichao/srtctrl/wiki');
        return true;
    });
    $('#dev-tool-button').click(function () {
        SrtCall('dev');
    });
});
