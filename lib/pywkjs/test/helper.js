var count = 0;
console.log(window);
console.log(window.pyobj);
window.button.connect('clicked', function(but) {
    document.write("aaa<br/>");
    for (var i = 0;i < arguments.length;i++) {
        console.log(arguments[i])
    }
    count++;
    but.set_label(count.toString());
}, 1, 2, [1, 2, 3], function() {
    return 1;
})
