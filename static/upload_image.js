var format1 = 'my-images/              my-images/\n' +
    '├── cat/                ├── train/\n' +
    '│   ├── 1.jpg           │   ├── cat/\n' +
    '│   └── 2.jpg           │   │   └── *.jpg\n' +
    '└── dog/                │   └── dog/\n' +
    '    ├── 1.jpg           │       └── *.jpg\n' +
    '    └── 2.jpg           └── test/\n' +
    '                            ├── cat/\n' +
    '                            │   └── *.jpg\n' +
    '                            └── dog/\n' +
    '                                └── *.jpg';

var format2 = 'my-images/               my-images/             my-images/\n' +
    '├── 1.jpg                ├── images/             ├── 1.jpg\n' +
    '├── 2.jpg                │   ├── 1.jpg           ├── 2.jpg\n' +
    '├── 3.jpg                │   └── 2.jpg           ├── 3.jpg\n' +
    '└── labels.txt           └── labels.txt          ├── train.txt\n' +
    '                                                 └── test.txt';


var format3 = 'Save your data with:\n\n' +
    'np.savez(filename, x=images, y=labels)\n\n' +
    'or\n\n' +
    'np.savez(filename, x_train=images_train, y_train=labels_train, x_test=images_test,   y_test=labels_test)';

var formats = {
    'option1': format1,
    'option2': format2,
    'option3': format3
};

var id_file_uploading = '';
var ajax;

function _(el) {
    return $('#' + el);
}

function clearFileInput(id) {
    var oldInput = document.getElementById(id);

    var newInput = document.createElement("input");

    newInput.type = "file";
    newInput.id = oldInput.id;
    newInput.name = oldInput.name;
    newInput.className = oldInput.className;
    newInput.style.cssText = oldInput.style.cssText;
    // TODO: copy any other relevant attributes

    oldInput.parentNode.replaceChild(newInput, oldInput);
}


$(document).ready(function () {

    $('#format-content').html(formats[$('#selector-selector').val()]);
    id_file_uploading = $('#selector-selector').val();

    $('#selector-selector').on('change', function () {
        //Clear last input
        _(id_file_uploading + '-file').val('');
        _(id_file_uploading + '-file').prev('.custom-file-label').addClass('selected').html('Choose file');
        $('#upload_form_button').prop('disabled', true);


        clear_upload_status();
        $('#format-content').html(formats[$(this).val()]);
        $('.img-select').addClass('hide-element');
        $('#' + $(this).val()).removeClass('hide-element');
        id_file_uploading = $(this).val();

        $('.custom-file-input').val('');

    });
    $('.custom-file-input').on('change', function () {
        let fileName = $(this).val().split('\\').pop();
        if (fileName === "")
            fileName = 'Choose file';
        $(this).prev('.custom-file-label').addClass("selected").html(fileName);
        clear_upload_status();
    });

    $('input:file').change(function (e) {
        if ($(this).val() !== '')
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
            if (response.msg === '')
                response.msg = 'Dataset format is not correct';

            $.notify("Upload error: " + response.msg, "error");
            clear_upload_status();
        } else if (this.readyState === 4 && response.status === 'ok') {
            $.notify("New dataset saved", "success");
            _("status_" + id_file_uploading).text('File upload completed');
            appConfig.handle_key.datasets.push([response.msg, 'Image']);
            let r_d = get_rows(appConfig.handle_key.datasets);
            $('#table_datasets').DataTable().clear().rows.add(r_d).draw();

        }
    };
    ajax.upload.addEventListener("progress", progressHandler, false);
    ajax.addEventListener("load", completeHandler, false);
    ajax.addEventListener("error", errorHandler, false);
    ajax.addEventListener("abort", abortHandler, false);

    ajax.open("POST", "/upload_image");
    ajax.send(new FormData(_("upload_form")[0]));
    _("progressBar_" + id_file_uploading).removeClass('invisible');
    $('.progress').removeClass('invisible');
    _("abort_" + id_file_uploading).removeClass('invisible');

}

function progressHandler(event) {
    _("loaded_n_total_" + id_file_uploading).text("Uploaded " + event.loaded + " bytes of " + event.total);
    let percent = (event.loaded / event.total) * 100;
    percent = Math.round(percent);
    document.getElementById('progressBar_' + id_file_uploading).style.width = percent.toString() + "%";
    _("status_" + id_file_uploading).text(percent + "% uploaded... please wait");
    if (percent === 100) {
        $('.custom-file-label').html('Choose file');
        $('.custom-file-input').val('');
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
