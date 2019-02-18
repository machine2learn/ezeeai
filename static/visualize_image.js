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
            $('.waiting-selection').addClass('hide-element');
            $('.loader').removeClass('hide-element');
            $('.visualization').addClass('hide-element');
            if ($('#label-dist').length > 0) {
                $('#label-dist').children().remove();
            }

            $.ajax({
                url: "/image_graphs",
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                accepts: {
                    json: 'application/json',
                },
                data: JSON.stringify({
                    'datasetname': table_datasets.row(this).data()[0]
                }),
                success: function (data) {
                    var collapsed = $("a[data-widgster='expand'][style='display: inline;']");
                    collapsed.click();
                    let imgs = data.data.data;
                     $('.visualization').removeClass('hide-element');

                    if ($('#img-sidebar').length > 0) {
                        appendImgs(imgs, 'img-sidebar');
                    }
                    if ($('#label-dist').length > 0) {
                        bar_plot('label-dist', Object.keys(data.data.counts), Object.values(data.data.counts));
                    }


                    $('.visualization').removeClass('hide-element');
                    collapsed.next().click();
                    $('.loader').addClass('hide-element');
                    for (var k in imgs) {
                        break
                    }
                    $('#' + k + '_th').click();


                }

            });


        }


    });


});

function appendImgs(imgs, div) {
    let container = $('#' + div);
    for (var key in imgs) {
        let row = $('<div></div>');
        row.addClass('row');

        let img = new Image();
        if (imgs[key].hasOwnProperty('extension'))
            img.src = 'data:image/' + imgs[key]['extension'] + ';base64,' + imgs[key]['img'];
        else
            img.src = 'data:image/jpg;base64,' + imgs[key]['img'];
        img.onclick = function () {
            displayImg(this);
        };
        img.alt = key;
        img.title = key;
        img.classList = 'gallery-thumbnail';
        img.id = key + '_th';

        row.append(img);
        container.append(row);

    }

}

function displayImg(imgs) {
    var expandImg = document.getElementById("expandedImg");
    var imgText = document.getElementById("imgText");
    expandImg.src = imgs.src;
    imgText.innerHTML = imgs.alt;
    expandImg.parentElement.style.display = "block";
}

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


