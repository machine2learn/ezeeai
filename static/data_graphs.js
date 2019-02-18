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
    var data = [
        {
            z: corr,
            x: columns,
            y: columns,
            type: 'heatmap',

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
    var plot_title = x_title + '  vs.  ' + y_title;
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

    var title = data.columns[index];

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
        xaxis: {automargin: true},
        yaxis: {automargin: true},
        showlegend: false,
    };

    var plot_data = [trace, trace_line];
    Plotly.newPlot(div, plot_data, layout, {responsive: true});


}
