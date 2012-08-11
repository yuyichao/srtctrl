$(function () {
    var npoint_dialog = $("#npoint-dialog");
    var npoint_dialog_content = $("#npoint-dialog-content");
    add_dialog($("#npoint-button"), npoint_dialog);
    npoint_dialog.resize(function () {
        npoint_dialog_content.outerHeight(
            $(this).height()
        );
        return false;
    });
});
