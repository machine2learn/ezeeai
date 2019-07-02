function create_layers(corelayers) {


    Object.keys(corelayers).forEach(function (key) {
        var key_np = key.replace(/ +/g, "");
        let card = $('<div></div>').attr('id', 'card-' + key_np);
        card.addClass('card');
        $('#accordion').append(card);

        let card_header = $('<div></div>').attr('id', 'card-header-' + key_np);
        card.append(card_header);

        let button = $('<button></button>');
        button.addClass('collapsed');
        button
            .attr('href', '#collapse-' + key_np)
            .attr('data-toggle', "collapse")
            .attr('aria-expanded', 'false')
            .attr('aria-controls', 'collapse-' + key_np);
        // .attr('data-parent', "#accordion");
        let i = $('<i class="' + fa_corelayers[key] + '"></i><br>');
        button
            .append(i)
            .append(key);
        card_header.append(button);

        let collapsible = $('<div></div>');
        collapsible
            .attr("id", 'collapse-' + key_np)
            .attr('aria-labelledby', 'card-header-' + key_np)
            .attr('data-parent', "#accordion");
        collapsible.addClass('collapse card-body');


        Object.keys(corelayers[key]).forEach(function (val) {

            const label = $('<label>');
            const input = $('<input>');
            input.attr('id', val)
                .attr('type', 'radio')
                .attr('name', 'radio');
            label.append(input);

            const span = $('<span>');
            span.html(val);
            label.append(span);
            collapsible.append(label);

        });
        card.append(collapsible);
    });
}


let fn_dic = {
    'select': (key, item, value) => add_input_select(key, item['options'], value),
    'boolean': (key, item, value) => add_input_select(key, ['true', 'false'], value),
    'integer': (key, item, value) => add_input_number(key, value, item, '1'),
    'float': (key, item, value) => add_input_number(key, value, item, 'any'),
    'text': (key, item, value) => add_input(key, value, 'text'),
    'integer_list': (key, item, value) => add_input(key, value, 'text')
};

function show_properties(content, id) {
    for (let key in content) {
        if (content.hasOwnProperty(key)) {
            const item = content[key];
            if (key !== 'class_name') {
                fn_dic[item.type](key, item, item['value']);
            }
        }
    }
    let x = $('<input>').attr('value', id).attr('id', 'node_name');
    $('#properties').append(x);
    $('#node_name').hide();
    $('#input_shape').prop('disabled', true);
}

function clear_properties() {
    $('.properties').empty();
}

function add_input(label_name, default_value, type_input) {
    add_label(label_name);

    let x = $('<input>');
    x
        .attr("type", type_input)
        .attr("id", label_name)
        .attr("name", label_name)
        .attr("value", default_value);

    $('.properties').append(x);

}

function add_input_number(label_name, default_value, content, input_step) {
    add_label(label_name);

    let x = $("<input>")
        .attr("type", "number")
        .attr("id", label_name)
        .attr("name", label_name)
        .attr("value", default_value);

    if ('min' in content) {
        x.attr("min", content['min']);
    }

    x.attr("step", input_step);
    let properties = $(".properties");
    properties.append(x);

    let sp = $('<span>').addClass('validity');
    properties.append(sp);

}

function add_input_select(label_name, options, value) {
    add_label(label_name);

    let selectList = $("<select>")
        .attr('id', label_name)
        .attr('name', label_name);

    let option_list = options.map((key) => $('<option>').val(key).text(key));
    selectList.append(option_list);
    $('.properties').append(selectList);
    $('#' + label_name).val(String(value));
}

function add_label(label_name) {
    let label = document.createTextNode(label_name);
    $('.properties').append(label);
}

function encode(s) { //TODO find a better way  to do this
    let out = [];
    for (let i = 0; i < s.length; i++) {
        out[i] = s.charCodeAt(i);
    }
    return new Uint8Array(out);
}


