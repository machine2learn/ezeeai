var ajax;
var options = {
    'Classifier - Cluster': 'cluster',
    'Classifier - Decision Tree': 'decision_tree',
    'Regression': 'regression'
};

$(document).ready(function () {
    toogle_script(false);
    $('#generate_div input[id!="#script"], #generate_div select[id!="#script"]').on('input', function () {
        toogle_script(true);
        $('#script').text(appConfig.handle_key.examples[get_option_selected()]);
    });

    $('#dataset_name').on('input', function () {
        if ($(this).val() === '') {
            $('#generate_form_button').prop('disabled', true);
            toogle_script(false);
        } else {
            if (appConfig.handle_key.datasets.indexOf($('#dataset_name').val()) > 0) {
                $(this).addClass('text-error');
                $('#gen_error').html('Dataset name already exists.');
                $('#generate_form_button').prop('disabled', true);
            } else {
                $('#generate_form_button').prop('disabled', false);
                $('#gen_error').html('');
                $(this).removeClass('text-error');
            }

        }
    });


});

function generateFile() {
    $.ajax({
        url: "/generate",
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        accepts: {
            json: 'application/json',
        },
        data: JSON.stringify({
            'datasetname': $('#dataset_name').val(),
            'script': $('#script').val()
        }),
        success: function (data) {
            var valid_mess = data.valid;
            if (valid_mess === 'True') {
                $.notify("Generated dataset saved", "success");
                toogle_script(false);
                let $dataset = $('#dataset_name')
                appConfig.handle_key.datasets.push($dataset.val());
                appConfig.handle_key.data_types.push([$dataset.val(), 'Tabular']);
                update_dataset_table();

                $dataset.val('');
                $('#gen_error').html('');
            } else {
                $('#gen_error').html(valid_mess);
            }
        }
    });


}

function toogle_script(show) {
    if (show) {
        document.getElementById('script').style.display = "";
        document.getElementById('script').labels[0].style.display = "";
        document.getElementById('script_help').style.display = "";

    } else {
        document.getElementById('script').style.display = "none";
        document.getElementById('script').labels[0].style.display = "none";
        document.getElementById('script_help').style.display = "none";
    }
}


function get_option_selected() {
    let option_selected = $('#example_type').find(":selected").text();
    return options[option_selected];
}
