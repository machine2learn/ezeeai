$(document).ready(function () {

    var dataset_rows = get_dataset_rows(appConfig.user_dataset);
    var table_datasets = $('#table_datasets').DataTable({
        data: dataset_rows,
        columns: [{title: 'Dataset'}, {title: 'Type'}],
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

    });
    $('#data_search').keyup(function () {
        table_datasets.search($(this).val()).draw();

    });

    if (appConfig.dataset_params !== null) {
        table_datasets.rows().every(function () {
            var data = this.data()[0];
            if (appConfig.dataset_params.name === data) {
                this.select();
                $("#select_continue").prop('disabled', false);
            }

        });
    }

    var load_table = $('#table_models').DataTable({
        data: get_load_rows(appConfig.parameters),
        columns: [
            {title: 'Model name'},
            {title: 'Dataset'},
            {title: 'Perf'},
            {title: 'Loss'}],
        'select': 'single',
        "lengthChange": false,
        fixedHeader: false,
        deferRender: false,
        "drawCallback": function () {
            if ($(this).DataTable().rows()[0].length <= 10) {
                let id = '#' + $(this).attr('id');
                $(id + '_paginate').remove();
                $(id + '_info').remove();
            }

        }

    });

    $('#model_search').keyup(function () {
        load_table.search($(this).val()).draw();


    });


    $('#table_models tbody').on('click', 'tr', function (e) {
        if (load_table.row(this, {selected: true}).any())
            $('#submit_load').prop('disabled', true);
        else if (load_table.page.info().recordsDisplay === 0) {
            $('#submit_load').prop('disabled', true);
        }
        else $("#submit_load").prop('disabled', false);

    });

    $('#form_load').submit(function () {
        let model_name;
        let datasset_name;
        $('#table_models').DataTable().rows({selected: true}).every(function () {
            model_name = this.data()[0];
            datasset_name = this.data()[1];
        });
        $('<input />').attr('type', 'hidden')
            .attr('name', 'model')
            .attr('value', model_name)
            .appendTo('#form_load');
        $('<input />').attr('type', 'hidden')
            .attr('name', 'dataset')
            .attr('value', datasset_name)
            .appendTo('#form_load');
        return true;
    });

    $('.add').click(function () {
        $('.all').prop("checked", false);
        var items = $("#list1 input:checked:not('.all')");
        var n = items.length;
        if (n > 0) {
            items.each(function (idx, item) {
                var choice = $(item);
                choice.prop("checked", false);
                choice.parent().appendTo("#list2");
            });
        }
        else {
            alert("Choose an option");
        }
    });

    $('.remove').click(function () {
        $('.all').prop("checked", false);
        var items = $("#list2 input:checked:not('.all')");
        items.each(function (idx, item) {
            var choice = $(item);
            choice.prop("checked", false);
            choice.parent().appendTo("#list1");
        });
    });

    /* toggle all checkboxes in group */
    $('.all').click(function (e) {
        e.stopPropagation();
        var $this = $(this);
        if ($this.is(":checked")) {
            $this.parents('.list-group').find(".pull-right").prop("checked", true);
        }
        else {
            $this.parents('.list-group').find(".pull-right").prop("checked", false);
            $this.prop("checked", false);
        }
    });

    $('[type=checkbox]').click(function (e) {
        e.stopPropagation();
    });

    /* toggle checkbox when list group item is clicked */

    $('.collapsible').collapsible();
    $('.collapse-aug').hide();

    $('.list-group a').on('click', function (e) {
        $('.collapse-aug').hide();
        $('.collapse-' + this.id).show();
    })
        .click(function (e) {
            e.stopPropagation();
            let $this = $(this).find(".pull-right");
            if ($this.is(":checked"))
                $this.prop("checked", false);
            $this.prop("checked", true);
            if ($this.hasClass("all"))
                $this.trigger('click');
        });
});


function wizard_next(number, dict_wizard) {
    $('#wizard' + (number - 1)).removeClass('active show')
        .parent().removeClass('active');
    $('#' + dict_wizard[number - 1]).removeClass('active in show');
    $('#wizard' + number).removeClass('disabled')
        .addClass('active show')
        .parent().addClass('active');
    $('#' + dict_wizard[number]).addClass('active in show');
}


