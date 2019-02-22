$(document).ready(function () {

    // var t = document.createTextNode(JSON.stringify(appConfig.handle_key.example.d, null, 4));
    // document.getElementById('req').appendChild(t);
    // t = document.createTextNode(appConfig.handle_key.example.curl);
    // document.getElementById('cresp').appendChild(t);
    // t = document.createElement("br")
    // document.getElementById('cresp').appendChild(t);
    // t = document.createElement("br")
    // document.getElementById('cresp').appendChild(t);
    // t = document.createTextNode(JSON.stringify(appConfig.handle_key.example.output, null, 4));
    // document.getElementById('cresp').appendChild(t);
    //
    //
    // table_tag = $('#deploy');
    // if ($("#deploy tr").hasClass("selected")) {
    //     $("input").prop('disabled', false);
    // }
    // table = table_tag.DataTable({
    //     "columnDefs": [
    //         {
    //             "render": function (data, type, row) {
    //                 return data == -1 ? 'Not relevant' : data;
    //             },
    //             "targets": 2
    //         }
    //     ],
    //     'ordering': false,
    //     'select': 'api'
    // });
    //
    // $('#deploy tbody').on('click', 'tr', function () {
    //     if (table.row(this, {selected: true}).any()) {
    //         table.row(this).deselect();
    //     }
    //     else {
    //         table.row(this).select();
    //     }
    //
    //     if (table.rows({selected: true}).any()) {
    //         $('#ddiv').attr('class', '');
    //     }
    //     else {
    //         $('#ddiv').attr('class', 'hidden');
    //     }
    // });
    //
    //
    // $('form').submit(function () {
    //     // let selected_rows = table.rows({selected: true}).data().map
    //     let selected_rows = [];
    //     table.rows({selected: true}).every(function (rowIdx, tableLoop, rowLoop) {
    //         selected_rows.push(this.data()[0]);
    //     });
    //     let input = $("<input>")
    //         .attr("type", "hidden")
    //         .attr("name", "selected_rows").val(JSON.stringify(selected_rows));
    //     $('form').append($(input));
    // });
    $('.widget').widgster();

    draw_models_select(appConfig.handle_key.models);


    $('#model_name').on('change', function () {
        enable_checkpoints();
        $('.waiting-selection-ckpt').removeClass('hide-element');
        $('#feature-div').addClass('hide-element');
        $('#prediction_div').addClass('hide-element');


        let model_name = $(this).val();
        $('#perf').text(appConfig.handle_key.models[model_name]['perf']);
        $('#loss').text(appConfig.handle_key.models[model_name]['loss']);

        $('.waiting-selection').addClass('hide-element');
        $('.loader').removeClass('hide-element');

        $.ajax({
            url: "/default_prediction",
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

                draw_checkpoints(data.checkpoints, data.metric);


            }
        })
    });

});

function draw_checkpoints(checkpoints, metric) {
    let table_checkpoints = $('#table_checkpoints').DataTable({
        data: get_rows(checkpoints),
        columns: [{title: 'Checkpoint'}, {title: metric}, {title: 'Loss'}],
        searching: true,
        'select': 'multi',
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