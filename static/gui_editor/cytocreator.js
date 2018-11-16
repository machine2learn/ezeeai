var counters = {};
var cy;
var table_feat_created = false;
var table_target_created = false;
var inputs_layers = {};

document.addEventListener('DOMContentLoaded', function () {
    $('#inp').val(appConfig.m_name);
    $('#submit').prop('disabled', true);
    create_layers(corelayers);

    cy = cytoscape({
        container: document.getElementById('cy'),
        elements: appConfig.cy_model.elements,
        style: cyto_styles
    });
    add_icons_nodes();

    //Update counters (nodes names)
    cy.nodes().forEach(function (node) {
        counters[node.data().name.split('_')[0]] = parseInt(node.data().name.split('_')[1]);
    });


    let edge_bending_options = {
        // this function specifies the positions of bend points
        bendPositionsFunction: function (ele) {
            return ele.data('bendPointPositions');
        },
        // whether to initilize bend points on creation of this extension automatically
        initBendPointsAutomatically: true,
        // whether the bend editing operations are undoable (requires cytoscape-undo-redo.js)
        undoable: false,
        // the size of bend shape is obtained by multipling width of edge with this parameter
        bendShapeSizeFactor: 6,
        // whether to start the plugin in the enabled state
        enabled: true,
        // title of add bend point menu item (User may need to adjust width of menu items according to length of this option)
        addBendMenuItemTitle: "Add Bend Point",
        // title of remove bend point menu item (User may need to adjust width of menu items according to length of this option)
        removeBendMenuItemTitle: "Remove Bend Point",
        // whether the bend point can be moved by arrow keys
        moveSelectedBendPointsOnKeyEvents: function () {
            return true;
        }
    };

    cy.edgeBendEditing(edge_bending_options);
    center_layout(cy);


    let options = {
        // List of initial menu items
        menuItems: [
            {
                id: 'remove', // ID of menu item
                content: 'remove', // Display content of menu item
                tooltipText: 'remove', // Tooltip text for menu item
                selector: 'node, edge',
                onClickFunction: function (event) { // The function to be executed on click
                    let target = event.target || event.cyTarget;
                    // if ((target.data().class_name === "InputLayer") && !(target.data().name in Object.keys(inputs_layers)))
                    //     clear_input_modal(dict_wizard);
                    if (inputs_layers.hasOwnProperty(target.data().name))
                        delete inputs_layers[target.data().name];
                    target.remove();
                    $('#' + target.id()).remove();
                    disable_submit_button();
                },
                disabled: false, // Whether the item will be created as disabled
                hasTrailingDivider: true, // Whether the item will have a trailing divider
                coreAsWell: false // Whether core instance have this item on cxttap
            },
            {
                id: 'add-node',
                content: 'add node',
                tooltipText: 'add node',
                selector: 'node',
                coreAsWell: true,
                onClickFunction: function (event) {
                    add_new_node(event);

                }
            }
        ]
    };
    cy.contextMenus(options);
    cy.edgehandles({snap: true});
    let ur = cy.undoRedo({undoableDrag: false});
    cy.clipboard();


    document.addEventListener("keydown", function (e) {
        if ((e.ctrlKey || e.metaKey) && e.target.nodeName === 'BODY') {
            if (e.which === 67) // CTRL + C
                cy.clipboard().copy(cy.$(":selected"));
            else if (e.which === 86) // CTRL + V
                ur.do("paste");
            else if (e.which === 65) { // + A
                cy.elements().select();
                e.preventDefault();
            }
            disable_submit_button()
        } else if (e.which === 46 || e.which === 8) { // + Remove
            if ($(":focus").length === 0) {
                let node = cy.nodes().filter((node) => (node.selected()));
                // if ((node.data().class_name === "InputLayer") && !(node.data().name in Object.keys(inputs_layers)))
                //     clear_input_modal(dict_wizard);
                if (inputs_layers.hasOwnProperty(node.data().name))
                    delete inputs_layers[node.data().name];
                node.remove();
                $('#' + node.id()).remove();
                let selected_edge = cy.edges().filter((edge) => (edge.selected()));
                selected_edge.remove();
                disable_submit_button();
            }
        }
    });


    cy.on('doubleTap', 'node', function (event) {
        if (event.target.data().class_name.includes('InputLayer')) {
            $('#modal').removeClass('fade')
                .addClass('show');
            disable_submit_button();
            if (inputs_layers.hasOwnProperty(event.target.data().name)) {
                let name = event.target.data().name;
                $('#datasets_availables').val(inputs_layers[name].dataset);
                update_split(inputs_layers[name].split.split(','));
                wizard_next(2, dict_wizard);
                table_feat_created = create_features_table(inputs_layers[name]['df'], inputs_layers[name]['category_list'], dict_wizard);
                table_target_created = create_target_table(inputs_layers[name]['df'], inputs_layers[name]['category_list'], inputs_layers[name]['targets'], dict_wizard)
                $('#normalize').prop('checked', inputs_layers[name]['normalize']);
            }
        }
    });

    var tappedBefore;
    var tappedTimeout;
    cy.on('tap', function (event) {
        let tappedNow = event.target;
        if (tappedTimeout && tappedBefore) {
            clearTimeout(tappedTimeout);
        }
        if (tappedBefore === tappedNow) {
            tappedNow.trigger('doubleTap');
            tappedBefore = null;
        } else {
            tappedTimeout = setTimeout(function () {
                tappedBefore = null;
            }, 300);
            tappedBefore = tappedNow;
        }
    });

    cy.on('tap', function (event) {
        let evtTarget = event.target;
        if (evtTarget === cy)
            add_new_node(event);
    });

    cy.on('tap', 'node', function (evt) {
        clear_properties();
        show_properties(evt.target.data().content, evt.target.id());
    });

    cy.on('ehcomplete', (event, sourceNode, targetNode, addedEles) => {
        if (targetNode.data().name.includes('InputLayer')) {
            addedEles.remove();
        } else if (targetNode.indegree() > 1 && !(targetNode.data().name in corelayers['Merge Layers'])) {
            addedEles.remove();
        } else if (sourceNode.data().name.includes('Loss')) {
            addedEles.remove();
        }
        disable_submit_button();
    });


    $('#properties').bind('input', function (e) {
        let id = $('#node_name').val();
        let new_value_id = e.target.id;
        let cy_element = cy.getElementById(id).data();
        if (is_valid(cy_element.content['type'], e.target.value, e.target.id, cy)) {
            e.target.classList.remove('invalid');
            if (!cy_element.content.hasOwnProperty(new_value_id)) {
                let param = new_value_id.split('-')[0];
                cy_element.content[param]['config'] = {};
                $.map($('#properties :input[id^=' + param + '-]'), function (i) {
                    let field = i.id.split('-')[1];
                    cy_element.content[param]['config'][field] = i.value;
                });
            } else {
                cy_element.content[new_value_id]['value'] = e.target.value;
                if (cy_element.content[new_value_id].hasOwnProperty('config'))
                    delete  cy_element.content[new_value_id]['config'];
                if (e.target.id === 'name') {
                    cy_element.name = e.target.value;
                    add_icons_nodes();
                    zoom(cy, 0.00000001); //find better way
                }
            }

        } else
            e.target.classList.add('invalid');
        disable_submit_button();
    })
        .on('change', 'select', function (e) {
            let prop = this.name;
            let param = $(e.target).val();
            show_params_config(prop, param, null)
        })
        .on('click', 'select', function (e) {
            let prop = this.name;
            let param = $(e.target).val();
            let node = cy.nodes().filter((node) => (node.selected()));
            let config = null;
            if (node.data()['content'][prop].hasOwnProperty('config')) {
                config = node.data()['content'][prop]['config']
            }
            show_params_config(prop, param, config)
        });


    function add_new_node(event) {
        let radio_checked = document.querySelector('input[name="radio"]:checked');
        if (radio_checked) {
            let id_checked = document.querySelector('input[name="radio"]:checked').id;
            let root = Object.keys(corelayers).find(key => id_checked in corelayers[key]);
            Object.keys(corelayers).forEach(function (key) {
                let content = $.extend(true, {}, corelayers[key][id_checked]);

                if (id_checked in corelayers[key]) {
                    if (id_checked === 'InputLayer' && 'input_shape' in content) {
                        content['input_shape']['value'] = appConfig.input_shape;
                    }
                    if (id_checked in counters) {
                        counters[id_checked] += 1;
                    } else {
                        counters[id_checked] = 0;
                    }
                    content['name'] = {'type': 'text'};
                    content['name']['value'] = id_checked + "_" + counters[id_checked].toString();
                    let new_node = cy.add({
                        group: "nodes",
                        data: {
                            name: id_checked + "_" + counters[id_checked].toString(),
                            class_name: id_checked,
                            root: root,
                            weight: 75,
                            content: content
                        },
                        position: event.position
                    });
                    disable_submit_button();
                }
                add_icons_nodes();
            });
        }
    }

    function add_icons_nodes() {
        cy.nodeHtmlLabel(Object.keys(fa_corelayers).map(function (key) {
                return {
                    query: "node[root = '" + key + "']",
                    tpl: function (data) {
                        return "<p class='icon_layer'> <i class='" + fa_corelayers[data.root] + "'> </i>" + data.name + "</p>"
                    }
                }
            })
        );
    }

    function check_input_output() {
        let input_nodes = cy.filter(function (element, i) {
            if (element.isNode() && 'name' in element.data())
                if (element.data().class_name.includes('InputLayer') && element.data().content.input_shape.value !== undefined)
                    return true;
            return false;
        });
        let output_nodes = cy.filter(function (element, i) {
            if (element.isNode() && 'name' in element.data())
                if (element.data('name').includes('Loss'))
                    return true;
            return false;
        });

        if (input_nodes.length !== 1)
            return 'Input layer not exists or  dataset not correctly added';

        if (input_nodes.length !== 1 || output_nodes.length !== 1)
            return 'Just one input layer and one loss layer are allowed';

        let dnn_nodes = cy.nodes().filter((node) => ('DNN' === node.data().class_name));
        let all = cy.nodes().filter((node) => ('class_name' in node.data()));

        if (dnn_nodes.length === 1 && all.length > 3)
            return 'If you use DNN layer is not posible use another layer (except input and loss)';
        return true;
    }

    $('#validate_model').on('click', async function (event) {
        cy.remove(cy.nodes().filter((node) => (!('name' in node.data()))));
        let mess = check_input_output();
        if (mess !== true) {
            alert(mess);
            disable_submit_button();
            return false;

        } else {
            let dnn = cy.nodes().filter((node) => ('DNN' === node.data().class_name));
            let dnn_layers = dnn.length;
            if (dnn_layers === 1) {
                var loss = dnn.successors().filter((node) => (node.data().hasOwnProperty('class_name') && node.data()['class_name'] === 'Loss')).data().content.function.value;
                $('#submit').removeClass('hidden')
                    .prop('disabled', false);
                $('#validate_model').addClass('hidden');
                send_canned(dnn, cy.json(), loss);


            } else if (dnn_layers === 0) {
                let loss_node = cy.nodes().filter((node) => (node.data('name').includes('Loss')));
                let edges = loss_node.connectedEdges();
                let loss_function = loss_node.data('content')['function'].value;
                cy.remove(loss_node);
                let models = create_json_model(sort_nodes(cy));
                cy.add(loss_node);
                cy.add(edges);
                await tf_load_model(sort_nodes(cy), models, loss_function, cy.json(), cy, loss_node);
                event.preventDefault();
            }
            else {
                alert("Just one Canned Model allowed");
                disable_submit_button();
                return false;
            }
        }
    });
    $('#inp').on('change', function () {
        disable_submit_button();
    });

    $('#zoom_handler').on('click', function () {
        center_layout(cy);
    });
    $('#zoom_plus').on('click', function () {
        zoom(cy, 0.1);
    });
    $('#zoom_minus').on('click', function () {
        zoom(cy, -0.1);
    });

});

