function create_graph(new_labels, new_data, name) {
    var new_canvas = document.createElement('canvas');
    new_canvas.width = 500;
    document.getElementById('explain_graphs').appendChild(new_canvas);
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
            new_colors.push('#ff890a');
        } else {
            new_colors.push('#019EBE');
        }
    }
    return new_colors;
}


function create_bar(predict) {
    var ctx = document.getElementById("probs").getContext('2d');

    if (predict["min_value"] < 0) {
        var my_datasets = [
            {
                backgroundColor: '#019EBE',
                data: [
                    predict["min_value"]
                ]
            },
            {
                backgroundColor: '#019EBE',
                data: [
                    predict['predicted_value']
                ]
            }]
    } else {
        var my_datasets = [
            {
                backgroundColor: '#019EBE',
                data: [
                    predict['predicted_value']
                ],
                fill: false,
                tension: 0
            }]
    }
    var barChartData = {
        labels: ['Prediction = ' + predict['predicted_value']],
        datasets: my_datasets
    };


    var myBarChart = new Chart(ctx, {
        type: 'bar',
        data: barChartData,
        responsive: true,
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
                    // stacked: true,
                    // display: true,

                    ticks: {
                        min: predict['min_value'],
                        max: predict['max_value'],
                        callback: function (value, index, values) {
                            if (index === values.length - 1) return predict['min_value'];
                            else if (index === 0) return predict['max_value'];
                            else return '';
                        }
                        // beginAtZero: false,
                        // min: predict['min_value'],
                        // // steps: 10,
                        // // stepValue: (predict['max_value'] - predict['min_value']) / 10,
                        // max: predict['max_value'],
                    }
                }]
            }
        }
    });
}


function get_donut_colors(new_Data) {
    var new_colors = [];
    var colors_palette = ['#0190af',
        '#ffbc0a',
        '#2fc6a2',
        '#0c6cc8',
        '#f58231',
        '#c47ade',
        '#9cd1f0',
        '#f0777f',
        '#fabebe',
        '#7d89d5',
        '#67b754',
        '#80447e'];
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

//
// function generate_plots(regression) {
//     var feature_selected = $("#features option:selected").text();
//     $.ajax({
//         url: "/explain_feature",
//         type: 'POST',
//         dataType: 'json',
//         contentType: 'application/json;charset=UTF-8',
//         accepts: {
//             json: 'application/json',
//         },
//         data: JSON.stringify({
//             'explain_feature': feature_selected,
//             'features_values': appConfig.handle_key.features,
//             'model': appConfig.handle_key.model,
//             'exp_target': appConfig.handle_key.exp_target
//         }),
//         success: function (data) {
//             if (data['data'] !== 'Error') {
//                 handle_key['data'] = data;
//                 let plot_data = [
//                     {
//                         x: data['data'][feature_selected],
//                         y: data['data'][appConfig.handle_key.exp_target],
//                         type: 'scatter'
//                     }
//                 ];
//                 let layout = {
//                     title: 'Individual Conditional Expectation',
//                     xaxis: {
//                         title: feature_selected,
//                         titlefont: {
//                             size: 14,
//                             color: '#7f7f7f'
//                         }
//                     },
//                     yaxis: {
//                         title: appConfig.handle_key.exp_target,
//                         titlefont: {
//                             size: 14,
//                             color: '#7f7f7f'
//                         }
//                     }
//                 };
//                 Plotly.newPlot('graph_ice_scatter', plot_data, layout);
//                 if (!regression) {
//                     let cluster = $("#labels_ice option:selected").text();
//                     let index_label = appConfig.handle_key.predict_table.columns.indexOf(cluster);
//                     let plot_data2 = [
//                         {
//                             x: data['data'][feature_selected],
//                             y: data['data'][appConfig.handle_key.exp_target + '_prob'].map(function (value, index) {
//                                 return value[index_label];
//                             }),
//                             type: 'scatter'
//                         }
//                     ];
//                     Plotly.newPlot('graph_ice_prob', plot_data2, get_prob_layout(appConfig, cluster));
//                 }
//
//             } else {
//                 alert('Error');
//             }
//         }
//     })
// }