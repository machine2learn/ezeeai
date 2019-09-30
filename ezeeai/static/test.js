$(document).ready(function () {
    draw_models_select(appConfig.handle_key.models);
    $('#model_name').on('change', function () {
        enable_checkpoints();
        hide_waiting();
        clean_upload_log();

        $.ajax({
            url: "/params_predict",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({'model_name': $(this).val()}),
            success: function (data) {
                $('.loader').addClass('hide-element');
                $('.visualization').removeClass('hide-element');
                if ($.fn.DataTable.isDataTable('#table_checkpoints')) {
                    $('#table_checkpoints').DataTable().destroy();
                    $('#table_checkpoints tbody').empty();
                    $('#table_checkpoints thead').empty();
                }

                create_checkpoint_table(data.checkpoints, data.metric);
                $('#features_div').addClass('disabled-custom');

                if (data.params.hasOwnProperty('image')) {
                    $('#image-upload-div').removeClass('hide-element');
                    $('#tabular-upload-div').addClass('hide-element');
                    appConfig.has_test = data.has_test;

                } else {
                    $('#tabular-upload-div').removeClass('hide-element');
                    $('#image-upload-div').addClass('hide-element');
                    appConfig.has_test = false;

                }
                create_table_test_files(data.params.test_files);

            },
            error: function () {
                $('.loader').addClass('hide-element');
                $.notify('Checkpoints not available')

            }
        })
    });

    $("#image-upload").on('change', function () {
        uploadZipFile(this);
    });
    $("#tabular-upload").on('change', function () {
        uploadCSVFile(this);
    });

    $('#test').on('click', function () {
        let test_file = $('#table_test_files').DataTable().rows({selected: true}).data()[0][0];
        let checkpoint = $('#table_checkpoints').DataTable().rows({selected: true}).data()[0][0];
        let model_name = $('#model_name').val();
        $('#graph_test_div').removeClass('disabled-custom');
        $('#table_prediction_div').removeClass('disabled-custom');

        $('.waiting-test-file').addClass('hide-element');
        $('.loader-test-file').removeClass('hide-element');
        $('#large_test').addClass('hide-element');

        $.ajax({
            url: "/test",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            accepts: {
                json: 'application/json',
            },
            // timeout:12000,
            data: JSON.stringify({
                'filename': test_file,
                'model_name': model_name,
                'checkpoint': checkpoint
            }),
            success: function (data) {
                if (data.hasOwnProperty('error')) {
                    alert(data.error);
                    $('.loader-test-file').addClass('hide-element');
                } else {
                    if ((data.predict_table['data'].length) > 1000 && (data.metrics.hasOwnProperty('y_pred'))) {
                        // add message and download complete csv link
                        $('#large_test_message').text('* Only 1000 of ' + data.predict_table['data'].length + ' are shown.');
                        $('#large_test').removeClass('hide-element');

                        appConfig.handle_key.long_data = data.predict_table['data'];
                        appConfig.handle_key.columns = data.predict_table['columns'];

                        data.predict_table['data'] = data.predict_table['data'].slice(0, 1000);
                        data.metrics.y_pred = data.metrics.y_pred.slice(0, 1000);
                        data.metrics.y_true = data.metrics.y_true.slice(0, 1000);
                    } else {
                        $('#large_test').addClass('hide-element');
                    }
                    $('.loader-test-file').addClass('hide-element');

                    $('.waiting-test-file').removeClass('hide-element');
                    create_table_predictions(data.predict_table['data'], data.predict_table['columns']);
                    if (Object.keys(data['metrics']).length > 0) {
                        appConfig.handle_key.metrics = data.metrics;
                        appConfig.handle_key.targets = data.targets;
                        create_graphs(data.metrics, data.targets);
                        $('#graph_test_div').removeClass('hide-element');
                    } else {
                        $('#graph_test_div').addClass('hide-element');
                    }
                }

            },
            error: function (e) {
                $('.loader-test-file').addClass('hide-element');
                $.notify('Test not successful')

            }
        })


    });
});

function remove_table(id) {
    if ($.fn.DataTable.isDataTable('#' + id)) {
        $('#' + id).DataTable().destroy();
        $('#' + id + ' tbody').empty();
        $('#' + id + ' thead').empty();
    }
}