function create_features_table(data, category_list, dict_wizard, r2n = false) {
    $('#tabular_features').removeAttr('hidden');
    $('#image_features').attr('hidden', '');

    if (table_feat_created)
        remove_table('table_features');
    // $('#table_features').DataTable().clear().rows.add(get_feature_rows(data, category_list)).draw();
    // } else {
    var table_features = $('#table_features').DataTable({
        data: get_feature_rows(data, category_list, r2n),
        columns: [{title: 'Features', name: 'Features'},
            {title: 'Category', name: 'Category'},
            {title: '#Unique Values'},
            {title: 'Most frequent'},
            {title: 'Frequency'},
            {title: 'Defaults', name: 'Defaults'}, {title: 'Sample 1'},
            {title: 'Sample 2'}, {title: 'Sample 3'}, {title: 'Sample 4'}, {title: 'Sample 5'}],
        fixedHeader: false,
        deferRender: true,
        scrollX: true,
        scroller: true,
        "lengthChange": false,
        "drawCallback": function () {
            if ($(this).DataTable().rows()[0].length <= 10) {
                let id = '#' + $(this).attr('id');
                $(id + '_paginate').remove();
                $(id + '_info').remove();
            }

        }
    });
    $('#feature_search').keyup(function () {
        table_features.search($(this).val()).draw();

    });

    return true;
}

function remove_table(id) {
    if ($.fn.DataTable.isDataTable('#' + id)) {
        $('#' + id).DataTable().destroy();
        $('#' + id + ' tbody').empty();
        $('#' + id + ' thead').empty();
    }
}


function create_image_feature(data, dict_wizard) {
    $('#tabular_features').attr('hidden', '');
    $('#image_features').removeAttr('hidden');
    $('#height').val(data.height);
    $('#width').val(data.width);
    return true;
}


function update_split(values) {
    $(".js-range-slider-1").data()['ionRangeSlider'].update({from: values[0]});
    $(".js-range-slider-2").data()['ionRangeSlider'].update({from: values[1]});
    $(".js-range-slider-3").data()['ionRangeSlider'].update({from: values[2]});
}

function create_target_table(data, category_list, targets, dict_wizard) {
    wizard_next(4, dict_wizard);
    $('#tabular_target').removeAttr('hidden');
    $('#image_target').attr('hidden', '');
    var $target_table = $('#table_targets');
    if (table_target_created)
        remove_table('table_targets');
    // $target_table.DataTable().clear().rows.add(get_target_rows(data, category_list)).draw();
    // } else {
    var target_table = $target_table.DataTable({
        data: get_target_rows(data, category_list),
        columns: [{title: 'Features'}, {title: 'Category', name: 'Category'}, {title: '#Unique Values'},
            {title: 'Most frequent'},
            {title: 'Frequency'}, {title: 'Defaults'}, {title: 'Sample 1'},
            {title: 'Sample 2'}, {title: 'Sample 3'}, {title: 'Sample 4'}, {title: 'Sample 5'}],
        'select': 'multiple',
        fixedHeader: false,
        deferRender: true,
        scrollX: true,
        scroller: true,
        "lengthChange": false,
        "drawCallback": function () {
            if ($(this).DataTable().rows()[0].length <= 10) {
                let id = '#' + $(this).attr('id');
                $(id + '_paginate').remove();
                $(id + '_info').remove();
            }

        }
    });
    $('#target_search').keyup(function () {
        target_table.search($(this).val()).draw();

    });

    $target_table.DataTable().rows().every(function () {
        let data = this.data()[0];
        if ((targets !== null) && (targets.indexOf(data) >= 0))
            this.select();
    });
    return true
}

function clear_table(id) {
    var table = $('#' + id).DataTable();
    let rows = table
        .rows()
        .remove()
        .draw();
}

function clear_input_modal(dict_wizard, clear_select) {
    wizard_next(1, dict_wizard);
    wizard_next(2, dict_wizard);
    $('.horizontal-slide').empty();

    if (table_target_created)
        clear_table('table_targets');
    wizard_next(3, dict_wizard);

    $("#height").val(0);
    $("#width").val(0);
    $("#normalization").val($("#normalization option:first").val());
    let aug_options = ['saturation', 'contrast', 'brightness', 'randomhue', 'quality', 'flip', 'rotation'];
    $.each(aug_options, function (index, id) {
        $('#' + id).appendTo("#list1");
    });
    $("#list1 input").each(function () {
        this.value = null
    });
    wizard_next(4, dict_wizard);

    if (table_feat_created) {
        clear_table('table_features');
        update_split([70, 30, 0]);

    }

    $('#wizard4').removeClass('active show')
        .parent().removeClass('active');
    $('#targets').removeClass('active in show');

    $('#wizard1').removeClass('disabled')
        .addClass('active show')
        .parent().addClass('active');
    $('#' + dict_wizard[1]).addClass('active in show');

    if (clear_select) {
        $('#table_datasets').DataTable().rows({selected: true}).every(function () {

            this.deselect();
            $("#select_continue").prop('disabled', true);
        });
    }


}

