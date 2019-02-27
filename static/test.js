$(document).ready(function () {
    draw_models_select(appConfig.handle_key.models);

    $('#model_name').on('change', function () {
        enable_checkpoints();
        $('.waiting-selection-ckpt').removeClass('hide-element');
        $('.waiting-selection').addClass('hide-element');
        $('.loader').removeClass('hide-element');
        $('#feature-div').addClass('hide-element');
        $('#test_file_disabled').removeClass('hide-element');
        $('#graph_test_div').addClass('disabled-custom');
        $('#table_prediction_div').addClass('disabled-custom');
        $('.waiting-test-file').addClass('hide-element');


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
                create_table_test_files(data.params.test_files);

                if (data.params.hasOwnProperty('image')) {
                    $('#image-upload-div').removeClass('hide-element');
                    $('#tabular-upload-div').addClass('hide-element');
                } else {
                    $('#tabular-upload-div').removeClass('hide-element');
                    $('#image-upload-div').addClass('hide-element');

                }
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
                $('.loader-test-file').addClass('hide-element');

                if (data.hasOwnProperty('error')) {
                    alert(data.error);
                } else {
                    $('.waiting-test-file').removeClass('hide-element');
                    appConfig.handle_key.metrics = data.metrics;
                    appConfig.handle_key.targets = data.targets;
                    create_table_predictions(data.predict_table['data'], data.predict_table['columns'])
                    create_graphs(data.metrics, data.targets)
                }

            },
            error: function () {
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
        return [d];
    });
    remove_table('table_test_files');
    let table_test = $('#table_test_files').DataTable({
        data: dataArr,
        columns: [{title: ''}],
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


function uploadZipFile($input) {
    let filename = document.getElementById('image-upload').files[0].name.split('.')[0];
    let f = new FormData();
    f.append('input_file', $input.files[0], $input[0].files[0].name);
    ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
        if (this.readyState === 4 && JSON.parse(this.response).result !== 'ok')
            alert('Upload failed: invalid data format');
        else if (this.readyState === 4 && JSON.parse(this.response).result === 'ok')
            upload_test_table(filename)
    };
    ajax.open("POST", "/upload_test_file");
    ajax.send(f);
}


function uploadCSVFile($input) {
    let filename = document.getElementById('tabular-upload').files[0].name;
    let fReader = new FileReader();
    fReader.readAsBinaryString($input.files[0]);
    fReader.onloadend = function (event) {
        $.ajax({
            url: "/upload_test_file",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            accepts: {
                json: 'application/json',
            },
            data: JSON.stringify({
                'file': event.target.result,
                'model_name': $('#model_name').val(),
                'filename': filename
            }),
            success: function (data) {
                if (data.result !== 'ok')
                    alert(data.result);
                else {
                    upload_test_table(filename);
                    $.notify("File saved", "success");
                }

            }
        })
    }
}

function upload_test_table(filename) {
    $('#table_test_files').DataTable().row.add([filename]).draw();

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

        } else {
            precision_recall_plots();
            roc_plot();
            add_metric('Accuracy', metrics.accuracy.toFixed(3))
        }
    }
}

function add_metric(label, value) {
    $('#metric_acc').html('<b>' + label + '</b>  : ' + value)
}