function create_table_predictions(data, columns) {
    remove_table('test_table_features');
    $('#test_table_features').DataTable({
        data: data,
        columns: columns,
        scrollX: true,
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'csv',
                title: 'pred-' + $('#table_test_files').DataTable().rows({selected: true}).data()[0][0]
            },
        ],
        initComplete: function () {
            $('.buttons-csv').html('<span class="fi flaticon-download" data-toggle="tooltip" title="Export To CSV"/></span>Download CSV ')
        }
    });

}

function create_table_test_files(data) {
    let dataArr = data.map(function (d) {
        let link = '<a data-id=' + d + ' onclick="deleteTestFile(this)" ><i class="fi flaticon-trash"></i></a>';
        return [d, link];
    });
    if (appConfig.has_test)
        dataArr.push(['TEST FROM SPLIT', '']);


    remove_table('table_test_files');
    let table_test = $('#table_test_files').DataTable({
        data: dataArr,
        columns: [{title: ''}, {title: '', width: "5%", 'sClass': 'trash-icon'}],
        // searching: true,
        'select': 'single',
        "lengthChange": false,
        "drawCallback": function () {
            if ($(this).DataTable().rows()[0].length <= 10) {
                let id = '#' + $(this).attr('id');
                $(id + '_paginate').remove();
                $(id + '_info').remove();
            }
        }
    }).on('select', function () {
        $('#test').attr('disabled', false);

    })
        .on('deselect', function () {
            $('#test').attr('disabled', true);
        });

}


function upload_test_table(filename) {
    $('#table_test_files').DataTable().row.add([filename, '<a data-id=' + filename + ' onclick="deleteTestFile(this)" ><i class="fi flaticon-trash"></i></a>']).draw();
}

function create_graphs(metrics, targets) {
    $('#exp_target').remove();
    $('#exp_label').remove();

    let len = targets.length;


    $('#exp_div').append('<label id="exp_label" class="cust_label" for="exp_target"><b> Target</b> </label>')
        .append('<select  id="exp_target" name="exp_target" class="form-control input-inline"></select>');

    for (let i = 0; i < len; i++) {
        $('#exp_target').append(new Option(targets[i], i));
    }

    $("#exp_target").change(function () {
        multi_regression_plots(parseInt(get_target_idx()));
        add_metric('R2 score', metrics.r2_score[get_target_idx()])
    });

    if (metrics != null) {
        if ('y_pred' in metrics) {
            let dim = [metrics.y_true.length, metrics.y_true[0].length];
            if (typeof dim[1] === "undefined") {
                regression_plots(metrics.y_true, metrics.y_pred);
            } else {
                multi_regression_plots(parseInt(get_target_idx()));
            }
            if (metrics.r2_score.length > 1) {
                add_metric('R2 score', metrics.r2_score[0].toFixed(3))
            } else {
                add_metric('R2 score', metrics.r2_score.toFixed(3))
            }
            show_regression_graphs_titles()
        } else {
            precision_recall_plots();
            roc_plot();
            add_metric('Accuracy', metrics.accuracy.toFixed(3));
            show_classification_graphs_titles()
        }
    }
}

function show_regression_graphs_titles() {
    $('#regr_graph1').removeClass('hide-element');
    $('#regr_graph2').removeClass('hide-element');

    $('#class_graph1').addClass('hide-element');
    $('#class_graph2').addClass('hide-element');
}

function show_classification_graphs_titles() {
    $('#regr_graph1').addClass('hide-element');
    $('#regr_graph2').addClass('hide-element');

    $('#class_graph1').removeClass('hide-element');
    $('#class_graph2').removeClass('hide-element');
}

function add_metric(label, value) {
    $('#metric_acc').html('<b>' + label + '</b>  : ' + value)
}

function download_large_dataset() {
    if (typeof appConfig.handle_key.long_data !== 'undefined') {
        let test_file = $('#table_test_files').DataTable().rows({selected: true}).data()[0][0].split('.')[0] + '_pred';
        let columns = appConfig.handle_key.columns.map(function (k) {
            return k['title']
        });
        exportCSVFile(columns, appConfig.handle_key.long_data, test_file)
    } else {
        $('#large_test').addClass('hide-element');
    }
}

function hide_waiting() {
    $('.waiting-selection-ckpt').removeClass('hide-element');
    $('.waiting-selection').addClass('hide-element');
    $('.loader').removeClass('hide-element');
    $('#feature-div').addClass('hide-element');
    $('#test_file_disabled').removeClass('hide-element');
    $('#graph_test_div').addClass('disabled-custom');
    $('#table_prediction_div').addClass('disabled-custom');
    $('.waiting-test-file').addClass('hide-element');
    $('#large_test').addClass('hide-element');

}