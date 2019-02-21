$(document).ready(function () {
    draw_models_select(appConfig.handle_key.models);


    $('#model_name').on('change', function () {
        enable_checkpoints();
        $('.waiting-selection-ckpt').removeClass('hide-element');
        $('#feature-div').addClass('hide-element');
        // $('#prediction_div').addClass('disabled-custom');


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
                    $('#image_upload').removeClass('hide-element');
                    $('#feature-div').addClass('hide-element');
                    let result = 'data:image/' + data.params.extension + ';base64,' + data.params.image;
                    $('.inputDnD').css('background-image', 'url("' + result + '")');
                    appConfig.handle_key['extension'] = data.params.extension;
                    appConfig.handle_key['image'] = data.params.image;

                } else {
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

    $('#predict').on('click', function () {

        if ($("#image_upload").hasClass("hide-element")) {
            let data_form = $("#predict_form").serializeArray();
            data_form.push({
                name: 'radiob',
                value: $('#table_checkpoints').DataTable().rows({selected: true}).data()[0][0]
            });
            data_form.push({name: 'model_name', value: $('#model_name').val()});
            $.ajax({
                url: "/predict",
                type: 'POST',
                dataType: 'json',
                data: data_form,
                success: function (data) {
                    console.log('hi');
                    $('#prediction_div').removeClass('hide-element');
                }
            });

        } else {
            var data_form = new FormData($("#predict_form")[0]);
            if ($('#inputFile').val() === '') {
                data_form.set('inputFile', dataURItoBlob('data:image/' + appConfig.handle_key.extension + ';base64,' + appConfig.handle_key.image))
            }
            data_form.append('radiob', $('#table_checkpoints').DataTable().rows({selected: true}).data()[0][0]);
            data_form.append('model_name', $('#model_name').val());
            var ajax = new XMLHttpRequest();
            ajax.open("POST", "/predict");
            ajax.send(data_form);
            ajax.addEventListener("load", completeHandler, false);
            ajax.addEventListener("error", errorHandler, false);
        }

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
    $('#checkpoints_div').removeClass('disabled-custom');
    $('.visualization').addClass('hide-element');
}


function add_input_number(type, label_name, value, input_step) {
    if (type === "number") {
        let x = $("<input>")
            .attr("type", type)
            .attr("id", label_name)
            .attr("name", label_name)
            .attr("value", value)
            .attr("step", input_step);
        let th = $('<th></th>')
            .append(x);
        let th2 = $('<th></th>')
            .text(label_name);
        let tr = $('<tr></tr>')
            .append(th2)
            .append(th);
        $("#table_features")
            .append(tr);
    }
}

function add_select(label_name, options) {
    let selectList = $("<select>")
        .attr('id', label_name)
        .attr('name', label_name);
    let option_list = options.map((key) => $('<option>').val(key).text(key));
    selectList.append(option_list);
    return selectList
}

function add_input_select(label_name, options, value_default) {
    let selectList = add_select(label_name, options);
    let th = $('<th></th>')
        .append(selectList);
    let th2 = $('<th></th>')
        .text(label_name);
    let tr = $('<tr></tr>')
        .append(th2)
        .append(th);
    $("#table_features")
        .append(tr);
}


function readUrl(input) {
    if (input.files && input.files[0]) {
        let reader = new FileReader();
        reader.onload = (e) => {
            let imgData = e.target.result;
            let imgName = input.files[0].name;
            input.setAttribute("data-title", imgName);
        };
        reader.readAsDataURL(input.files[0]);
    }
    var file = document.querySelector('input[type=file]').files[0];
    var reader = new FileReader();
    reader.onloadend = function () {
        $('.inputDnD').css('background-image', 'url("' + reader.result + '")');
    };

    reader.readAsDataURL(input.files[0]);
}

function create_checkpoint_table(checkpoints, metric) {
    let table_checkpoints = $('#table_checkpoints').DataTable({
        data: get_rows(checkpoints),
        columns: [{title: 'Checkpoint'}, {title: metric}, {title: 'Loss'}],
        searching: true,
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
        .on('select', function () {
            $('.waiting-selection-ckpt').addClass('hide-element');
            $('#feature-div').removeClass('hide-element');
            $('#features_div').removeClass('disabled-custom');
        })
        .on('deselect', function () {
            $('.waiting-selection-ckpt').removeClass('hide-element');
            $('#feature-div').addClass('hide-element');
            $('#features_div').addClass('disabled-custom');
        });

    $('#checkpoint_search').keyup(function () {
        table_checkpoints.search($(this).val()).draw();
    });
}

function get_rows(checkpoints) {
    let rows = [];
    $.each(checkpoints, function (key, value) {
        let val = 0;
        if ('accuracy' in value)
            val = value['accuracy'];
        else if ('r_squared' in value)
            val = value['r_squared'];
        rows.push([key, val, value['loss']]);
    });
    return rows;
}


function serialize_form() {
    let data_form = $("#predict_form").serializeArray();
    data_form.push({name: 'radiob', value: get_checkpoint_selected()});
    return data_form;
}


function completeHandler(event) {
    $("#predict_button").attr('disabled', false);
    $("#loading_predict").addClass('hidden');

    let data = JSON.parse(event.target.responseText);
    if ('error' in data) {
        alert(data.error);
    } else {
        console.log('ok')
        $('#prediction_div').removeClass('hide-element');
        // $('#predict_val').empty();
        //
        // $.each(data, function (key, val) {
        //     $('#predict_val')
        //         .append(key)
        //         .append(' : ')
        //         .append(val)
        //         .append('<br>');
        // });
    }
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


function errorHandler(event) {
    alert('Error prediction');
    $("#predict_button").attr('disabled', false);
    $("#loading_predict").addClass('hidden');
}
