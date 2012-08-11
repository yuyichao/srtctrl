$(function () {
    var props_hidden = false;
    var props_region = $("#props-region");
    var props_slider = $("#props-region-slider");
    var real_props_region = $("#real-props-region");
    function props_region_size() {
        if (props_hidden)
            return;
        var width = props_region.width() - props_slider.width();
        real_props_region.width(width);
    };
    props_region.resize(props_region_size);
    props_slider.resize(props_region_size);
    props_region_size();
    props_slider.click(function () {
        if (props_hidden) {
            $("#plot-region").animate({width: "69%"}, {
                speed: 500
            });
            props_slider.css({
                "float": "left"
            });
            props_region.animate({width: "29%"}, {
                speed: 500,
                complete: function () {
                    props_hidden = false;
                    real_props_region.show();
                    props_slider.removeClass(
                        "v-slider-left"
                    ).addClass(
                        "v-slider-right"
                    );
                }
            });
        } else {
            props_hidden = true;
            real_props_region.hide();
            props_region.animate({width: "2%"}, {
                speed: 500,
                complete: function () {
                    props_slider.css({
                        "float": "right"
                    }).removeClass(
                        "v-slider-right"
                    ).addClass(
                        "v-slider-left"
                    );
                }
            });
            $("#plot-region").animate({width: "97%"}, {
                speed: 500
            });
        }
    });
});
