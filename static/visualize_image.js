$(document).ready(function () {
    $('.widget').widgster();
    $('.visualization').addClass('hide-element');


    var dataset_rows = get_rows(appConfig.handle_key.datasets);
    var table_datasets = $('#table_datasets').DataTable({
        data: dataset_rows,
        columns: [{title: 'Dataset'}, {title: '', width: "1%", "sClass": "trash-icon"}],
        searching: true,
        'select': 'single',
        "lengthChange": false,
        "drawCallback": function () {
            $("#table_datasets thead").remove();
            if ($(this).DataTable().rows()[0].length <= 10) {
                $("#table_datasets_paginate").remove();
                $("#table_datasets_info").remove();
            }

        },

    });
    $('#dataset_search').keyup(function () {
        table_datasets.search($(this).val()).draw();
    });

    $('#table_datasets tbody').on('click', 'td', function (e) {
        if (table_datasets.row(this, {selected: true}).any()) {
            $('.visualization').addClass('hide-element');
            $('.waiting-selection').removeClass('hide-element');
        } else if (table_datasets.page.info().recordsDisplay === 0) {
            $('.visualization').addClass('hide-element');
            $('.waiting-selection').removeClass('hide-element');
        } else {
            if ($(this).hasClass('trash-icon')) {
                return;
            }


        }


    });


});

function get_rows(datasets) {
    let dataset_rows = [];
    datasets.forEach(function (d) {
        if (d[1] === 'Image') {
            let conf_row = [d[0], '<a data-id=' + d[0] + ' onclick="ConfirmDelete(this, false)" ><i class="fi flaticon-trash"></i></a>'];
            dataset_rows.push(conf_row)
        }
    });
    return dataset_rows;
}

function upload_table(data) {
    appConfig.handle_key.datasets = data.data_types;
    let r_d = get_rows(data.data_types);
    $('#table_datasets').DataTable().clear().rows.add(r_d).draw();
}


function ConfirmDelete(elem, all) {
    let dataset = $(elem).attr('data-id');

    let message = "Are you sure you want to delete the selected dataset? (All models related will be delete)";

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
                'models': [],
                'all': all
            }),
            success: function (data) {
                upload_table(data);
                //TODO clear visualizations if deleted is selected one
            }
        })
    }
}


