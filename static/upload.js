var id_file_uploading;
var ajax;
var options = {
    'Classifier - Cluster': 'cluster',
    'Classifier - Decision Tree': 'decision_tree',
    'Regression': 'regression'
};

function _(el) {
    return $('#' + el);
}

$(document).ready(function () {
    $('#selector-selector').change(function () {
        $(".img-select").children("div").each(function () {
            let $this = _(this.id);
            if (!$this.hasClass("hidden")) {
                $this.addClass("hidden");
            }
            _(this.id + '-file').val('');
        });
        let num = this.selectedIndex + 1;
        _('option' + num).removeClass('hidden');
    });

    $("div.bhoechie-tab-menu>div.list-group>a").click(function (e) {
        e.preventDefault();
        $(this).siblings('a.active').removeClass("active");
        $(this).addClass("active");
        var index = $(this).index();
        $("div.bhoechie-tab>div.bhoechie-tab-content").removeClass("active")
            .eq(index).addClass("active");
        $('#selected').val(this.name);
    });
    $('#selected').val('tabular_data');
    $('#options-is_existing option[value="new_files"]').prop('selected', true);
    $('#data_graphs_button').prop('disabled', true);
    $('#upload_form_button').prop('disabled', true);
    $('#generate_dataset-script').text(appConfig.handle_key.examples[get_option_selected()]);

    $('#upload_form').submit(function () {
        return check_selected();
    });

    $('#confirm').on('click', function (e) {
        clear_tabular_form();
        clear_images_form();
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
        let text = appConfig.handle_key.examples[get_option_selected()];
        $('#generate_dataset-script').text(text);
        changes_generate_form();
    });
    $('#generate_dataset-script').bind('input', function () {
        changes_generate_form();
    });
    $('#generate_dataset-dataset_name').bind('input', function () {
        changes_generate_form();
    });


    $("#data_graphs_button").click(function (e) {
        clear_tabular_form();
        clear_images_form();
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
    $('#option1-file').change(function (e) {
        $('#upload_form_button').prop('disabled', false);
    });
    $('#option2-file').change(function (e) {
        $('#upload_form_button').prop('disabled', false);
    });
    $('#option3-file').change(function (e) {
        $('#upload_form_button').prop('disabled', false);
    });

});


function clear_tabular_form() {
    $('#new_tabular_files-train_file').val('');
    $('#new_tabular_files-test_file').val('');
}

function clear_images_form() {
    $(".img-select").children("div").each(function () {
        $('#' + this.id + '-file').val('');
        $('#' + this.id + '-test_file').val('');
        $('#progres_bar_' + this.id).val(0);
        $('#status_' + this.id).text('');
        $('#loaded_n_total_' + this.id).text('');
    });
}


function get_option_selected() {
    let option_selected = $('#generate_dataset-example_type').find(":selected").text();
    return options[option_selected];
}

function check_selected() {
    let dataset_name = $('#generate_dataset-dataset_name').val();
    if (dataset_name === "" || appConfig.handle_key.configs.indexOf(dataset_name) >= 0) {
        $('#error-confirm').text('Not valid dataset name');
        return false;
    }
    return true;
}

function changes_generate_form() {
    $("#confirm").removeClass('btn-success')
        .addClass('btn-primary');
    $('#upload_form_button').prop('disabled', true);
    $('#data_graphs_button').prop('disabled', true);
}

function uploud_id_file_uploading() {
    let selected = $('#selected').val();
    if (selected === 'images') {
        id_file_uploading = $('#selector-selector').val();
        clear_tabular_form()
    }
    else if (selected === 'tabular_data') {
        id_file_uploading = 'new_tabular_files';
    }
}

function freeze_view() {
    _('selector-selector').prop('disabled', true);
    _('upload_form_button').prop('disabled', true);
    $(".list-group a").addClass('not-active');
    $(".panel-body input").addClass('not-active');
}

function unfreeeze_view() {
    _('selector-selector').prop('disabled', false);
    $(".list-group a").removeClass('not-active');
    $(".panel-body input").removeClass('not-active');
}


function uploadFile() {
    uploud_id_file_uploading();
    ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
        if (this.readyState === 4 && this.responseText !== 'Ok') {
            alert('Upload failed: invalid data format');
            _("progressBar_" + id_file_uploading).val(0);
        } else if (this.readyState === 4 && this.responseText === 'Ok') {
            $.notify("New dataset saved", "info");
            _("status_" + id_file_uploading).text('File upload completed');
            unfreeeze_view()
        }
    };
    appConfig.handle_key.configs.push($('#generate_dataset-dataset_name').val());
    ajax.upload.addEventListener("progress", progressHandler, false);
    ajax.addEventListener("load", completeHandler, false);
    ajax.addEventListener("error", errorHandler, false);
    ajax.addEventListener("abort", abortHandler, false);

    ajax.open("POST", "/upload");

    ajax.send(new FormData(_("upload_form")[0]));
    freeze_view();
    _("progressBar_" + id_file_uploading).removeClass('hidden');
    _("abort_" + id_file_uploading).removeClass('hidden');

}

function progressHandler(event) {
    _("loaded_n_total_" + id_file_uploading).text("Uploaded " + event.loaded + " bytes of " + event.total);
    let percent = (event.loaded / event.total) * 100;
    percent = Math.round(percent);
    _("progressBar_" + id_file_uploading).val(percent);
    _("status_" + id_file_uploading).text(percent + "% uploaded... please wait");
    if (percent === 100) {
        clear_tabular_form();
        clear_images_form();
    }
}

function completeHandler(event) {
    unfreeeze_view()
}

function errorHandler(event) {
    _("status_" + id_file_uploading).text("Upload Failed");
    unfreeeze_view()
}

function abortHandler(event) {
    _("status_" + id_file_uploading).text("Upload Aborted");
    _("loaded_n_total_" + id_file_uploading).text("");
    unfreeeze_view()
}


