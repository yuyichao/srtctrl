$(function () {
    var npoint_dialog_content = $("#npoint-dialog-content");
    npoint_dialog_content.popup("#npoint-button");
    $("#file-npoint").click($.select_file);
});
