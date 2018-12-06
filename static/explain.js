$(document).ready(function () {
    var predict = appConfig.handle_key.predict_table;
    var graphics = appConfig.handle_key.graphs;
    var regression = true;

    $('#graph_ice_prob').remove();

    h4 = document.createElement("h4");
    if (appConfig.handle_key.type === 'regression') {
        h4.textContent = "Prediction value ";
        create_bar(predict);
    } else {
        h4.textContent = "Prediction probabilities ";
        create_donut(predict);
    }
    document.getElementById('prediction_probabilities_title').appendChild(h4);


    for (var key in graphics) {
        create_graph(graphics[key]['labels'], graphics[key]['data'], key);
    }

    if (appConfig.handle_key.data_type === 'tabular') {

        // TABULAR OPTIONS

        var dataset_rows = get_rows(appConfig.handle_key.features);
        var configs_table = $('#table_features').DataTable({
            data: dataset_rows,
            columns: [{title: 'Feature'}, {title: 'Value'}],
            fixedHeader: false,
            searching: false,
            paginate: false,
            'select': 'single',
            scrollY: 200,
            deferRender: true,
            scroller: true
        });

        $('#select_feature_explain').append(add_select('features', Object.keys(appConfig.handle_key.features)));
        if (!regression) {
            $('#select_feature_explain').append(add_select('labels_ice', appConfig.handle_key.predict_table.columns));
        }


        //  TODO ICE
        if ('columns' in appConfig.handle_key.predict_table)
            regression = false;
        else
            $('#graph_ice_prob').remove();


        $('#features').change(function (e) {
            generate_plots(regression);
        });


        $('#labels_ice').change(function (e) {
            if ('data' in handle_key) {
                let feature_selected = $("#features option:selected").text();
                let cluster = $("#labels_ice option:selected").text();
                let index_label = appConfig.handle_key.predict_table.columns.indexOf(cluster);
                let plot_data = [
                    {
                        x: handle_key.data['data'][feature_selected],
                        y: handle_key.data['data'][appConfig.handle_key.exp_target + '_prob'].map(function (value, index) {
                            return value[index_label];
                        }),
                        type: 'scatter'
                    }
                ];
                Plotly.newPlot('graph_ice_prob', plot_data, get_prob_layout(appConfig, cluster));
            }
        });
        generate_plots(regression);

    } else {

        // IMAGE  OPTIONS
        $('#explain_graps').addClass('hidden');
        $('#select_feature_explain').addClass('hidden');
        let im2 = new Image();
        im2.src = 'data:image/jpg;base64,' + appConfig.handle_key.features;
        im2.style = "width:50%"; //TODO image size
        $("#features_values").append(im2);


    }


});

function create_graph(new_labels, new_data, name) {
    var new_canvas = document.createElement('canvas');
    new_canvas.width = 500;
    document.getElementById('explain_graps').appendChild(new_canvas);
    var ctx = new_canvas.getContext('2d');
    var chart = new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            labels: new_labels,
            datasets: [{
                backgroundColor: get_colors(new_data),
                borderColor: 'rgb(0, 0, 0)',
                data: new_data,
            }]
        },
        // Configuration options go here
        options: {
            legend: {display: false},
            title: {
                display: true,
                text: name
            },
            devicePixelRatio: 0.1,
            responsive: false
        }
    });
}


function get_colors(new_Data) {
    var new_colors = [];
    for (var i = 0; i < new_Data.length; i++) {
        if (new_Data[i] < 0) {
            new_colors.push('#ca3e09');
        } else {
            new_colors.push('#4886ec');
        }
    }
    return new_colors;
}


function get_rows(dictionary) {
    let dataset_rows = [];
    Object.keys(dictionary).forEach(function (key) {
        dataset_rows.push([key, dictionary[key]])
    });
    return dataset_rows;
}