function show_params_config(prop, param, saved_config) {
    var config;
    var prop_pre = prop.concat('-');
    $('#properties [id^=' + prop_pre + ']').remove();
    config = null;
    if (prop.includes('initializer')) {
        if (initializers.hasOwnProperty(param))
            config = initializers[param];
    } else if (prop.includes('regularizer')) {
        if (regularizers.hasOwnProperty(param))
            config = regularizers[param];
    } else if (prop.includes('constraint')) {
        if (constraints.hasOwnProperty(param))
            config = constraints[param];
    } else {
        return;
    }

    if (config !== null) {
        if (saved_config !== null) {
            Object.keys(config).forEach(function (key) {
                config[key]['value'] = saved_config[key]
            });
        }
        Object.keys(config).forEach(function (key) {
            append_after(key, config[key], prop); //param, config, parent

        });
    }
}


$(document).ready(function () {
    wizard_next(1, dict_wizard);
    if (appConfig.data_df !== null) {
        // Load input modal window
        $('#datasets_availables').val(appConfig.parameters[appConfig.m_name].dataset);
        update_split(appConfig.dataset_params.split.split(','));
        wizard_next(2, dict_wizard);
        table_feat_created = create_features_table(appConfig.data_df, appConfig.dataset_params.category_list, dict_wizard);
        table_target_created = create_target_table(appConfig.data_df, appConfig.dataset_params.category_list, appConfig.dataset_params.targets, dict_wizard)
        $('#normalize').prop('checked', appConfig.dataset_params.normalize);

        let input_nodes = cy.nodes().filter((node) => 'name' in node.data()).roots();
        input_nodes.forEach(node => {
            inputs_layers[node.data('name')] = {
                'dataset': appConfig.parameters[appConfig.m_name].dataset,
                'split': appConfig.dataset_params.split,
                'df': appConfig.data_df,
                'category_list': appConfig.dataset_params.category_list,
                'normalize': appConfig.dataset_params.normalize,
                'targets': appConfig.dataset_params.targets
            };
        });
    }
    $('#select_continue').click(function (e) {
        let dataset = $('#datasets_availables').find("option:selected").text();
        appConfig.dataset = dataset;
        wizard_next(2, dict_wizard);
        $.ajax({
            url: "/gui_select_data",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            accepts: {
                json: 'application/json',
            },
            data: JSON.stringify({
                'dataset': dataset,
            }),
            success: function (data) {
                if (data.data) {
                    update_split(data.data.split(','));
                    wizard_next(2, dict_wizard);
                }
            }
        });
    });

    $('#splitTabContinue').click(function (e) {
        let train = $('#range1').val();
        let val = $('#range2').val();
        let test = $('#range3').val();
        appConfig.dataset_params.split = train + ',' + val + ',' + test;
        $.ajax({
            url: "/gui_split",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            accepts: {
                json: 'application/json',
            },
            data: JSON.stringify({
                'train': train,
                'validation': val,
                'test': test,
            }),
            success: function (data) {
                table_feat_created = create_features_table(data.data, null, dict_wizard);
            }
        })
    });

    $('#featuresContinue').click(function (e) {
        let table = $('#table_features').DataTable();
        let cat_column = table.column('Category:name').data().map(b => $(b).val());
        let default_features = table.column('Features:name').data();
        let default_column = table.column('Defaults:name').data();
        appConfig.dataset_params.normalize = $('#normalize').is(":checked");
        $.ajax({
            url: "/gui_features",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            accepts: {
                json: 'application/json',
            },
            data: JSON.stringify({
                'default_featu': default_features.toArray(),
                'cat_column': cat_column.toArray(),
                'default_column': default_column.toArray(),
                'normalize': appConfig.dataset_params.normalize
            }),
            success: function (data) {
                appConfig.dataset_params.category_list = JSON.parse(data.data)['Category'];
                appConfig.data_df = data.data;
                table_target_created = create_target_table(data.data, null, null, dict_wizard);
            }
        });
    });

    $('#table_features').on('change', '.selfeat', function () {
        let td = $(this).parent('td');
        let cell = $('#table_features').DataTable().cell(td);
        let k = $(this);
        k.find(`option[value= ${$(cell.data()).val()}]`).attr('selected', false);
        k.find(`option[value= ${$(this).val()}]`).attr('selected', true);
        cell.data(k.prop('outerHTML'));
    });

    $('#targetContinue').click(function (e) {
        var targets = [];
        $('#table_targets').DataTable().rows({selected: true}).every(function () {
            targets.push(this.data()[0]);
        });
        if (targets.length > 0) {
            appConfig.dataset_params.targets = targets;
            $.ajax({
                url: "/gui_targets",
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                accepts: {
                    json: 'application/json',
                },
                data: JSON.stringify({
                    'targets': targets
                }),
                success: function (data) {
                    if (data.error === false) {
                        appConfig.num_outputs = data.num_outputs;
                        let input_shape = data.input_shape;
                        $('#input_shape').val(input_shape);
                        cy.$(':selected').data()['content']['input_shape']['value'] = input_shape;
                        inputs_layers[cy.$(':selected').data().name] = {
                            'dataset': appConfig.dataset,
                            'split': appConfig.dataset_params.split,
                            'df': appConfig.data_df,
                            'category_list': appConfig.dataset_params.category_list,
                            'normalize': appConfig.dataset_params.normalize,
                            'targets': appConfig.dataset_params.targets
                        };
                        clear_input_modal(dict_wizard);
                        close_modal();
                    } else
                        alert(data.error);
                }
            });
        } else
            alert('Select target!');
    });

    $("#submitform").submit(function (e) {
        let model_name = $('#inp').val();
        if (model_name === '') {
            e.preventDefault();
            alert('Model name can not be empty!');
            return false
        } else if (model_name in appConfig.parameters) {
            if (!confirm('This model name already exists do yo want to overwrite it?'))
                return false;
        }
        $('#modelname').val(model_name);

        let dnn = cy.nodes().filter((node) => ('DNN' === node.data().class_name)).length;
        $('#mode').val(dnn);
    });

});

