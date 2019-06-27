$(document).ready(function () {
    $('.widget').widgster();
    $('.visualization').addClass('hide-element');

    var dataset_rows = get_rows(appConfig.handle_key.data_types);
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
        $('#get_profile').addClass('disabled-custom');

        if (table_datasets.row(this, {selected: true}).any()) {
            $('.visualization').addClass('hide-element');
            $('.waiting-selection').removeClass('hide-element');
            $('#table_datasets').removeClass('no-clickable');

        } else if (table_datasets.page.info().recordsDisplay === 0) {
            $('.visualization').addClass('hide-element');
            $('.waiting-selection').removeClass('hide-element');
            $('#table_datasets').removeClass('no-clickable');

        } else {
            if ($(this).hasClass('trash-icon')) {
                return;
            }
            if (typeof $.fn.DataTable === 'undefined') {
                $.noConflict();
            }
            if ($.fn.DataTable.isDataTable('#table_raw_data')) {
                $('#table_raw_data').DataTable().destroy();

                $('#table_raw_data tbody').empty();
                $('#table_raw_data thead').empty();

            }
            $('.waiting-selection').addClass('hide-element');
            $('.loader').removeClass('hide-element');
            $('.visualization').addClass('hide-element');
            $('#table_datasets').addClass('no-clickable');

            if ($('#scatter').length > 0) {
                $('#scatter-select-div1').children().remove();
                $('#scatter-select-div2').children().remove();
            }
            if ($('#hist-select').length > 0) {
                $('#hist-select').children().remove();
            }
            $('#table_datasets').addClass('diabled-custom');

            $.ajax({
                url: "/data_graphs",
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                accepts: {
                    json: 'application/json',
                },
                timeout: 120000,
                data: JSON.stringify({
                    'datasetname': table_datasets.row(this).data()[0]
                }),
                success: function (data) {
                    $('#table_datasets').removeClass('no-clickable');
                    var collapsed = $("a[data-widgster='expand'][style='display: inline;']");
                    collapsed.click();
                    appConfig['vis_data'] = data.data;
                    appConfig['vis_norm'] = data.norm;
                    $('.visualization').removeClass('hide-element');

                    if ($('#table_raw_data').length > 0) {
                        create_table(data.data, 'table_raw_data', 'raw_data_search');
                    }
                    if ($('#scatter').length > 0) {
                        create_selector('scatter-select-div1', 'scatter-select1', 'x-axis', data.data['columns']);
                        create_selector('scatter-select-div2', 'scatter-select2', 'y-axis', data.data['columns']);
                        scatter('scatter-select1', 'scatter-select2', 'scatter-content', data.data);
                        $("select[id^='scatter-select']").on('change', function () {
                            scatter('scatter-select1', 'scatter-select2', 'scatter-content', appConfig['vis_data']);

                        });

                    }
                    if ($('#hist-select').length > 0) {
                        create_selector('hist-select', 'hist-select1', 'feature', data.data['columns']);
                        histogram('hist-select1', 'hist-content', data.norm, data.data);

                        $("select[id^='hist-select']").on('change', function () {
                            histogram('hist-select1', 'hist-content', appConfig['vis_norm'], appConfig['vis_data']);

                        });
                    }
                    if ($('#corr-mat').length > 0) {
                        heatmap('corr-mat', data.norm.ccols, data.corr);
                    }

                    collapsed.next().click();

                    $('.loader').addClass('hide-element');
                    if (data.num_rows > 1000) {
                        $('#overflow_dataset').text('* Only shown 1000 rows of ' + data.num_rows)
                    } else {
                        $('#overflow_dataset').text('')
                    }
                    $('#get_profile').removeClass('disabled-custom')

                },
                error: function (xmlhttprequest, textstatus, message) {
                    // $('#table_datasets').removeClass('no-clickable');
                    $('.loader').addClass('hide-element');
                    if (textstatus === "timeout") {
                        $.notify("Time out", "error");
                    }
                    else if (textstatus === "error") {
                        $.notify("Server error", "error");
                    }
                    else {
                        $.notify("Error loading dataset", "error");
                    }
                }

            });

        }


    });
    $('#get_profile').on('click', function () {

        $('#get_profile').text('Showing report...')
            .addClass('disabled-custom');

        $.ajax({
            url: "/tabular_profile",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            accepts: {
                json: 'application/json',
            },
            timeout: 120000,
            data: JSON.stringify({
                'datasetname': $('#table_datasets').DataTable().rows({selected: true}).data()[0][0]
            }),
            success: function (data) {
                $("#profile_modal").show();
                $('#modal_body').html(data.data);
                $('#get_profile').text('Show report')
                    .removeClass('disabled-custom');
            },
            error: function (xmlhttprequest, textstatus, message) {
                $('#get_profile').text('Show report')
                    .removeClass('disabled-custom');
                if (textstatus === "timeout") {
                    $.notify("Time out", "error");
                }
                else if (textstatus === "error") {
                    $.notify("Server error", "error");
                }
                else {
                    $.notify("Error loading dataset", "error");
                }
            }
        })
    });
    $('#close').on('click', function () {
        $("#profile_modal").hide();
        $('#modal_body').html('');
        $.noConflict();
    })
});

function get_rows(datasets) {
    let dataset_rows = [];
    datasets.forEach(function (d) {
        if (d[1] === 'Tabular') {
            let conf_row = [d[0], '<a data-id=' + d[0] + ' onclick="ConfirmDelete(this, false)" ><i class="fi flaticon-trash"></i></a>'];
            dataset_rows.push(conf_row)
        }
    });
    return dataset_rows;
}

function upload_table(data) {
    appConfig.handle_key.datasets = data.datasets;
    appConfig.handle_key.data_types = data.data_types;
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
            }
        })
    }
}

function create_selector(id_selector, id_feature, label_text, options) {
    var sel = document.getElementById(id_selector);
    var selectList = document.createElement("select");
    selectList.id = id_feature;
    selectList.setAttribute('style', "margin-right: 5px;");
    var label = document.createElement("label");
    label.setAttribute('for', id_feature);
    label.setAttribute('style', "margin-right: 5px;");
    label.innerText = label_text;

    sel.appendChild(label);
    sel.appendChild(selectList);

    for (var i = 0; i < options.length; i++) {
        var option = document.createElement("option");
        option.value = i;
        option.text = options[i];
        selectList.appendChild(option);
    }
    $('#' + id_feature).addClass('form-control form-control-inline');
}