function create_bar(predict) {
    var ctx = document.getElementById("probs").getContext('2d');
    var barChartData = {
        labels: ['Prediction = ' + predict['predicted_value']],
        datasets: [{
            backgroundColor: '#4886ec',
            data: [
                predict["min_value"]
            ]
        }, {

            backgroundColor: '#4886ec',
            data: [
                predict['predicted_value']
            ]
        }]
    };

    var myBarChart = new Chart(ctx, {
        type: 'bar',
        data: barChartData,
        options: {
            tooltips: {
                callbacks: {
                    label: function () {
                        return ''
                    }
                }
            },
            legend: {display: false},
            responsive: false,
            scales: {
                xAxes: [{
                    stacked: true,
                }],
                yAxes: [{
                    stacked: true,
                    display: true,
                    ticks: {
                        beginAtZero: false,
                        min: predict['min_value'],
                        steps: 10,
                        stepValue: (predict['max_value'] - predict['min_value']) / 10,
                        max: predict['max_value'],
                    }
                }]
            }
        }
    });
}


function get_donut_colors(new_Data) {
    var new_colors = [];
    var colors_palette = ['#e6194b', '#3cb44b', '#ffbc0a', '#0082c8', '#f58231',
        '#911eb4', '#9cd1f0', '#f032e6', '#fabebe', '#008080', '#800000', '#000080'];
    for (var i = 0; i < new_Data.length; i++) {
        if (i > colors_palette.length) {
            new_colors.push('#' + Math.floor(Math.random() * 16777215).toString(16));
        }
        new_colors.push(colors_palette[i]);
    }
    return new_colors;
}


function create_donut(predict) {
    var new_data = {
        datasets: [{
            label: 'Prediction',
            data: predict['data'],
            backgroundColor: get_donut_colors(predict['data'])
        }],
        labels: predict['columns'],

    };
    var ctx = document.getElementById("probs").getContext('2d');
    var myDoughnutChart = new Chart(ctx, {
        type: 'doughnut',
        data: new_data,
        options: {
            responsive: false,
            title: {
                display: true,
                text: 'Prediction probabilities'
            },
        }
    });
}


function add_select(label_name, options) {
    let selectList = $("<select>")
        .attr('id', label_name)
        .attr('name', label_name);
    let option_list = options.map((key) => $('<option>').val(key).text(key));
    selectList.append(option_list);
    return selectList
}

function get_prob_layout(appConfig, cluster) {
    return {
        title: 'Target Conditional Probability',
        xaxis: {
            title: $("#features option:selected").text(),
            titlefont: {
                size: 14,
                color: '#7f7f7f'
            }
        },
        yaxis: {
            range: [0, 1],
            title: 'prob_' + appConfig.handle_key.exp_target + '_' + cluster,
            titlefont: {
                size: 10,
                color: '#7f7f7f'
            }
        }
    };

}

function generate_plots(regression) {
    var feature_selected = $("#features option:selected").text();
    $.ajax({
        url: "/explain_feature",
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        accepts: {
            json: 'application/json',
        },
        data: JSON.stringify({
            'explain_feature': feature_selected,
            'features_values': appConfig.handle_key.features,
            'model': appConfig.handle_key.model,
            'exp_target': appConfig.handle_key.exp_target
        }),
        success: function (data) {
            if (data['data'] !== 'Error') {
                handle_key['data'] = data;
                let plot_data = [
                    {
                        x: data['data'][feature_selected],
                        y: data['data'][appConfig.handle_key.exp_target],
                        // error_y: {
                        //     type: 'data',
                        //     array: [1, 2, 3],
                        //     visible: true
                        // },
                        type: 'scatter'
                    }
                ];
                let layout = {
                    title: 'Individual Conditional Expectation',
                    xaxis: {
                        title: feature_selected,
                        titlefont: {
                            size: 14,
                            color: '#7f7f7f'
                        }
                    },
                    yaxis: {
                        title: appConfig.handle_key.exp_target,
                        titlefont: {
                            size: 14,
                            color: '#7f7f7f'
                        }
                    }
                };
                Plotly.newPlot('graph_ice_scatter', plot_data, layout);
                if (!regression) {
                    let cluster = $("#labels_ice option:selected").text();
                    let index_label = appConfig.handle_key.predict_table.columns.indexOf(cluster);
                    let plot_data2 = [
                        {
                            x: data['data'][feature_selected],
                            y: data['data'][appConfig.handle_key.exp_target + '_prob'].map(function (value, index) {
                                return value[index_label];
                            }),
                            type: 'scatter'
                        }
                    ];
                    Plotly.newPlot('graph_ice_prob', plot_data2, get_prob_layout(appConfig, cluster));
                }

            } else {
                alert('Error');
            }
        }
    })
}