function zoom(cy, level) {
    let zoom = cy.zoom();
    cy.zoom({level: zoom + level});
}

function center_layout(cy) {
    let layout = cy.layout({name: 'dagre'});
    layout.run();
    cy.maxZoom(1.2);
    cy.fit();
    cy.maxZoom(cy.maxZoom());
    cy.center();
}

function sort_nodes(cy) {
    let s = [];
    let explored = [];

    function dfs(node, explored, s) {
        explored.push(node);
        node.outgoers().forEach(n => {
            if (n.isNode() && explored.indexOf(n) < 0)
                dfs(n, explored, s);
        });
        s.push(node);
    }

    let input_nodes = cy.nodes().filter((node) => 'name' in node.data()).roots();
    input_nodes.forEach(node => {
        if (explored.indexOf(node) < 0)
            dfs(node, explored, s);
    });
    s.reverse().forEach(function (el, idx) {
        el.data()['depth'] = idx;
    });
    return cy.nodes().sort(function (a, b) {
        return a.data('depth') - b.data('depth');
    });
}


function send_canned(dnn_nodes, cy_json, loss) {
    $.ajax({
        url: "/save_canned",
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        accepts: {
            json: 'application/json',
        },
        data: JSON.stringify({
            'data': dnn_nodes.data().content,
            'cy_model': cy_json,
            'model_name': $('#inp').val(),
            'loss': loss
        }),
        success: function (result) {
        }
    });
}


