$(document).ready(function () {
    var playing = false;
    let running = appConfig.running;
    if (running === 'running')
        toggle_play(true);

    $('svg').click(function () {
        playing = !playing;
        let form_data = {'action': 'pause'};
        if (playing)
            form_data['action'] = 'run';
        form_data['resume_from'] = '';
        if (document.getElementById("resume_training").checked === true)
            form_data['resume_from'] = get_checkpoint_selected();
        playing = !playing;
        $.ajax({
            url: "/run",
            type: 'POST',
            data: form_data,
            success: function () {
                playing = !playing;
                var animation = playing ? 'stop' : 'play';
                $('#animate_to_' + animation).get(0).beginElement();
                $('#resume_training').prop('checked', false);
            }
        })

    });

    function toggle_play(val) {
        playing = val;
        let animation = playing ? 'stop' : 'play';
        $('#animate_to_' + animation).get(0).beginElement();
    }

    $("#predict_button").click(function (e) {
        let $loading = $('#loading_predict');
        $("#predict_button").attr('disabled', true);
        $loading.removeClass('hidden');
        if ($("#image_upload").hasClass("hidden")) {
            $.ajax({
                url: "/predict",
                type: 'POST',
                dataType: 'json',
                data: serialize_form(),
                success: function (data) {
                    $("#predict_button").attr('disabled', false);
                    $loading.addClass('hidden');

                    if ('error' in data) {
                        alert('Model\'s structure does not match the new parameter configuration');
                    } else {
                        $('#predict_val').empty();

                        $.each(data, function (key, val) {
                            $('#predict_val')
                                .append(key)
                                .append(' : ')
                                .append(val)
                                .append('<br>');
                        });
                    }
                }
            })
        } else {

            var data_form = new FormData($("#predict_form")[0]);
            if ($('#inputFile').val() === '') {
                data_form.set('inputFile', dataURItoBlob('data:image/' + appConfig.handle_key.extension + ';base64,' + appConfig.handle_key.image))
            }
            data_form.append('radiob', get_checkpoint_selected());
            var ajax = new XMLHttpRequest();
            ajax.open("POST", "/predict");
            ajax.send(data_form);
            ajax.addEventListener("load", completeHandler, false);
            ajax.addEventListener("error", errorHandler, false);
        }

    });

    function test_success(href, result) {
        if (result !== 'ok')
            alert(result);
        else
            $("<a>").attr({"href": href, "target": '_blank'})[0].click();
    }

    $("#explain_button").click(function (e) {
        $('#loading_explain').removeClass('hidden');
        $('#explain_button').prop('disabled', true);

        if ($("#image_upload").hasClass("hidden")) {
            $.ajax({
                url: "/explain",
                type: 'POST',
                data: serialize_form(),
                success: function (data) {
                    $('#loading_explain').addClass('hidden');
                    $('#explain_button').prop('disabled', false);
                    test_success('explain', data.explanation);
                }
            })
        } else {
            let data_form = new FormData($("#predict_form")[0]);
            if ($('#inputFile').val() === '') {
                data_form.set('inputFile', dataURItoBlob('data:image/' + appConfig.handle_key.extension + ';base64,' + appConfig.handle_key.image))
            }
            data_form.append('radiob', get_checkpoint_selected());
            let ajax = new XMLHttpRequest();
            ajax.open("POST", "/explain");
            ajax.send(data_form);
            ajax.addEventListener("load", completeHandlerExplain, false);
        }
    });


    function completeHandlerExplain(event) {
        let data = JSON.parse(event.target.responseText);
        explain_success(data);
    }

    function explain_success(data) {
        $('#loading_explain').addClass('hidden');
        $('#explain_button').prop('disabled', false);
        test_success('explain', data['explanation']);
    }

    $("#test_button").click(function (e) {
        let input = get_testfile_selected();
        let $loading = $('#loading_test');
        $("#test_button").attr('disabled', true);
        if (!input) {
            alert("Please select a file.")
        } else {
            $loading.removeClass('hidden');
            $.ajax({
                url: "/test",
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                accepts: {
                    json: 'application/json',
                },
                data: JSON.stringify({
                    'filename': input,
                    'model': get_checkpoint_selected()
                }),
                success: function (data) {
                    test_success('show_test', data.result);
                    $loading.addClass('hidden');
                    $("#test_button").attr('disabled', false);
                }
            })
        }

    });

    let inputs = document.querySelectorAll('.inputfile');
    Array.prototype.forEach.call(inputs, function (input) {
        let label = input.nextElementSibling,
            labelVal = label.innerHTML;

        input.addEventListener('change', function (e) {
            let fileName = '';
            if (this.files && this.files.length > 1)
                fileName = (this.getAttribute('data-multiple-caption') || '').replace('{count}', this.files.length);
            else
                fileName = e.target.value.split('\\').pop();

            if (fileName)
                label.querySelector('span').innerHTML = fileName;
            else
                label.innerHTML = labelVal;
        });
    });

    function set_epochs(val) {
        if (val !== null) {
            let str = val.toString().padStart(6, "0");
            let txt = str.slice(0, 3) + ',' + str.slice(3);
            $("#iter-number").text(txt);
        }
    }

    setInterval(function () {
        if (playing) {
            $.ajax({
                url: "/refresh",
                type: 'GET',
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                accepts: {
                    json: 'application/json',
                },
                data: JSON.stringify("checkpoints"),
                success: function (data) {
                    set_epochs(data.epochs);
                    if (playing !== data.running)
                        toggle_play(data.running);

                    if (data.data !== '')
                        $('#log').append(data.data).scrollTop($('#log')[0].scrollHeight);
                    let $checkp_table = $('#checkp_table').DataTable();
                    let row_selected = $checkp_table.rows({selected: true});
                    let rows = get_rows(data.checkpoints);
                    // $("#next_button").attr("disabled", rows.length < 1);
                    $checkp_table
                        .clear().rows.add(rows).draw()
                        .row(row_selected).select();
                }
            })
        }
    }, 1000);
})
;

