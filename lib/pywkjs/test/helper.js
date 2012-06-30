console.log(window);
console.log(window.pyobj);
window.button.connect('clicked', function() {
    document.write("aaa<br/>");
    var ary = [];
    for (var i = 0;i < arguments.length;i++) {
        ary[i] = arguments[i]
    }
    console.log(ary);
})