function createMenu(selected, ...items) {
    let result = $("<select>");
    result.addClass('selfeat');
    for (let i = 0; i < items.length; i++) {
        result.append(options[items[i]]());
    }
    result.find('option[value=' + selected + ']').attr('selected', true);
    return result.prop('outerHTML');
}

let categorical = 'categorical';
let hash = 'hash';
let none = 'none';
let range = 'range';
let numerical = 'numerical';

let options = {
    numerical: () => $('<option>').attr('value', numerical).text('Numerical'),
    categorical: () => $('<option>').attr('value', categorical).text('Categorical'),
    hash: () => $('<option>').attr('value', hash).text('Hash'),
    none: () => $('<option>').attr('value', none).text('No use'),
    range: () => $('<option>').attr('value', range).text('Range')
};

let category = {
    'categorical': createMenu(categorical, categorical, hash, none),
    'hash': createMenu(hash, hash, categorical, none),
    'int-range': createMenu(range, range, hash, categorical, numerical, none),
    'range': createMenu(range, range, hash, categorical, numerical, none),
    'int-hash': createMenu(hash, hash, categorical, numerical, none),
    'int-category': createMenu(hash, hash, range, categorical, numerical, none),
    'bool': createMenu(categorical, categorical, none),
    'numerical': createMenu(numerical, numerical, none),
    'none': createMenu(none, none, categorical, hash, range, numerical),
    'none-categorical': createMenu(none, none, categorical, hash),
    'none-hash': createMenu(none, none, categorical, hash),
    'none-range': createMenu(none, none, range, hash, categorical, numerical),
    'none-int-range': createMenu(none, none, range, hash, categorical, numerical),
    'none-int-category': createMenu(none, none, range, hash, categorical, numerical),
    'none-int-hash': createMenu(none, none, range, hash, categorical, numerical),
    'none-numerical': createMenu(none, none, numerical),
    'none-bool': createMenu(none, none, categorical),
    'none-none': createMenu(none, none, numerical, range, hash, categorical),
    'range-numerical': createMenu(numerical, numerical, range, hash, categorical, none),
};

function get_feature_rows(data, category_list, n2r = false) {
    let result = JSON.parse(data);
    let dataset = [];
    if (category_list !== null)
        result['Category'] = category_list;
    jQuery.map(Object.keys(result['Category']), function (f) {
        let u_val = result['#Unique Values'][f];
        if (u_val === -1)
            u_val = 'Not relevant';
        let cat = result['Category'][f];
        if (n2r && cat.includes('range'))
            cat = 'range-numerical';
        let mff = result['(Most frequent, Frequency)'][f];
        dataset.push([f, category[cat], u_val, mff[0], mff[1],
            result['Defaults'][f], result['Sample 1'][f], result['Sample 2'][f], result['Sample 3'][f],
            result['Sample 4'][f], result['Sample 5'][f]]);
    });
    return dataset
}

function get_target_rows(data, category_list) {
    let result = JSON.parse(data);
    let dataset = [];
    if (category_list !== null)
        result['Category'] = category_list;
    jQuery.map(Object.keys(result['Category']), function (f) {
        let u_val = result['#Unique Values'][f];
        if (u_val === -1)
            u_val = 'Not relevant';
        let mff = result['(Most frequent, Frequency)'][f];
        if (!result['Category'][f].includes("none")) {
            dataset.push([f, result['Category'][f], u_val, mff[0], mff[1],
                result['Defaults'][f], result['Sample 1'][f], result['Sample 2'][f], result['Sample 3'][f],
                result['Sample 4'][f], result['Sample 5'][f]]);
        }
    });
    return dataset
}


function close_modal() {
    clear_input_modal(dict_wizard, true);
    $('#modal').addClass('fade');
    $('#modal').hide();

}


