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
    selectList.addClass('form-control');
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
