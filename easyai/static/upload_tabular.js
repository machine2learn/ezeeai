var id_file_uploading = '';
var ajax;

function _(el) {
    return $('#' + el);
}

$(document).ready(function () {
    $('#sb-datasets').addClass('active');
    $('#upload_tabular').addClass('active');
    $('#sidebar-data').addClass('show');
    $('.custom-file-input').on('change', function () {
        let fileName = $(this).val().split('\\').pop();
        if (fileName === "")
            fileName = 'Choose file';
        $(this).prev('.custom-file-label').addClass("selected").html(fileName);
        clear_upload_status();
    });


    $('#train_file:file').change(function (e) {
        if ($('#train_file').val() !== '')
            $('#upload_form_button').prop('disabled', false);
        else
            $('#upload_form_button').prop('disabled', true);
    });


});

function clear_upload_status() {
    _("progressBar_" + id_file_uploading).addClass('invisible');
    _("abort_" + id_file_uploading).addClass('invisible');
    $('.progress').addClass('invisible');
    _("status_" + id_file_uploading).text('');
    _("loaded_n_total_" + id_file_uploading).text('');
}

function uploadFile() {
    ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
        if (this.responseText.length === 0) {
            return;
        }
        var response = JSON.parse(this.responseText);
        if (this.readyState === 4 && response.status === 'error') {
            alert('Upload failed: ' + response.msg);
            clear_upload_status();
        } else if (this.readyState === 4 && response.status === 'ok') {
            $.notify("New dataset saved", "success");
            _("status_" + id_file_uploading).text('File upload completed');
            appConfig.handle_key.datasets.push(response.msg);
            appConfig.handle_key.data_types.push([response.msg, 'Tabular']);
            update_dataset_table();
            // let r_d = get_rows(appConfig.handle_key.data_types);
            // $('#table_datasets').DataTable().clear().rows.add(r_d).draw();

        }
    };
    ajax.upload.addEventListener("progress", progressHandler, false);
    ajax.addEventListener("load", completeHandler, false);
    ajax.addEventListener("error", errorHandler, false);
    ajax.addEventListener("abort", abortHandler, false);

    ajax.open("POST", "/upload_tabular");

    ajax.send(new FormData(_("upload_form")[0]));
    _("progressBar_" + id_file_uploading).removeClass('invisible');
    $('.progress').removeClass('invisible');
    _("abort_" + id_file_uploading).removeClass('invisible');

}

function progressHandler(event) {
    _("loaded_n_total_" + id_file_uploading).text("Uploaded " + event.loaded + " bytes of " + event.total);
    let percent = (event.loaded / event.total) * 100;
    percent = Math.round(percent);
    document.getElementById('progressBar_').style.width = percent.toString() + "%";
    _("status_" + id_file_uploading).text(percent + "% uploaded... please wait");
    if (percent === 100) {
        $('#train_file').prev('.custom-file-label').html('Choose file');
        $('#test_file').prev('.custom-file-label').html('Choose file');
        $('#train_file').val('');
        $('#test_file').val('');
        $('#upload_form_button').prop('disabled', true);
    }
}

function completeHandler(event) {
}

function errorHandler(event) {
    _("status_" + id_file_uploading).text("Upload Failed");
}

function abortHandler(event) {
    _("status_" + id_file_uploading).text("Upload Aborted");
    _("loaded_n_total_" + id_file_uploading).text("");
}


function update_dataset_table() {
    let r_d = get_rows(appConfig.handle_key.data_types);
    $('#table_datasets').DataTable().clear().rows.add(r_d).draw();
}