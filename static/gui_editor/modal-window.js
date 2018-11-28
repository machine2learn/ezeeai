$(document).ready(function () {
    $('#close').on('click', function () {
        clear_input_modal(dict_wizard);
        close_modal();
    });

    var load_table = $('#table_models').DataTable({
        data: get_load_rows(appConfig.parameters),
        columns: [
            {title: 'Model name'},
            {title: 'Dataset'},
            {title: 'Perf'},
            {title: 'Loss'}],
        'select': 'single',
        fixedHeader: false,
        deferRender: false,

    });

    modal_add_input_select('datasets_availables', appConfig.user_dataset);


    $('#table_models tbody').on('click', 'tr', function (e) {

        if (load_table.row(this, {selected: true}).any()) {
            $('#submit_load').prop('disabled', true);
        }
        else {
            $("#submit_load").prop('disabled', false);
        }

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
            alert("Choose an item from list 1");
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
            $this.parents('.list-group').find("[type=checkbox]").prop("checked", true);
        }
        else {
            $this.parents('.list-group').find("[type=checkbox]").prop("checked", false);
            $this.prop("checked", false);
        }
    });

    $('[type=checkbox]').click(function (e) {
        e.stopPropagation();
    });

    /* toggle checkbox when list group item is clicked */
    $('.list-group a').click(function (e) {

        e.stopPropagation();

        var $this = $(this).find("[type=checkbox]");
        if ($this.is(":checked")) {
            $this.prop("checked", false);
        }
        else {
            $this.prop("checked", true);
        }

        if ($this.hasClass("all")) {
            $this.trigger('click');
        }
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


function create_features_table(data, category_list, dict_wizard) {
    wizard_next(3, dict_wizard);

    if (table_feat_created) {
        $('#table_features').DataTable().clear().rows.add(get_feature_rows(data, category_list)).draw();
    } else {
        $('#table_features').DataTable({
            data: get_feature_rows(data, category_list),
            columns: [{title: 'Features', name: 'Features'},
                {title: 'Category', name: 'Category'},
                {title: '#Unique Values'},
                {title: '(Most frequent, Frequency)'},
                {title: 'Defaults', name: 'Defaults'}, {title: 'Sample 1'},
                {title: 'Sample 2'}, {title: 'Sample 3'}, {title: 'Sample 4'}, {title: 'Sample 5'}],
            fixedHeader: false,
            deferRender: true,
            scrollX: true,
            scroller: true
        });
    }
    return true;
}


function create_image_feature(data, dict_wizard) {
    if (table_feat_created) {
        $('#table_features').DataTable().clear();
        $('#tabular_features').addClass('hidden');
    }
    wizard_next(3, dict_wizard);
    $('#image_features').removeClass('hidden');
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
    var $target_table = $('#table_targets');
    if (table_target_created) {
        $target_table.DataTable().clear().rows.add(get_target_rows(data, category_list)).draw();
    } else {
        $target_table.DataTable({
            data: get_target_rows(data, category_list),
            columns: [{title: 'Features'}, {title: 'Category', name: 'Category'}, {title: '#Unique Values'},
                {title: '(Most frequent, Frequency)'}, {title: 'Defaults'}, {title: 'Sample 1'},
                {title: 'Sample 2'}, {title: 'Sample 3'}, {title: 'Sample 4'}, {title: 'Sample 5'}],
            'select': 'multiple',
            fixedHeader: false,
            deferRender: true,
            scrollX: true,
            scroller: true
        })
    }
    $target_table.DataTable().rows().every(function () {
        var data = this.data()[0];
        if ((targets !== null) && (targets.indexOf(data) >= 0))
            this.select();
    });
    return true
}

function clear_input_modal(dict_wizard) {
    if (table_feat_created)
        $('#table_features').DataTable().clear().rows();
    if (table_target_created)
        $('#table_targets').DataTable().clear().rows();

    update_split([70, 30, 0]);

    $('#wizard4').removeClass('active show')
        .parent().removeClass('active');
    $('#targets').removeClass('active in show');

    $('#wizard1').removeClass('disabled')
        .addClass('active show')
        .parent().addClass('active');
    $('#' + dict_wizard[1]).addClass('active in show');
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
    'none-none': createMenu(none, none, numerical, range, hash, categorical)
};

function get_feature_rows(data, category_list) {
    let result = JSON.parse(data);
    let dataset = [];
    if (category_list !== null)
        result['Category'] = category_list;
    jQuery.map(Object.keys(result['Category']), function (f) {
        dataset.push([f, category[result['Category'][f]], result['#Unique Values'][f], result['(Most frequent, Frequency)'][f],
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
        if (!result['Category'][f].includes("none")) {
            dataset.push([f, result['Category'][f], result['#Unique Values'][f], result['(Most frequent, Frequency)'][f],
                result['Defaults'][f], result['Sample 1'][f], result['Sample 2'][f], result['Sample 3'][f],
                result['Sample 4'][f], result['Sample 5'][f]]);
        }
    });
    return dataset
}


function close_modal() {
    $('#modal').addClass('fade')
        .removeClass('show');
}

function modal_add_input_select(label_name, options) {
    let selectList = $("<select>")
        .attr('id', label_name)
        .attr('name', label_name);
    let option_list = options.map((key) => $('<option>').val(key).text(key));
    $('#selectDataset').append(selectList.append(option_list));
}


function get_rows(configs, parameters) {
    let dataset_selected = $('#datasets_availables').find("option:selected").text();
    let len = configs[dataset_selected].length;
    let dataset_rows = [];
    for (var i = 0; i < len; i++) {
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
        }
    });
    return models;
}