$(document).ready(function () {
    draw_models_select(appConfig.handle_key.models);


    $('#model_name').on('change', function () {
        enable_checkpoints();
        $('.waiting-selection-ckpt').removeClass('hide-element');
        $('#feature-div').addClass('hide-element');
        $('#prediction_div').addClass('hide-element');


        let model_name = $(this).val();
        $('#perf').text(appConfig.handle_key.models[model_name]['perf']);
        $('#loss').text(appConfig.handle_key.models[model_name]['loss']);

        $('.waiting-selection').addClass('hide-element');
        $('.loader').removeClass('hide-element');

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

                let $feature_div = $('.pre-scrollable')[0];
                $('#table_features').children().remove();

                if (data.params.hasOwnProperty('image')) {
                    $('#image_upload').removeClass('hide-element');
                    $('#feature-div').addClass('hide-element');
                    let result = 'data:image/' + data.params.extension + ';base64,' + data.params.image;
                    $('.inputDnD').css('background-image', 'url("' + result + '")');
                    appConfig.handle_key['extension'] = data.params.extension;
                    appConfig.handle_key['image'] = data.params.image;

                } else {
                    $('#image_upload').addClass('hide-element');
                    $('#features_div').removeClass('hide-element');
                    $.each(data.params.features, function (key, value) {
                        add_input_number(data.params.types[key], key, value, 0.001);
                    });
                    $.each(data.params.categoricals, function (key, value) {
                        add_input_select(key, data.params.categoricals[key], data.params.features[key]);
                    });
                }

            }
        })
    });

    $('#predict').on('click', function () {
        $('#prediction_div').removeClass('hide-element');
        $('#pred-loader').removeClass('hide-element');
        $('#table_prediction').addClass('hide-element');

        if ($("#image_upload").hasClass("hide-element")) {
            let data_form = $("#predict_form").serializeArray();
            data_form.push({
                name: 'radiob',
                value: $('#table_checkpoints').DataTable().rows({selected: true}).data()[0][0]
            });
            data_form.push({name: 'model_name', value: $('#model_name').val()});
            $.ajax({
                url: "/predict",
                type: 'POST',
                dataType: 'json',
                data: data_form,
                success: function (data) {
                    if (data.hasOwnProperty('error')) {
                        alert(data.error);
                        $('#prediction_div').addClass('hide-element');
                    } else {

                        create_table_predictions(data);
                    }
                    $('#pred-loader').addClass('hide-element');
                    $('#table_prediction').removeClass('hide-element');

                }
            });

        } else {
            var data_form = new FormData($("#predict_form")[0]);
            if ($('#inputFile').val() === '') {
                data_form.set('inputFile', dataURItoBlob('data:image/' + appConfig.handle_key.extension + ';base64,' + appConfig.handle_key.image))
            }
            data_form.append('radiob', $('#table_checkpoints').DataTable().rows({selected: true}).data()[0][0]);
            data_form.append('model_name', $('#model_name').val());
            var ajax = new XMLHttpRequest();
            ajax.open("POST", "/predict");
            ajax.send(data_form);
            ajax.addEventListener("load", completeHandler, false);
            ajax.addEventListener("error", errorHandler, false);
        }

    });
});

//
// function serialize_form() {
//     let data_form = $("#predict_form").serializeArray();
//     data_form.push({name: 'radiob', value: get_checkpoint_selected()});
//     return data_form;
// }


function completeHandler(event) {
    $("#predict_button").attr('disabled', false);
    $("#loading_predict").addClass('hidden');
    $('#table_prediction').removeClass('hide-element');

    let data = JSON.parse(event.target.responseText);
    if (data.hasOwnProperty('error')) {
        alert(data.error);
        $('#prediction_div').addClass('hide-element');
    } else {
        $('#pred-loader').addClass('hide-element');
        $('#prediction_div').removeClass('hide-element');
        create_table_predictions(data);
    }
}


function errorHandler(event) {
    alert('Error prediction');
    $("#predict_button").attr('disabled', false);
    $("#loading_predict").addClass('hidden');
}

function create_table_predictions(data) {
    let rows = [];
    $.each(data, function (key, val) {
        rows.push([key, val])
    });

    if ($.fn.DataTable.isDataTable('#table_prediction')) {
        $('#table_prediction').DataTable().destroy();
        $('#table_prediction tbody').empty();
        $('#table_prediction thead').empty();
    }

    let table_predictions = $('#table_prediction').DataTable({
        data: rows,
        columns: [{title: 'Target'}, {title: 'Prediction'}],
        searching: true,
        'select': false,
        "lengthChange": false,
        "drawCallback": function () {
            if ($(this).DataTable().rows()[0].length <= 10) {
                let id = '#' + $(this).attr('id');
                $(id + '_paginate').remove();
                $(id + '_info').remove();
            }
        }
    })


}