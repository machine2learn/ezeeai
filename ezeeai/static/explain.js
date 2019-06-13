$(document).ready(function () {
    draw_models_select(appConfig.handle_key.models);


    $('#model_name').on('change', function () {
        enable_checkpoints();
        clear_graphs();
        $('#feature-div').addClass('hide-element');
        $('#prediction_div').addClass('hide-element');
        $('#features_div').removeClass('disabled-custom');


        if (appConfig.handle_key.grey_scale.indexOf($('#model_name').val()) >= 0) {
             $.notify('Grayscale images are not supported', "error");
            $('#features_div').addClass('disabled-custom');

             return;
        }


        $('.waiting-selection-ckpt').removeClass('hide-element');

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
                // show_error_has_hash(data.params.has_test);
                $('#exp_target').remove();
                $('#target_input').empty();
                if (data.params.targets.length > 1) {
                    let explain_select_target = add_select("exp_target", data.params.targets);
                    $('#target_input').append(explain_select_target);

                } else {
                    appConfig.exp_target = data.params.targets[0];
                    $('#target_input').append(data.params.targets[0]);

                }
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
                    $('#explain_params_div').addClass('hide-element');
                    $('#image_upload').removeClass('hide-element');
                    $('#feature-div').addClass('hide-element');
                    let result = 'data:image/' + data.params.extension + ';base64,' + data.params.image;
                    $('.inputDnD').css('background-image', 'url("' + result + '")');
                    appConfig.handle_key['extension'] = data.params.extension;
                    appConfig.handle_key['image'] = data.params.image;

                } else {
                    $('#explain_params_div').removeClass('hide-element');
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

    $('#explain').on('click', function () {
        let tp = $('#top_labels').val();
        let nf = $('#num_feat').val();
        if (tp.indexOf('e') > -1 || tp === '' || nf.indexOf('e') > -1 || nf === '') {
            $.notify('Explain params not valid', "error");
            return;
        }

        $('#explain_div_out').removeClass('hide-element');
        $('#explain_div_expl').removeClass('hide-element');
        $('.loader-pred').removeClass('hide-element');

        clear_graphs();

        if ($("#image_upload").hasClass("hide-element")) {

            let data_form = $("#explain_form").serializeArray();

            data_form.push({
                name: 'radiob',
                value: $('#table_checkpoints').DataTable().rows({selected: true}).data()[0][0]
            });
            data_form.push({name: 'model_name', value: $('#model_name').val()});
            if (!('exp_target' in data_form)) {
                data_form.push({name: 'exp_target', value: appConfig.exp_target});
            }
            $.ajax({
                url: "/explain",
                type: 'POST',
                dataType: 'json',
                data: data_form,
                success: function (data) {

                    if (data.hasOwnProperty('error')) {
                        alert(data.error);
                        $('#explain_div_out').addClass('hide-element');
                        $('#explain_div_expl').addClass('hide-element');
                        $('.loader-pred').addClass('hide-element');


                    } else {
                        $('.loader-pred').addClass('hide-element');
                        $('#prediction_probabilities').removeClass('hide-element');
                        $('#explain_graphs').removeClass('hide-element');
                        generate_explain_plots(data);
                    }


                },
                error: function (e) {
                    $.notify('Server error', "error");
                    $('#explain_div_out').addClass('hide-element');
                    $('#explain_div_expl').addClass('hide-element');
                    $('.loader-pred').addClass('hide-element');
                }
            });

        } else {
            var data_form = new FormData($("#explain_form")[0]);
            if ($('#inputFile').val() === '') {
                data_form.set('inputFile', dataURItoBlob('data:image/' + appConfig.handle_key.extension + ';base64,' + appConfig.handle_key.image))
            }
            data_form.append('radiob', $('#table_checkpoints').DataTable().rows({selected: true}).data()[0][0]);
            data_form.append('model_name', $('#model_name').val());
            if (!('exp_target' in data_form)) {
                data_form.append('exp_target', appConfig.exp_target);
            }
            var ajax = new XMLHttpRequest();
            ajax.open("POST", "/explain");
            ajax.send(data_form);
            ajax.addEventListener("load", completeHandler, false);
            ajax.addEventListener("error", errorHandler, false);
        }

    });
});

function generate_explain_plots(data) {
    var predict = data.predict_table;
    var graphics = data.graphs;

    if (data.type === 'regression') {
        create_bar(predict);
    } else {
        create_donut(predict);
    }

    for (var key in graphics) {
        create_graph(graphics[key]['labels'], graphics[key]['data'], key);
    }

}


function completeHandler(event) {
    $('.loader-pred').addClass('hide-element');
    $('#prediction_probabilities').removeClass('hide-element');
    $('#explain_graphs').removeClass('hide-element');


    let data = JSON.parse(event.target.responseText);
    if ('error' in data) {
        alert(data.error);
        $('#explain_div_out').addClass('hide-element');
        $('#explain_div_expl').addClass('hide-element');
    } else {
        $('#result_explain').removeClass('hide-element');
        create_donut(data.predict_table);

        let im2 = new Image();
        im2.src = 'data:image/jpg;base64,' + data.features;
        $("#explain_graphs").append(im2);
    }
}


function errorHandler(event) {
    alert('Error prediction');
    $("#predict_button").attr('disabled', false);
    $("#loading_predict").addClass('hidden');
}

function clear_graphs() {
    $('#probs').remove();
    let canvas = $("<canvas>")
        .attr("id", 'probs');
    $('#prediction_probabilities').append(canvas);

    $('canvas').children().remove();
    $('#explain_graphs').children().remove();
}