async function tf_load_model(nodes, models, loss_function, cy_json, cy, loss_node) {
    let blob = new Blob([encode(JSON.stringify(models['tensorflowjs_json'], null, 4))], {
        type: 'application/octet-stream'
    });
    let url = URL.createObjectURL(blob);

    try {
        const model = await tf.loadModel(url);
        let topology = model.toJSON(null, false);
        let model_json = {"modelTopology": topology};
        create_poppers(model.layers, nodes, cy, loss_node);

        $.ajax({
            url: "/gui_editor",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            accepts: {
                json: 'application/json',
            },
            data: JSON.stringify({
                'loss_function': loss_function,
                'model': model_json,
                'cy_model': cy_json
            }),
            success: function (result) {
                if (result.explanation !== 'ok') {
                    alert(result.explanation);
                    disable_submit_button();
                    return false;
                }
                if (!(check_output(model.outputs[0].shape))) {
                    alert('Output shape is not valid. Should be : ' + appConfig.num_outputs);
                    disable_submit_button();
                    return false;
                }
                $('#submit').removeClass('hidden')
                    .prop('disabled', false);
                $('#validate_model').addClass('hidden');

            }
        });
    } catch (error) {
        alert(error);
        disable_submit_button();
        return false;
    }
}

function disable_submit_button() {
    $('#submit').addClass('hidden')
        .prop('disabled', true);
    let $validate_model = $('#validate_model');
    $validate_model
        .removeClass('hidden')
        .removeClass('btn-valid')
        .addClass('btn-secondary');
    $("div.popper-div").remove();
}

