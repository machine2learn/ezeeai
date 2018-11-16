$(document).ready(function () {
    $('#username').prop('disabled', true);
    var dataset_rows = get_rows(appConfig.handle_key.datasets);
    var table_datasets = $('#table_datasets').DataTable({
        data: dataset_rows,
        columns: [{title: 'Dataset'}, {title: '', width: "3%"}],
        'select': 'single'
    });
    var models_rows = get_rows_model(appConfig.handle_key.parameters);
    var models_table = $('#table_models').DataTable({
        data: models_rows,
        columns: [{title: 'Model name'}, {title: 'Dataset'}, {title: 'Performance'}, {title: 'Loss'}, {
            title: '',
            width: "5%"
        }],
        'select': 'single',
        fixedHeader: false
    });
});

function get_rows(datasets) {
    let dataset_rows = [];
    datasets.forEach(function (d) {
        let conf_row = [d, '<a data-id=' + d + ' onclick="ConfirmDelete(this, false)" ><i class="fas fa-times"></i></a>'];
        dataset_rows.push(conf_row)
    });
    return dataset_rows;
}

function get_rows_model(models) {
    let models_rows = [];
    Object.keys(models).forEach(function (key) {
        let prf = 'No evaluated yet';
        let loss = 'No evaluated yet';
        if (models[key].hasOwnProperty("perf")) {
            prf = models[key]["perf"];
            loss = models[key]["loss"];
        }
        let row = [key, models[key]["dataset"], prf, loss,
            '<a data-id=' + key + ' onclick="ConfirmModelDelete(this, false)" ><i class="fas fa-times"></i></i></a>'];
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
    appConfig.handle_key.datasets = data.datasets;
    appConfig.handle_key.parameters = data.models;
    let r_d = get_rows(data.datasets);
    let r_m = get_rows_model(data.models);
    $('#table_datasets').DataTable().clear().rows.add(r_d).draw();
    $('#table_models').DataTable().clear().rows.add(r_m).draw();
}
