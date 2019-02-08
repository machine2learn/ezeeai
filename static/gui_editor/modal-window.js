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
        "lengthChange": false,
        fixedHeader: false,
        deferRender: false,

    });

    $('#model_search').keyup(function () {
        load_table.search($(this).val()).draw();


    });

    modal_add_input_select('datasets_availables', appConfig.user_dataset);

    if (appConfig.data_df !== null)
        $('#datasets_availables').val(appConfig.dataset_params.name);

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


function create_features_table(data, category_list, dict_wizard) {
    wizard_next(3, dict_wizard);

    $('#tabular_features').removeAttr('hidden');
    $('#image_features').attr('hidden', '');

    if (table_feat_created) {
        $('#table_features').DataTable().clear().rows.add(get_feature_rows(data, category_list)).draw();
    } else {
        var table_features = $('#table_features').DataTable({
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
            scroller: true,
            "lengthChange": false
        });
        $('#feature_search').keyup(function () {
            table_features.search($(this).val()).draw();

        });
    }
    return true;
}


function create_image_feature(data, dict_wizard) {
    wizard_next(3, dict_wizard);
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
    if (table_target_created) {
        $target_table.DataTable().clear().rows.add(get_target_rows(data, category_list)).draw();
    } else {
        var target_table = $target_table.DataTable({
            data: get_target_rows(data, category_list),
            columns: [{title: 'Features'}, {title: 'Category', name: 'Category'}, {title: '#Unique Values'},
                {title: '(Most frequent, Frequency)'}, {title: 'Defaults'}, {title: 'Sample 1'},
                {title: 'Sample 2'}, {title: 'Sample 3'}, {title: 'Sample 4'}, {title: 'Sample 5'}],
            'select': 'multiple',
            fixedHeader: false,
            deferRender: true,
            scrollX: true,
            scroller: true,
            "lengthChange": false,
        });
        $('#target_search').keyup(function () {
            target_table.search($(this).val()).draw();

        });
    }
    $target_table.DataTable().rows().every(function () {
        var data = this.data()[0];
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

function clear_input_modal(dict_wizard) {
    wizard_next(1, dict_wizard);
    wizard_next(2, dict_wizard);
    $('#image_row').empty();
    $('#image_demo').empty();
    $('#slides').empty();

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
        $("#datasets_availables").val($("#datasets_availables option:first").val());
    }
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
        let u_val = result['#Unique Values'][f];
        if (u_val === -1)
            u_val = 'Not relevant';
        dataset.push([f, category[result['Category'][f]], u_val, result['(Most frequent, Frequency)'][f],
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
        if (!result['Category'][f].includes("none")) {
            dataset.push([f, result['Category'][f], u_val, result['(Most frequent, Frequency)'][f],
                result['Defaults'][f], result['Sample 1'][f], result['Sample 2'][f], result['Sample 3'][f],
                result['Sample 4'][f], result['Sample 5'][f]]);
        }
    });
    return dataset
}


function close_modal() {
    clear_input_modal(dict_wizard);
    $('#modal').addClass('fade');
    $('#modal').hide();

}

function modal_add_input_select(label_name, options) {
    let selectList = $("<select>")
        .attr('id', label_name)
        .attr('name', label_name);

    let tabular_group = $("<optgroup>")
        .attr('id', 'tabular_group')
        .attr('label', 'Tabular dataset');

    let image_group = $("<optgroup>")
        .attr('id', 'image_group')
        .attr('label', 'Image dataset');


    let option_list = Object.keys(options).map((key) => $('<option>').val(key).text(key));
    let tab_list = [];
    let im_lit = [];

    $.each(option_list, function (index, value) {
        if (options[value.text()] === 'tabular') {
            tab_list.push(option_list[index])
        } else {
            im_lit.push(option_list[index])
        }
    });
    image_group.append(im_lit);
    tabular_group.append(tab_list);
    selectList.append(tabular_group);
    selectList.append(image_group);

    $('#selectDataset').append(selectList);

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
        }
    });
    return models;
}

function openModal() {
    document.getElementById('image_modal').style.display = "block";
}

//
function closeModal() {
    document.getElementById('image_modal').style.display = "none";
}

var slideIndex = 1;
//
// showSlides(slideIndex);

function plusSlides(n) {
    showSlides(slideIndex += n);
}

function currentSlide(n) {
    showSlides(slideIndex = n);
}

function showSlides(n) {
    var i;
    var slides = document.getElementsByClassName("mySlides");
    var dots = document.getElementsByClassName("demo");
    var captionText = document.getElementById("caption");
    if (n > slides.length) {
        slideIndex = 1
    }
    if (n < 1) {
        slideIndex = slides.length
    }
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }
    slides[slideIndex - 1].style.display = "block";
    dots[slideIndex - 1].className += " active";
    captionText.innerHTML = dots[slideIndex - 1].alt;
}

function create_images_targets(data) {
    wizard_next(4, dict_wizard);
    $('#tabular_target').attr('hidden', '');
    $('#image_target').removeAttr('hidden');
    $('#image_row').empty();
    $('#image_demo').empty();
    $('#slides').empty();
    let cont = 1;
    $.each(data, function (label, value) {
        let column = $('<div></div>').addClass('column');

        let text = $('<div></div>').addClass('text-block');
        let my_label = $('<p>' + label + '</p>');
        let i = data[label];
        let im = new Image();
        im.src = 'data:image/' + i['extension'] + ';base64,' + i['img'];
        im.id = cont;
        im.onclick = function () {
            openModal();
            currentSlide(this.id);
        };

        im.classList = "hover-shadow cursor";

        column.append(im);
        text.append(my_label);
        column.append(text);
        $('#image_row').append(column);

        let my_slides = $('<div></div>').addClass('mySlides');

        let number_text = $('<div>' + cont + '</div>').addClass('numbertext');
        let im2 = new Image();
        im2.src = 'data:image/' + i['extension'] + ';base64,' + i['img'];
        im2.style = "width:100%";

        my_slides.append(number_text);
        my_slides.append(im2);


        $('#slides').append(my_slides);

        let column_i = $('<div></div>').addClass('column');
        let im3 = new Image();
        if (i.hasOwnProperty('extension'))
            im3.src = 'data:image/' + i['extension'] + ';base64,' + i['img'];
        else
            im3.src = 'data:image/jpg;base64,' + i['img'];
        im3.style = "width:100%";
        im3.addEventListener('click', function (e) {
            currentSlide(this.id)
        });
        im3.alt = label;
        im3.id = cont;
        im3.classList = 'demo cursor';
        column_i.append(im3);
        $('#image_demo').append(column_i);
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