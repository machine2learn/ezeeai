$(document).ready(function () {
    $("div.bhoechie-tab-menu>div.list-group>a").click(function (e) {
        e.preventDefault();
        $(this).siblings('a.active').removeClass("active");
        $(this).addClass("active");
        var index = $(this).index();
        $("div.bhoechie-tab>div.bhoechie-tab-content").removeClass("active");
        $("div.bhoechie-tab>div.bhoechie-tab-content").eq(index).addClass("active");
        $('#selected').val(this.name);
    });
$('#selected').val('tabular_data');

    $('#options-is_existing option[value="new_files"]').prop('selected', true);

    if (appConfig.handle_key.mess !== false)
        $.notify("New dataset :  " + appConfig.handle_key.mess + " saved", "info");


    $('#data_graphs_button').prop('disabled', true);
    $('#upload_form_button').prop('disabled', true);
    $('#generate_dataset-script').text(appConfig.handle_key.examples[get_option_selected()]);

    $('#upload_form').submit(function () {
        return check_selected();
    });

    $('#confirm').on('click', function (e) {
        if (!check_selected()) {
            return false;
        }
        $('#error-confirm').text('');
        e.preventDefault();
        $.ajax({
            url: "/confirm",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            accepts: {
                json: 'application/json',
            },
            data: JSON.stringify({
                'datasetname': $('#generate_dataset-dataset_name').val(),
                'script': $('#generate_dataset-script').val()
            }),
            success: function (data) {
                var valid_mess = data.valid;
                console.log(valid_mess);
                if (valid_mess === 'True') {
                    $('#upload_form_button').prop('disabled', false);
                    $('#data_graphs_button').prop('disabled', false);
                    document.getElementById("confirm").classList.remove('btn-primary');
                    document.getElementById("confirm").classList.add('btn-success');
                } else {
                    $('#error-confirm').text(valid_mess);
                }
            }
        });
    });


    $('#generate_dataset-example_type').change(function () {
        var text = appConfig.handle_key.examples[get_option_selected()];
        $('#generate_dataset-script').text();
        changes_generate_form();
    });
    $('#generate_dataset-script').bind('input', function () {
        changes_generate_form();
    });
    $('#generate_dataset-dataset_name').bind('input', function () {
        changes_generate_form();
    });


    $("#data_graphs_button").click(function (e) {
        $.ajax({
            url: "/data_graphs",
            type: 'POST',
            data: $("#upload_form").serialize(),
            success: function (response) {
                $("<a>").attr({"href": 'data_graphs', "target": '_blank'})[0].click();
            }
        })
    });

    $('#new_tabular_files-train_file:file').change(function (e) {
        $('#upload_form_button').prop('disabled', false);
    });

    $('#tabular_data').click(function (e) {
        if ($('#new_tabular_files-train_file').val() !== '')
            $('#upload_form_button').prop('disabled', false);
        $('#tabular_data_div').removeClass('hidden');
        $('#image_data_div').addClass('hidden');
        $('#generate_data_div').addClass('hidden');
        $('#selected').val('tabular_data');
        e.preventDefault();
    });
    $('#image_data').click(function (e) {
        $('#image_data_div').removeClass('hidden');
        $('#tabular_data_div').addClass('hidden');
        $('#generate_data_div').addClass('hidden');
        $('#selected').val('image_data');
        e.preventDefault();
    });
    $('#generate_data').click(function (e) {
        $('#generate_data_div').removeClass('hidden');
        $('#tabular_data_div').addClass('hidden');
        $('#image_data_div').addClass('hidden');
        $('#selected').val('generate_data');
        $('#upload_form_button').prop('disabled', true);
        e.preventDefault();
    });
});


function get_option_selected() {
    var option_selected = $('#generate_dataset-example_type').find(":selected").text();
    if (option_selected === 'Classifier - Cluster') {
        option_selected = 'cluster';
    }
    if (option_selected === 'Classifier - Decision Tree') {
        option_selected = 'decision_tree';
    }
    if (option_selected === 'Regression') {
        option_selected = 'regression';
    }
    return option_selected;
}

function check_selected() {
    var option_selected = $('#options-is_existing').find(":selected").text();
    if (option_selected === "Generate data") {
        var dataset_name = $('#generate_dataset-dataset_name').val();
        if (dataset_name === "" || appConfig.handle_key.configs.indexOf(dataset_name) >= 0) {
            $('#error-confirm').text('Not valid dataset name');
            return false;
        }
    }
    return true;
}

function changes_generate_form() {
    document.getElementById("confirm").classList.add('btn-primary');
    document.getElementById("confirm").classList.remove('btn-success');
    $('#upload_form_button').prop('disabled', true);
    $('#data_graphs_button').prop('disabled', true);
}