function ConfirmDelete(elem, all) {
    let message = "Are you sure you want to delete the selected model?";
    if (all === true) {
        message = "Are you sure you want to delete all saved models?";
    }
    if (confirm(message)) {
        $.ajax({
            url: "/delete",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            accepts: {
                json: 'application/json',
            },
            data: JSON.stringify({'deleteID': $(elem).attr('data-id')}),
            success: function (data) {
                en_disable_objs(true);
                data = get_rows(data.checkpoints);
                $('#checkp_table').DataTable().clear().rows.add(data).draw();
            }
        })
    }
}

function serialize_form() {
    let data_form = $("#predict_form").serializeArray();
    data_form.push({name: 'radiob', value: get_checkpoint_selected()});
    return data_form;
}

function get_checkpoint_selected() {
    let model = $('#checkp_table').DataTable().rows({selected: true}).data();
    return model[0][0];
}

function get_testfile_selected() {
    let file = $('#test_table').DataTable().rows({selected: true}).data()[0];
    if (file === undefined)
        return false;
    if (file[0].indexOf('TEST FROM SPLIT') > 0)
        return 'TEST FROM SPLIT';
    return file[0];
}


function dataURItoBlob(dataURI) {
    // convert base64/URLEncoded data component to raw binary data held in a string
    let byteString;
    if (dataURI.split(',')[0].indexOf('base64') >= 0)
        byteString = atob(dataURI.split(',')[1]);
    else
        byteString = unescape(dataURI.split(',')[1]);

    // separate out the mime component
    let mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

    // write the bytes of the string to a typed array
    let ia = new Uint8Array(byteString.length);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }

    return new Blob([ia], {type: mimeString});
}

function completeHandler(event) {
    $("#predict_button").attr('disabled', false);
    $("#loading_predict").addClass('hidden');

    let data = JSON.parse(event.target.responseText);
    if ('error' in data) {
        alert('Model\'s structure does not match the new parameter configuration');
    } else {
        $('#predict_val').empty();

        $.each(data, function (key, val) {
            $('#predict_val')
                .append(key)
                .append(' : ')
                .append(val)
                .append('<br>');
        });
    }
}

function errorHandler(event) {
    alert('Error prediction');
    $("#predict_button").attr('disabled', false);
    $("#loading_predict").addClass('hidden');
}

function upload_test_file(e) {
    let $input = $('#upload-file');
    if ($input[0].files.length === 0) {
        alert("Please select a file.")
    } else {
        let $input = $('#upload-file');
        if (handle_key.hasOwnProperty('image'))
            uploadZipFile($input); //zip images
        else
            uploadCSVFile($input); //tabular data
    }
}


function uploadZipFile($input) {
    let filename = document.getElementById('upload-file').files[0].name.split('.')[0];
    let f = new FormData();
    f.append('input_file', $input[0].files[0], $input[0].files[0].name);
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
    let filename = document.getElementById('upload-file').files[0].name;
    let fReader = new FileReader();
    fReader.readAsBinaryString($input[0].files[0]);
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
    let test_files = appConfig.handle_key.test_files.map((val) => [val]);
    if (appConfig.handle_key.has_test)
        test_files.push([' <span class="glyphicon glyphicon-tasks"></span> TEST FROM SPLIT']);
    test_files.push([filename]);
    appConfig.handle_key.test_files.push(filename);
    $('#test_table').DataTable().clear().rows.add(test_files).draw()

}