$(document).ready(function () {
    draw_models_select(appConfig.handle_key.models);


    $('#model_name').on('change', function () {
        enable_checkpoints();

        let model_name = $(this).val();
        $('#perf').text(appConfig.handle_key.models[model_name]['perf']);
        $('#loss').text(appConfig.handle_key.models[model_name]['loss']);

        $('.waiting-selection').addClass('hide-element');
        $('.loader').removeClass('hide-element');

        $.ajax({
            url: "/params_run",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({'model_name': $(this).val()}),
            success: function (data) {
                $('.loader').addClass('hide-element');
                $('.visualization').removeClass('hide-element');
                update_checkpoint_table(data.checkpoints, data.metric);
            }
        })
    });

});

function draw_models_select(models) {
    let label = $('<label></label>');
    label.addClass('control-label');
    label.html('<b> Model </b>');


    let select = $("<select></select>")
        .attr('id', 'model_name')
        .attr('name', 'model_name');
    select.addClass('form-control');

    let option_list = Object.keys(models).map((key) => $('<option>').val(key).text(key));
    option_list.unshift($('<option disabled selected value> Please select an option </option>'));
    select.append(option_list);

    $('#models-select-div').append(label)
        .append(select);

}

function enable_checkpoints() {
    $('#parameters_div').removeClass('disabled-custom');
    $('#checkpoints_div').removeClass('disabled-custom');
    $('.visualization').addClass('hide-element');

}