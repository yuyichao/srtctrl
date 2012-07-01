document.write(Back.a);
document.write('<br/>');
document.write(Back);
document.write('<br/>');
function escapeHTML(str) {
    return $('<div/>').text(str).html()
};
document.write(escapeHTML(UI.Gtk));
document.write('<br/>');
document.write(escapeHTML(UI.window));
document.write('<br/>');
document.write(escapeHTML(UI.webview));
document.write('<br/>');
