function create_table(data, id, search_id) {
    var columns = [];
    for (var i = 0; i < data['columns'].length; i++) {
        var column = {title: data['columns'][i]};
        columns.push(column);
    }
    var data_table = $('#' + id).DataTable({
        data: data['data'],
        columns: columns,
        scrollX: true,
        'select': false,
        "lengthChange": false,
        fixedHeader: false,
        deferRender: false,
        "drawCallback": function () {
            if ($(this).DataTable().rows()[0].length <= 10) {
                let id = '#' + $(this).attr('id');
                $(id + '_paginate').remove();
                $(id + '_info').remove();
            }

        }
    });
    $('#' + search_id).keyup(function () {
        data_table.search($(this).val()).draw();
    });
}


function heatmap(id, columns, corr) {
    var min = Math.min.apply(Math, corr.flat());
    var max = Math.max.apply(Math, corr.flat());
    var zval = Math.abs(0 - min / (max - min));

    var data = [
        {
            z: corr,
            x: columns,
            y: columns,
            type: 'heatmap',
            colorscale: [['0.0', 'rgba(214, 39, 40, 0.85)'],
                         [zval.toString(), 'rgba(255, 255, 255, 0.85)'],
                         ['1.0', 'rgba(6,54,21, 0.85)']]

        }
    ];
    var layout = {
        margin: {l: 0, r: 0, t: 25, b: 0},
        xaxis: {automargin: true},
        yaxis: {automargin: true},
    };
    Plotly.newPlot(id, data, layout, {responsive: true});
}


function scatter(feat1, feat2, div, data) {

    var index_x = parseInt($('#' + feat1)[0].value);
    var index_y = parseInt($('#' + feat2)[0].value);
    var x_values = [];
    var y_values = [];
    var x_title = data.columns[index_x];
    var y_title = data.columns[index_y];
    // var plot_title = x_title + '  vs.  ' + y_title;
    for (var i = 0; i < data.data.length; i++) {
        x_values.push(data.data[i][index_x]);
        y_values.push(data.data[i][index_y]);
    }

    var trace1 = {
        x: x_values,
        y: y_values,
        mode: 'markers',
        type: 'scatter'
    };
    var layout = {
        margin: {l: 0, r: 0, t: 25, b: 0},
        xaxis: {automargin: true, title: x_title},
        yaxis: {automargin: true, title: y_title},
    };

    var plot_data = [trace1];
    Plotly.newPlot(div, plot_data, layout, {responsive: true});


}

function histogram(feat1, div, norm, data) {

    var index = parseInt($('#' + feat1)[0].value);
    var bins = norm.bins[index];
    var line = norm.line[index];
    var count = norm.counts[index];

    // var title = data.columns[index];

    var trace_line = {
        x: bins,
        y: line,
        type: 'lines',
    };
    var trace = {
        x: bins,
        y: count,
        type: 'bar',
    };


    var layout = {
        margin: {l: 0, r: 0, t: 25, b: 0},
        xaxis: {automargin: true },
        yaxis: {automargin: true},
        showlegend: false,
    };

    var plot_data = [trace, trace_line];
    Plotly.newPlot(div, plot_data, layout, {responsive: true});


}

function bar_plot(div, x, y) {
    var data = [
        {
            x: x,
            y: y,
            type: 'bar'
        }
    ];
    var layout = {
        margin: {l: 0, r: 0, t: 0, b: 0},
        xaxis: {automargin: true, type: 'category', showticklabels: true},
        yaxis: {automargin: true},
        showlegend: false,
    };
    Plotly.newPlot(div, data, layout, {responsive: true});
}

function line_plot_2_variables(div, x1, y1, x2, y2, name1, name2, xaxis, yaxis) {

    var trace1 = {
        x: x1,
        y: y1,
        mode: 'lines',
        name: name1
    };
    var data = [trace1];
    if (x2.length > 0) {
        var trace2 = {
            x: x2,
            y: y2,
            mode: 'lines',
            name: name2
        };
        data = [trace1, trace2];
    }

    var layout = {
        margin: {l: 10, r: 0, t: 25, b: 25},
        xaxis: {automargin: false, title: xaxis},
        yaxis: {automargin: true, title: yaxis},
    };


    Plotly.newPlot(div, data, layout, {responsive: true});

}