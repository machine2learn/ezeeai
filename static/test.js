$(document).ready(function () {
    draw_models_select(appConfig.handle_key.models);

    $('#model_name').on('change', function () {
        enable_checkpoints();
        $('.waiting-selection-ckpt').removeClass('hide-element');
        $('.waiting-selection').addClass('hide-element');
        $('.loader').removeClass('hide-element');

        $.ajax({
            url: "/params_predict",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({'model_name': $(this).val()}),
            success: function (data) {
                let test_params = data.params.test_files;
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

            }
        })
    });

    $("#image-upload").on('change', function(){
        uploadZipFile(this);
    });
     $("#tabular-upload").on('change', function(){
        uploadCSVFile(this);
    });

    $('#test').on('click', function () {
        let test_file = get_testfile_selected();
        let checkpoint = $('#table_checkpoints').DataTable().rows({selected: true}).data()[0][0];
        let model_name = $('#model_name').val();

        if (!test_file) {
            alert("Please select a file.")
        } else {
            $.ajax({
                url: "/test",
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                accepts: {
                    json: 'application/json',
                },
                data: JSON.stringify({
                    'filename': test_file,
                    'model': model_name,
                    'checkpoint': checkpoint
                }),
                success: function (data) {
                    // test_success('show_test', data);
                    // $loading.addClass('hidden');
                    // $("#test_button").attr('disabled', false);
                }
            })
        }

    });
});


function create_table_test_files(data) {

    let dataArr = data.map(function (d) {
        return [d];
    });

    if ($.fn.DataTable.isDataTable('#table_test_files')) {
        $('#table_test_files').DataTable().destroy();
        $('#table_test_files tbody').empty();
        $('#table_test_files thead').empty();
    }

    let table_test = $('#table_test_files').DataTable({
        data: dataArr,
        columns: [{title: 'Test file'}],
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
    })


}


function get_testfile_selected() {
    let file = $('#test_table').DataTable().rows({selected: true}).data()[0];
    if (file === undefined)
        return false;
    if (file[0].indexOf('TEST FROM SPLIT') > 0)
        return 'TEST FROM SPLIT';
    return file[0];
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
                else
                    upload_test_table(filename);
            }
        })
    }
}


function upload_test_table(filename) {
   console.log(filename)

}





