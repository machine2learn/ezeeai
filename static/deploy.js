$(document).ready(function () {

    var t = document.createTextNode(JSON.stringify(appConfig.handle_key.example.d, null, 4));
    document.getElementById('req').appendChild(t);
    t = document.createTextNode(appConfig.handle_key.example.curl);
    document.getElementById('cresp').appendChild(t);
    t = document.createElement("br")
    document.getElementById('cresp').appendChild(t);
    t = document.createElement("br")
    document.getElementById('cresp').appendChild(t);
    t = document.createTextNode(JSON.stringify(appConfig.handle_key.example.output, null, 4));
    document.getElementById('cresp').appendChild(t);


    table_tag = $('#deploy');
    if ($("#deploy tr").hasClass("selected")) {
        $("input").prop('disabled', false);
    }
    table = table_tag.DataTable({
        "columnDefs": [
            {
                "render": function (data, type, row) {
                    return data == -1 ? 'Not relevant' : data;
                },
                "targets": 2
            }
        ],
        'ordering': false,
        'select': 'api'
    });

    $('#deploy tbody').on('click', 'tr', function () {
        if (table.row(this, {selected: true}).any()) {
            table.row(this).deselect();
        }
        else {
            table.row(this).select();
        }

        if (table.rows({selected: true}).any()) {
            $('#ddiv').attr('class', '');
        }
        else {
            $('#ddiv').attr('class', 'hidden');
        }
    });


    $('form').submit(function () {
        // let selected_rows = table.rows({selected: true}).data().map
        let selected_rows = [];
        table.rows({selected: true}).every(function (rowIdx, tableLoop, rowLoop) {
            selected_rows.push(this.data()[0]);
        });
        let input = $("<input>")
            .attr("type", "hidden")
            .attr("name", "selected_rows").val(JSON.stringify(selected_rows));
        $('form').append($(input));
    });

});