function get_rows(configs, parameters) {
    let dataset_selected = $('#datasets_availables').find("option:selected").text();
    let len = configs[dataset_selected].length;
    let dataset_rows = [];
    for (let i = 0; i < len; i++) {
        let config_name = configs[dataset_selected][i];
        let conf_row = [config_name,
            parameters[dataset_selected + '_' + config_name]["model"],
            parameters[dataset_selected + '_' + config_name]["perf"],
            parameters[dataset_selected + '_' + config_name]["loss"]];
        dataset_rows.push(conf_row)
    }
    dataset_rows.push(['new_config', '', '', '', '']);
    return dataset_rows;
}


function get_load_rows(parameters) {
    let models = [];
    jQuery.map(Object.keys(parameters), function (f) {
        if ('dataset' in parameters[f]) {
            if ('perf' in parameters[f])
                models.push([f, parameters[f]['dataset'], parameters[f]['perf'], parameters[f]['loss']]);
            else
                models.push([f, parameters[f]['dataset'], 'Not evaluated yet', 'Not evaluated yet']);
        } else {
            models.push([f, 'Not assigned yet', 'Not evaluated yet', 'Not evaluated yet']);
        }
    });
    return models;
}

//TODO
function create_images_targets(data) {
    wizard_next(4, dict_wizard);
    $('#tabular_target').attr('hidden', '');
    $('#image_target').removeAttr('hidden');
    $('.horizontal-slide').empty();
    let cont = 1;
    $.each(data, function (label, value) {
        let column = $('<li></li>');
        let text = $('<div></div>'); //.addClass('text-block');
        let my_label = $('<p>' + label + '</p>');
        let i = data[label];
        let im = new Image();
        im.src = 'data:image/' + i['extension'] + ';base64,' + i['img'];
        im.id = cont;
        im.classList = "thumbnail";

        column.append(im);
        text.append(my_label);
        column.append(text);
        $('.horizontal-slide').append(column);

        cont += 1;
    });
}

function restore_features_images(height, width, norm, aug_op, aug_param) {
    $('#image_features').removeAttr('hidden');
    $('#tabular_features').attr('hidden', '');

    wizard_next(3, dict_wizard);

    $("#height").val(height);
    $("#width").val(width);
    $("#normalization").val(norm);

    $.each(aug_op, function (key, val) {
        $('#' + val).appendTo("#list2");
    });
    $.each(aug_param, function (key, val) {
        let $input = $('#' + key);
        if ($input[0].type === 'radio')
            $input.attr('checked', val);
        if ($input[0].type === 'checkbox')
            $input.prop('checked', val);
        else
            $input.val(val);

    })

}

function get_dataset_rows(datasets) {
    let dataset_rows = [];
    Object.keys(datasets).forEach(function (d) {
        let type = 'Tabular';
        if (datasets[d].includes('image')) {
            type = 'Image';
        }
        let conf_row = [d, type];
        dataset_rows.push(conf_row)
    });
    return dataset_rows;
}

function reset_wizard() {
    clear_input_modal(dict_wizard, true);
    $('#wizard2').addClass('disabled');
    $('#wizard3').addClass('disabled');
    $('#wizard4').addClass('disabled');
}

function range2numerical() {
    create_features_table(appConfig.data_df, null, dict_wizard, true);
    $('#range-numerical').prop('disabled', true);
}

$(function () {
    $("input[type='number']").keydown(function () {
        let min = -9999;
        let max = 9999;
        if ($(this).prop('min') !== undefined && $(this).prop('min') !== '') {
            min = $(this).prop('min')
        }
        if ($(this).prop('max') !== undefined && $(this).prop('max') !== '') {
            max = $(this).prop('max')
        }

        // Save old value.
        if (!$(this).val() || (parseFloat($(this).val()) <= max && parseFloat($(this).val()) >= min))
            $(this).data("old", $(this).val());
    });
    $("input[type='number']").keyup(function () {
        let min = -9999;
        let max = 9999;
        if ($(this).prop('min') !== undefined && $(this).prop('min') !== '') {
            min = $(this).prop('min')
        }
        if ($(this).prop('max') !== undefined && $(this).prop('max') !== '') {
            max = $(this).prop('max')
        }
        // Check correct, else revert back to old value.
        if (!$(this).val() || (parseFloat($(this).val()) <= max && parseFloat($(this).val()) >= min))
            ;
        else
            $(this).val($(this).data("old"));
    });
});