function check_output(model_shape) {
    return (model_shape[model_shape.length - 1] === appConfig.num_outputs);
}

function create_popper(cy, node, id, text) {
    var makeDiv = function (text, id) {
        let div = $('<div></div>').attr('id', id)
            .addClass('popper-div')
            .text('(' + text + ')')
            .appendTo('body');
        return div;
    };
    let popperA = node.popper({
        content: function () {
            return makeDiv(text, id);
        }
    });
    let updateA = function () {
        popperA.scheduleUpdate();
    };
    node.on('position', updateA);
    cy.on('pan zoom resize', updateA);
}

function create_poppers(layers, nodes, cy, loss_node) {
    $("div.popper-div").remove();
    let shapes = layers.map(function (layer) {
        if ('batchInputShape' in layer)
            return String(add_ba_size(layer.batchInputShape));
        if ('kernel' in layer)
            return String(add_ba_size(layer.kernel.shape));
        if ('outputShape' in layer)
            return String(add_ba_size(layer.outputShape));
        return ''
    });
    zip([shapes, nodes]).map(p => create_popper(cy, p[1], p[1].id(), p[0]));
    let last_shape = shapes[shapes.length - 1].split(',');
    create_popper(cy, loss_node, loss_node.id(), 'None,' + last_shape[last_shape.length - 1]);
}

