// $(document).ready(function () {
//     var configs_table = $('#test_table_features').DataTable({
//         data: appConfig.handle_key.predict_table['data'],
//         columns: appConfig.handle_key.predict_table['columns'],
//         scrollX: true
//     });
//     var targets = appConfig.handle_key.targets;
//     var len = targets.length;
//     $('#exp_label').append('<select  id="exp_target" name="exp_target"> Target: </select>');
//     var i;
//     for (i = 0; i < len; i++) {
//         $('#exp_target').append(new Option(targets[i], i));
//     }
//
//
//     $("#exp_target").change(function () {
//         multi_regression_plots(parseInt(get_target_idx()));
//         $('#metric_acc').text('R2 score : ' + appConfig.handle_key.metrics.r2_score[get_target_idx()]);
//     });
//
//     if (appConfig.handle_key.metrics != null) {
//         if ('y_pred' in appConfig.handle_key.metrics) {
//             var dim = [appConfig.handle_key.metrics.y_true.length, appConfig.handle_key.metrics.y_true[0].length];
//             if (typeof dim[1] == "undefined") {
//                 regression_plots(appConfig.handle_key.metrics.y_true, appConfig.handle_key.metrics.y_pred);
//             } else {
//                 multi_regression_plots(parseInt(get_target_idx()));
//             }
//             if (appConfig.handle_key.metrics.r2_score.length > 1) {
//                 $('#metric_acc').text('R2 score : ' + appConfig.handle_key.metrics.r2_score[0].toFixed(3));
//             } else {
//                 $('#metric_acc').text('R2 score : ' + appConfig.handle_key.metrics.r2_score.toFixed(3));
//             }
//
//         } else {
//             precision_recall_plots();
//             roc_plot();
//             $('#metric_acc').text('Accuracy : ' + appConfig.handle_key.metrics.accuracy.toFixed(3));
//         }
//
//     }
//
//
//     //
//     // }else()
//
//
// });

function get_target_idx() {
    var sel = document.getElementById('exp_target');
    return sel.options[sel.selectedIndex].value;
}

function arr_diff(a1, a2) {
    var diff = [];
    for (var i = 0; i < a1.length; i++) {
        diff.push(a1[i] - a2[i])
    }
    return diff;
}

function regression_plots(y_true, y_pred) {
    var filtered_y_true = y_true.filter(function (value) {
        return !Number.isNaN(value);
    });
    var filtered_y_pred = y_pred.filter(function (value) {
        return !Number.isNaN(value);
    });
    var min = Math.min(Math.min(...filtered_y_true), Math.min(...filtered_y_pred)) - 0.1;
    var max = Math.max(Math.max(...filtered_y_true), Math.max(...filtered_y_pred)) + 0.1;
    var trace1 = {
        x: [min, max],
        y: [min, max],
        type: 'scatter',
        mode: 'lines',
        line: {
            dash: 'dot',
            width: 2,
            color: "rgb(1,1,1)",
        }
    };
    var trace2 = {
        x: y_true,
        y: y_pred,
        type: 'scatter',
        mode: 'markers'
    };
    var data = [trace1, trace2];
    var layout = {
        // title: 'Predicted vs. Actual Response',
        font: {
            family: '"Montserrat", sans-serif',
            size: 11
        },
        showlegend: false,
        xaxis: {
            title: 'True response'
        },
        yaxis: {
            title: 'Predicted response'
        },
        margin: {
            t: 50,
            pad: 4
        },
        plot_bgcolor: 'rgba(0,0,0,0)'
    }
    Plotly.newPlot('recall_div', data, layout, {responsive: true});


    var dif = arr_diff(y_true, y_pred);
    var abs = Math.max.apply(null, dif.map(Math.abs)) + 1;

    var layout2 = {
        // title: 'Difference',
        font: {
            family: '"Montserrat", sans-serif',
            size: 11
        },
        showlegend: false,
        xaxis: {
            title: 'True response'
        },
        yaxis: {
            title: 'Predicted - True',
            range: [-abs, abs]
        },
        margin: {
            t: 50,
            pad: 4
        },
        plot_bgcolor: 'rgba(0,0,0,0)'
    }
    var data2 = [
        {
            x: [...Array(y_pred.length).keys()],
            y: dif,
            type: 'scatter',
            mode: 'markers'
        }
    ];
    Plotly.newPlot('roc_div', data2, layout2, {responsive: true});
}

function multi_regression_plots(target_idx) {
    var y_true = appConfig.handle_key.metrics.y_true.map(function (value, index) {
        return value[target_idx];
    });
    var y_pred = appConfig.handle_key.metrics.y_pred.map(function (value, index) {
        return value[target_idx];
    });
    regression_plots(y_true, y_pred)
}

