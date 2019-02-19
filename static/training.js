var playing = false;

$(document).ready(function () {

    draw_models_select(appConfig.handle_key.models, appConfig.handle_key.datasets);

    if (appConfig.handle_key.running) {
        playing = true;
        toggle_play();
        enable_run();
        disable_run_config();
    }

    if (appConfig.handle_key.model_name !== ''){
        $('#model_name').val(appConfig.handle_key.model_name);
        enable_run();
    }


    $('#model_name').on('change', function () {
        enable_run();
    });

    setInterval(function () {
        if (playing) {
            $.ajax({
                url: "/refresh",
                type: 'GET',
                success: function (data) {
                    set_epochs(data.epochs);
                    if (playing !== data.running) {
                        playing = data.running;
                        toggle_play();
                        enable_run_config();

                    }


                    // if (data.data !== '')
                    //     $('#log').append(data.data).scrollTop($('#log')[0].scrollHeight);
                    // let $checkp_table = $('#checkp_table').DataTable();
                    // let row_selected = $checkp_table.rows({selected: true});
                    // let rows = get_rows(data.checkpoints);
                    // // $("#next_button").attr("disabled", rows.length < 1);
                    // $checkp_table
                    //     .clear().rows.add(rows).draw()
                    //     .row(row_selected).select();
                }
            })
        }
    }, 1000);


});

function draw_models_select(models, datasets) {
    let label = $('<label></label>');
    label.addClass('control-label');
    label.html('<b> Model </b>');

    $('#models-select-div').append(label);

    let select = $("<select></select>")
        .attr('id', 'model_name')
        .attr('name', 'model_name');
    select.addClass('form-control');

    let option_list = Object.keys(models).map((key) => $('<option>').val(key).text(key));
    option_list.unshift($('<option disabled selected value> Please select an option </option>'));
    select.append(option_list);
    $('#models-select-div').append(select);

}

function enable_run() {
    $('#run_div').removeClass('disabled-custom');

}

function enable_run_config() {
    $('#run_config_div').removeClass('disabled-custom');

}

function disable_run_config() {
    $('#run_config_div').addClass('disabled-custom');

}

function button_play() {

    playing = !playing;

    let formData = new FormData($('#parameters_form')[0]);
    let action = 'pause';
    if (playing)
        action = 'run';

    formData.append('action', action);
    formData.append('resume_from', '');
    playing = !playing;

    // form_data['resume_from'] = '';
    // if (document.getElementById("resume_training").checked === true)
    //     form_data['resume_from'] = get_checkpoint_selected();
    $.ajax({
        url: "/run",
        type: 'POST',
        processData: false,
        contentType: false,
        data: formData,
        success: function (data) {
            //TODO if error not playing = !playing
            playing = !playing;
            toggle_play();
            if (playing) {
                disable_run_config();
            } else {
                enable_run_config();
            }
        }
    });

}

function toggle_play() {
    let animation = playing ? 'stop' : 'play';
    $('#animate_to_' + animation).get(0).beginElement();
}

function set_epochs(val) {
    if (val !== null) {
        let str = val.toString().padStart(6, "0");
        let txt = str.slice(0, 3) + ',' + str.slice(3);
        $("#iter-number").text(txt);
    }
}

