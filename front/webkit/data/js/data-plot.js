$(function () {
    var data_plot_region = $('#data-plot-region');
    var spectrum_plot = $('#spectrum-plot');
    var iface;
    data_plot_region.resize(function () {
        spectrum_plot.outerHeight(data_plot_region.height());
        spectrum_plot.outerWidth(data_plot_region.width() / 3);
    });
    iface = spectrum_plot.plot_region();
    SrtIFace.connect('signal::radio', function (name, value, props) {
        try {
            iface.set_xlimit.apply(this, value.freq_range);
            iface.set_plot('spectrum', value.data);
        } catch (e) {
            console.log(e);
            console.log(JSON.stringify(e));
        }
    });
})
