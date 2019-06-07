$(document).ready(function () {
    $('#username').prop('disabled', true);
    var dataset_rows = get_rows(appConfig.handle_key.datasets);
    var table_datasets = $('#table_datasets').DataTable({
        data: dataset_rows,
        columns: [{title: 'Dataset'}, {title: 'Type'}, {title: '', width: "3%", 'sClass': 'trash-icon'}],
        searching: true,
        'select': false,
        "lengthChange": false,
        "drawCallback": function () {
            if ($(this).DataTable().rows()[0].length <= 10) {
                let id = '#' + $(this).attr('id');
                $(id + '_paginate').remove();
                $(id + '_info').remove();
            }

        }

    });
    var models_rows = get_rows_model(appConfig.handle_key.parameters);
    var models_table = $('#table_models').DataTable({
        data: models_rows,
        columns: [{title: 'Model name'}, {title: 'Dataset'}, {title: 'Performance'}, {title: 'Loss'}, {
            title: '',
            width: "5%",
            'sClass': 'trash-icon'
        }],
        'select': false,
        fixedHeader: false,
        searching: true,
        "lengthChange": false,
        "drawCallback": function () {
            if ($(this).DataTable().rows()[0].length <= 10) {
                let id = '#' + $(this).attr('id');
                $(id + '_paginate').remove();
                $(id + '_info').remove();
            }

        }
    });
    $('#data_search').keyup(function () {
        table_datasets.search($(this).val()).draw();

    });
    $('#model_search').keyup(function () {
        models_table.search($(this).val()).draw();

    });


});

function get_rows(datasets) {
    let dataset_rows = [];
    datasets.forEach(function (d) {
        let conf_row = [d[0], d[1], '<a data-id=' + d[0] + ' onclick="ConfirmDelete(this, false)" ><i class="fi flaticon-trash"></i></a>'];
        dataset_rows.push(conf_row)
    });
    return dataset_rows;
}

function get_rows_model(models) {
    let models_rows = [];
    Object.keys(models).forEach(function (key) {
        let prf = 'Not evaluated yet';
        let loss = 'Not evaluated yet';
        let dataset = 'Not assigned yet';
        if (models[key].hasOwnProperty("perf")) {
            prf = models[key]["perf"];
            loss = models[key]["loss"];
        }
        if (models[key].hasOwnProperty("dataset")) {
            dataset = models[key]["dataset"];
        }
        let row = [key, dataset, prf, loss,
            '<a data-id=' + key + ' onclick="ConfirmModelDelete(this, false)" ><i class="fi flaticon-trash"></i></i></a>'];
        models_rows.push(row);
    });
    return models_rows;
}


function ConfirmDelete(elem, all) {
    let dataset = $(elem).attr('data-id');
    let models_dataset = [];

    let message = "Are you sure you want to delete the selected dataset? (All models related will be delete)";
    if (all) {
        message = "Are you sure you want to delete all saved datasets?  (All models related will be delete)";
    } else {
        Object.keys(appConfig.handle_key.parameters).forEach(function (key) {
            if (appConfig.handle_key.parameters[key]['dataset'] === dataset)
                models_dataset.push(key);
        });
    }
    if (confirm(message)) {
        $.ajax({
            url: "/delete_dataset",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            accepts: {
                json: 'application/json',
            },
            data: JSON.stringify({
                'dataset': dataset,
                'models': models_dataset,
                'all': all
            }),
            success: function (data) {
                upload_tables(data);
            }
        })
    }
}

function ConfirmModelDelete(elem, all) {
    let message = "Are you sure you want to delete the selected model?";
    if (all === true) {
        message = "Are you sure you want to delete all saved configurations?";
    }
    if (confirm(message)) {
        $.ajax({
            url: "/delete_model",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            accepts: {
                json: 'application/json',
            },
            data: JSON.stringify({
                'model': $(elem).attr('data-id'),
                'all': all
            }),
            success: function (data) {
                upload_tables(data);
            }
        })
    }
}

function upload_tables(data) {
    appConfig.handle_key.datasets = data.data_types;
    appConfig.handle_key.parameters = data.models;
    let r_d = get_rows(data.data_types);
    let r_m = get_rows_model(data.models);
    $('#table_datasets').DataTable().clear().rows.add(r_d).draw();
    $('#table_models').DataTable().clear().rows.add(r_m).draw();
}
