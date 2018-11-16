$(document).ready(function () {
    create_table(appConfig.handle_key['data']);
    create_selectors();
    create_graph1();
    create_graph2();
    create_graph3();
    hidden_by_ids(['div_graph2', 'div_graph3']);

    document.getElementById("selector_graphs_list").onchange = function () {
        if (document.getElementById("selector_graphs_list").value === 'graph1') {
            show_by_ids(['div_graph1']);
            hidden_by_ids(['div_graph2', 'div_graph3']);
        } else if (document.getElementById("selector_graphs_list").value === 'graph2') {
            show_by_ids(['div_graph2']);
            hidden_by_ids(['div_graph1', 'div_graph3']);
        } else {
            show_by_ids(['div_graph3']);
            hidden_by_ids(['div_graph1', 'div_graph2']);
        }
    };
    document.getElementById("feature1").onchange = function () {
        create_graph1();
    };
    document.getElementById("feature2").onchange = function () {
        create_graph1();
    };
    document.getElementById("feature3").onchange = function () {
        create_graph2();
    };

});

function create_table(data) {
    var columns = [];
    for (var i = 0; i < data['columns'].length; i++) {
        var column = {title: data['columns'][i]};
        columns.push(column);
    }
    var data_table = $('#table_data').DataTable({
        data: data['data'],
        columns: columns,
        scrollX: true
    });
}

function create_selectors() {
    create_selector("selector1", "feature1");
    create_selector("selector2", "feature2");
    create_selector("selector3", "feature3");
    create_selector_graphs();
}

function create_selector_graphs() {
    var sel = document.getElementById("selector_graphs");
    var selectList = document.createElement("select");
    selectList.id = "selector_graphs_list";
    sel.appendChild(selectList);
    var options = ['ScatterPlot', 'Histogram', 'Heatmap'];
    for (var i = 0; i < options.length; i++) {
        var option = document.createElement("option");
        var grap_number = i + 1;
        option.value = 'graph' + grap_number;
        option.text = options[i];
        selectList.appendChild(option);
    }
}

function create_selector(id_selector, id_feature) {
    var sel = document.getElementById(id_selector);
    var selectList = document.createElement("select");
    selectList.id = id_feature;
    sel.appendChild(selectList);
    var options = appConfig.handle_key['data']['columns'];
    for (var i = 0; i < options.length; i++) {
        var option = document.createElement("option");
        option.value = i;
        option.text = options[i];
        selectList.appendChild(option);
    }
}


function create_graph1() {
    var index_x = parseInt($('#feature1')[0].value);
    var index_y = parseInt($('#feature2')[0].value);
    var x_values = [];
    var y_values = [];
    var x_title = appConfig.handle_key['data']['columns'][index_x];
    var y_title = appConfig.handle_key['data']['columns'][index_y];
    var plot_title = x_title + '  Vs.  ' + y_title;
    for (var i = 0; i < appConfig.handle_key['data']['data'].length; i++) {
        x_values.push(appConfig.handle_key['data']['data'][i][index_x]);
        y_values.push(appConfig.handle_key['data']['data'][i][index_y]);
    }
    scatter_plot(x_values, y_values, 'graph1', x_title, y_title, plot_title);
}

function create_graph2() {
    var index = parseInt($('#feature3')[0].value);
    var bins = appConfig.handle_key.norm.bins[index];
    var line = appConfig.handle_key.norm.line[index];
    var count = appConfig.handle_key.norm.counts[index];
    var values = [];
    var title = appConfig.handle_key['data']['columns'][index];
    var plot_title = 'Histogram ' + title;
    for (var i = 0; i < appConfig.handle_key['data']['data'].length; i++) {
        values.push(appConfig.handle_key['data']['data'][i][index]);
    }
    histogram_plot(values, 'graph2', title, plot_title, bins, line, count);
}

function create_graph3() {
    var x = appConfig.handle_key['data']['columns'];
    var z = appConfig.handle_key.corr;
    heatmap_plot(x, z, 'graph3')
}


function scatter_plot(array_x, array_y, div_name, x_title, y_title, plot_title) {
    var trace1 = {
        x: array_x,
        y: array_y,
        mode: 'markers',
        type: 'scatter'
    };
    var layout = {
        title: plot_title,
        xaxis: {
            title: x_title
        },
        yaxis: {
            title: y_title
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    };
    var data = [trace1];
    Plotly.newPlot(div_name, data, layout);
}


function histogram_plot(data, div_name, title, plot_title, bins, line, count) {
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
        title: plot_title,
        showlegend: false,
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'

    };
    var data = [trace, trace_line];
    Plotly.newPlot(div_name, data, layout);

}

function heatmap_plot(x, z, divname) {
    var data = [
        {
            z: z,
            x: x,
            y: x,
            type: 'heatmap'
        }
    ];
    var layout = {
        title: 'Correlation Matrix',
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    };
    Plotly.newPlot(divname, data, layout);

}


function show_by_ids(ids) {
    for (let i = 0; i < ids.length; i++) {
        document.getElementById(ids[i]).classList.remove('hidden');
    }
}

function hidden_by_ids(ids) {
    for (let i = 0; i < ids.length; i++) {
        document.getElementById(ids[i]).classList.add('hidden');
    }
}