function precision_recall_plots() {
    if ('bin' in appConfig.handle_key.metrics.pr.recall) {
        var trace1 = {
            x: appConfig.handle_key.metrics.pr.recall['bin'],
            y: appConfig.handle_key.metrics.pr.precision['bin'],
            mode: 'lines',
            name: 'precision-recall (' + Math.round(appConfig.handle_key.metrics.pr.average_precision.bin * 100) / 100 + ')'
        };
        var data = [trace1];

    } else {
        var trace1 = {
            x: appConfig.handle_key.metrics.pr.recall['micro'],
            y: appConfig.handle_key.metrics.pr.precision['micro'],
            mode: 'lines',
            name: 'micro-average precision-recall (' + Math.round(appConfig.handle_key.metrics.pr.average_precision.micro * 100) / 100 + ')'
        };
        var data = [trace1];
        for (class_name in appConfig.handle_key.metrics.pr.precision) {
            if (class_name !== 'micro') {
                var trace2 = {
                    x: appConfig.handle_key.metrics.pr.recall[class_name],
                    y: appConfig.handle_key.metrics.pr.precision[class_name],
                    mode: 'lines',
                    name: 'prec-recall class ' + class_name + ' (' + Math.round(appConfig.handle_key.metrics.pr.average_precision[class_name] * 100) / 100 + ')'
                };
                data.push(trace2);
            }
        }
    }


    var layout = {
        // title: 'Precision-Recall',
        font: {
            family: '"Montserrat", sans-serif',
            size: 11
        },
        showlegend: true,
        // legend: {
        //     y: -0.3,
        //     "orientation": "h"
        // },
        legend: {
            x: 1.1,
            y: 0.5
        },
        xaxis: {
            title: 'Recall',
            range: [0, 1]
        },
        yaxis: {
            title: 'Precision',
            range: [0, 1]
        },
        margin: {
            l: 50,
            r: 50,
            t: 50,
            pad: 4
        },
        plot_bgcolor: 'rgba(0,0,0,0)'
    };
    Plotly.newPlot('recall_div', data, layout, {responsive: true});
}


function roc_plot() {
    if ('bin' in appConfig.handle_key.metrics.roc.fpr) {
        var trace1 = {
            x: appConfig.handle_key.metrics.roc.fpr['bin'],
            y: appConfig.handle_key.metrics.roc.tpr['bin'],
            mode: 'lines',
            name: 'ROC curve (' + Math.round(appConfig.handle_key.metrics.roc.roc_auc.bin * 100) / 100 + ')'
        };

        var trace2 = {
            x: [0, 1],
            y: [0, 1],
            showlegend: false,
            type: 'scatter',
            mode: 'lines',
            line: {
                dash: 'dot',
                width: 2,
                color: "rgb(1,1,1)"
            },
        };
        var data = [trace1, trace2];

    } else {
        var trace1 = {
            x: appConfig.handle_key.metrics.roc.fpr['micro'],
            y: appConfig.handle_key.metrics.roc.tpr['micro'],
            mode: 'lines',
            name: 'micro-average ROC (' + Math.round(appConfig.handle_key.metrics.roc.roc_auc.micro * 100) / 100 + ')'
        };
        var trace2 = {
            x: appConfig.handle_key.metrics.roc.fpr['macro'],
            y: appConfig.handle_key.metrics.roc.tpr['macro'],
            mode: 'lines',
            name: 'macro-average ROC (' + Math.round(appConfig.handle_key.metrics.roc.roc_auc.macro * 100) / 100 + ')'
        };
        var trace3 = {
            x: [0, 1],
            y: [0, 1],
            showlegend: false,
            type: 'scatter',
            mode: 'lines',
            line: {
                dash: 'dot',
                width: 2,
                color: "rgb(1,1,1)"
            },
        };
        var data = [trace1, trace2, trace3];

        for (class_name in appConfig.handle_key.metrics.roc.fpr) {
            if (class_name !== 'micro' && class_name !== 'macro') {
                var trace4 = {
                    x: appConfig.handle_key.metrics.roc.fpr[class_name],
                    y: appConfig.handle_key.metrics.roc.tpr[class_name],
                    mode: 'lines',
                    name: 'ROC of class ' + class_name + ' (' + Math.round(appConfig.handle_key.metrics.roc.roc_auc[class_name] * 100) / 100 + ')'
                };
                data.push(trace4);
            }
        }
    }


    var layout = {
        // title: 'Receiver operating characteristic (ROC)',
        font: {
            family: '"Montserrat", sans-serif',
            size: 11
        },
        showlegend: true,
        legend: {
            x: 1.1,
            y: 0.5
        },
        xaxis: {
            title: 'False Positive Rate',
            range: [0, 1]
        },
        yaxis: {
            title: 'True Positive Rate',
            range: [0, 1]
        },
        margin: {
            l: 50,
            r: 50,
            t: 50,
            pad: 4
        },
        plot_bgcolor: 'rgba(0,0,0,0)'
    };
    Plotly.newPlot('roc_div', data, layout, {responsive: true});
}
