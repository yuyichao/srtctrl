$(function () {
    var npoint_dialog_content = $("#npoint-dialog-content");
    npoint_dialog_content.popup("#npoint-button");
    $("#file-npoint").click(function () {
        $(this).val($.save_file($(this).val()));
    });
});