function create_json_model(nodes) {
    const js_json = {"modelTopology": {"keras_version": "2.1.6", "backend": "tensorflow", 'model_config': {}}};
    const py_json = {"keras_version": "2.2.0", "backend": "tensorflow", "class_name": "Model"};
    const config = {"name": "model_1", "layers": []};

    nodes = nodes.filter((node) => ('name' in node.data() && node.data('name') !== 'Loss')); //TODO: Remove the extra node from handling edges

    config['layers'] = nodes
        .map(function (node) {
            const inbound_nodes = node
                .incomers()
                .filter((ele) => ele.isNode())
                .map((ele) => [ele.id(), 0, 0, {}]);

            return {
                'class_name': node.data('class_name'),
                'name': node.id(),
                "inbound_nodes": [inbound_nodes],
                'config': create_layer_config(node.data('content'))
            };
        });

    config['input_layers'] = nodes
        .roots()
        .map((node) => [node.id(), 0, 0]);

    config['output_layers'] = nodes
        .leaves()
        .map((node) => [node.id(), 0, 0]);

    py_json['config'] = config;
    js_json['modelTopology']['model_config'] = {
        'config': config,
        'class_name': 'Model'
    };
    return {'keras_json': py_json, 'tensorflowjs_json': js_json}
}


let ly_dic = {
    'integer_list': (value) => JSON.parse(value),
    'float': (value) => parseFloat(value),
    'integer': (value) => parseInt(value),
    'boolean': (value) => {
        return value;
    },
    'select': (value) => {
        if (value === 'null' || value === '')
            return null;
        return value;
    },
    'text': (value) => {
        if (value === 'null' || value === '')
            return null;
        return value;
    }
};

function get_param_type(param, key) {
    if (initializers.hasOwnProperty(param))
        return initializers[param][key]['type'];
    if (regularizers.hasOwnProperty(param))
        return regularizers[param][key]['type'];
    if (constraints.hasOwnProperty(param))
        return constraints[param][key]['type'];
}

function get_class_name(class_name) {
    if (initializers.hasOwnProperty(class_name) || constraints.hasOwnProperty(class_name))
        return class_name.charAt(0).toUpperCase() + class_name.substring(1);
    return class_name;
}

function create_layer_config(content) {
    let layer_config = {};
    Object.keys(content).map(function (param) {
        if (param !== 'class_name') {
            try {
                layer_config[param] = ly_dic[content[param]['type']](content[param]['value']);
            } catch (e) {
                alert('Invalid value for parameter ' + param + ' in ' + content.name.value);
                throw 'Model could not be validated.'
            }
            if (content[param].hasOwnProperty('config')) {
                layer_config[param] = {};
                var class_name = content[param]['value'];
                layer_config[param]['class_name'] = get_class_name(class_name);
                layer_config[param]['config'] = {};
                Object.keys(content[param]['config']).forEach(function (key) {
                    try {
                        let type = get_param_type(content[param]['value'], key);
                        layer_config[param]['config'][key] = ly_dic[type](content[param]['config'][key]);
                    } catch (e) {
                        alert('Invalid value for parameter ' + param + '/' + key + ' in ' + content.name.value);
                        throw 'Model could not be validated.'
                    }
                });

            }
        }
    });


    return layer_config;
}

function add_ba_size(shape) {
    if (shape[0] == null || shape[0] === "None")
        shape[0] = 'None';
    else
        shape.unshift("None");
    return shape
}

function zip(arrays) {
    return arrays[0].map(function (_, i) {
        return arrays.map(function (array) {
            return array[i]
        })
    });
}

function add_submit_input(label_name, default_value) {
    let x = $('<input>');
    x
        .attr("type", 'hidden')
        .attr("name", label_name)
        .attr("value", default_value);
    $('#submitform').append(x);
}

function redraw_models_table(table_id, data){
    if ($.fn.dataTable.isDataTable('#' + table_id)) {
        $('#' + table_id).DataTable().destroy();
    }
    $('#' + table_id).DataTable({
        data: get_load_rows(data),
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
}