function node_name_exists(cy, value) {
    let nodes_names = cy.nodes().map(function (node) {
        return String(node.data('name'))
    });
    return nodes_names.indexOf(value) >= 0
}

// TODO validate different types
function is_valid(type, value, id, cy) {
    if (id === 'name' && node_name_exists(cy, value)) {
        return false;
    } else if (type === 'integer_list') {
        let list_number = RegExp('^\[[0-9]+(,[0-9]+)*\]$');
        let only_number = new RegExp('^[0-9]+$');
        return list_number.test(value) || only_number.test(value) || value === null || value === ''
    }
    return true;
}

function append_after(label_name, config, id_item_before) {
    let $label = $("<label>").text(label_name);
    $label.attr("id", id_item_before.concat('-').concat(label_name));
    if (config['type'] === "select") {
        let selectList = $("<select>")
            .attr('id', id_item_before.concat('-').concat(label_name))
            .attr('name', label_name);

        let option_list = config['options'].map((key) => $('<option>').val(key).text(key));
        selectList.append(option_list);
        selectList.attr('value', config['value']);
        selectList.appendTo($label);
        $('#' + id_item_before).after(selectList)
            .after($label);
        return;
    }

    let x = $('<input>')
        .attr("id", id_item_before.concat('-').concat(label_name))
        .attr("name", label_name)
        .attr("value", config['value']);
    x.appendTo($label);

    if (config['type'] === "float") {
        x.attr("type", "number")
            .attr("step", "0.001");
        if ('min' in config)
            x.attr("min", config['min']);
        if ('max' in config)
            x.attr("max", config['max']);
    } else if (config['type'] === "integer") {
        x.attr("type", "number")
            .attr("step", "1");
    }

    $('#' + id_item_before).after(x)
        .after($label);
}