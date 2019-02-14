var counters = {};
var cy;
var table_feat_created = false;
var table_target_created = false;
var inputs_layers = {};
var mode, loaded_input;
Array.prototype.contains = function (element) {
    return this.indexOf(element) > -1;
};

document.addEventListener('DOMContentLoaded', function () {
    $('#inp').val(appConfig.m_name);
    $('#submit').prop('disabled', true);
    create_layers(corelayers);

    cy = cytoscape({
        container: document.getElementById('cy'),
        elements: appConfig.cy_model.elements,
        style: cyto_styles
    });
    var expandCollapse_defaults = {
        layoutBy: null,
        fisheye: false,
        animate: false,
        ready: function () {
        },
        undoable: true, // and if undoRedoExtension exists,
        cueEnabled: true, // Whether cues are enabled
        expandCollapseCuePosition: 'top-left', // default cue position is top left you can specify a function per node too
        expandCollapseCueSize: 18, // size of expand-collapse cue
        expandCollapseCueLineSize: 1, // size of lines used for drawing plus-minus icons
        expandCueImage: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAb1BMVEUAAABxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXEyJiWEAAAAJHRSTlMAAgMEBQgODxIdIygwMTs/QEZKVWJokZSVq7TDzNze5Obz9/th0slBAAAAkUlEQVQoz83SywJCUBhF4YXklmsohGi//zM2aKLT0diafqOz/wPgxFnxXZ4GfCoXWep8gEb2nj5EUh9i5pUvddBqdLBUSgGzapvhSSlSYUWk/B8WB8WHuV2ywZ9h8w0m5slOR37nHq6q9jBj0M1qoRRzlS4Wc3otDu4k3StjoaIepRI4T/Z/2wDgXofVlLmNgDdGVyVbqNQxVwAAAABJRU5ErkJggg==', // image of expand icon if undefined draw regular expand cue
        collapseCueImage: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAb1BMVEUAAABxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXFxcXEyJiWEAAAAJHRSTlMAAgMEBQgODxIdIygwMTs/QEZKVWJokZSVq7TDzNze5Obz9/th0slBAAAApklEQVQokc3SSRLCMAwF0Q4zBLDDEOa5739GFlAhCWbP31mvtLAkgGwyj82E2ZBXipuJ7PoA6xSp1z6MdT+inW7xcAelp+zLgEKHXFxVhV7IP706Q2NVCPpp1dDA2MT4p3hszy6v4ddgQw3z16ZKfa+s98///IV3F9U791jHOQc3pDLSCUudJizbe8vonHW7aB11XJ20AAbn9N2uAegsD/e2XMox8AQnVCppI6CYIwAAAABJRU5ErkJggg==', // image of collapse icon if undefined draw regular collapse cue
        expandCollapseCueSensitivity: 2 // sensitivity of expand-collapse cues
    };
    cy.expandCollapse(expandCollapse_defaults);
    let api = cy.expandCollapse('get');
    let collapsed = [];


    add_icons_nodes();

    //Update counters (nodes names)
    cy.nodes().forEach(function (node) {
        counters[node.data().name.split('_')[0]] = parseInt(node.data().name.split('_')[1]);
    });
    counters['block'] = 0;


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
                    if (inputs_layers.hasOwnProperty(target.data().name)) {
                        delete inputs_layers[target.data().name];
                        reset_wizard();
                    }

                    target.remove();
                    $('#' + target.id()).remove();
                    disable_submit_button();
                    clean_blocks();
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
            },
            {
                id: 'group-nodes',
                content: 'group nodes',
                tooltipText: 'group selected nodes',
                selector: 'node',
                coreAsWell: true,
                disabled: false,
                onClickFunction: function (event) {
                    group_selected_nodes(event);
                    disable_submit_button();
                    add_icons_nodes();

                }
            },
            {
                id: 'ungroup-nodes',
                content: 'ungroup nodes',
                tooltipText: 'ungroup selected nodes',
                selector: 'node',
                coreAsWell: true,
                disabled: false,
                onClickFunction: function (event) {
                    let target = event.target || event.cyTarget;
                    target.children().forEach(function (c) {
                        c.move({'parent': null});
                    });
                    target.remove();
                    disable_submit_button();
                    add_icons_nodes();


                }
            }
        ]
    };
    let instances = cy.contextMenus(options);
    instances.hideMenuItem('group-nodes');
    instances.hideMenuItem('ungroup-nodes');

    let eh = cy.edgehandles({snap: true});
    let ur = cy.undoRedo({undoableDrag: false});
    cy.clipboard();

    function deleteEles(eles) {
        return eles.remove();
    }

    function restoreEles(eles) {
        return eles.restore();
    }

    ur.action("deleteEles", deleteEles, restoreEles);


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
                if (node.length > 0) {
                    if (inputs_layers.hasOwnProperty(node.data().name)) {
                        delete inputs_layers[node.data().name];
                        reset_wizard();
                    }

                    $('#' + node.id()).remove();
                    disable_submit_button();
                }
                ur.do("deleteEles", cy.$(":selected"));
                clean_blocks();
            }


        }
    });
    document.addEventListener("click", function (e) {
        let selected = cy.nodes().filter((node) => (node.selected()));
        instances.hideMenuItem('ungroup-nodes');
        if (selected.length > 1) {
            instances.showMenuItem('group-nodes');
        } else {
            instances.hideMenuItem('group-nodes');
            if (selected.length === 1 && selected[0].data().class_name === 'block') {
                instances.showMenuItem('ungroup-nodes');
            }

        }

    });


    cy.on('doubleTap', 'node', function (event) {
        if (event.target.data().class_name.includes('InputLayer')) {

            $('#modal').removeClass('fade');

            disable_submit_button();
            if (inputs_layers.hasOwnProperty(event.target.data().name) && inputs_layers[event.target.data().name].is_saved) {
                let name = event.target.data().name;

                $('#table_datasets').DataTable().rows().every(function () {
                    var data = this.data()[0];
                    if (inputs_layers[name].dataset === data) {
                        this.select();
                        $("#select_continue").prop('disabled', false);
                    }

                });
                wizard_next(2, dict_wizard);

                update_split(inputs_layers[name].split.split(','));

                if (inputs_layers[name].hasOwnProperty('df')) {
                    wizard_next(3, dict_wizard);
                    table_feat_created = create_features_table(inputs_layers[name]['df'], inputs_layers[name]['category_list'], dict_wizard);
                    table_target_created = create_target_table(inputs_layers[name]['df'], inputs_layers[name]['category_list'], inputs_layers[name]['targets'], dict_wizard);
                    $('#normalize').prop('checked', inputs_layers[name]['normalize']);
                } else {
                    restore_features_images(inputs_layers[name]['height'], inputs_layers[name]['width'], inputs_layers[name]['normalization'], inputs_layers[name]['augmentation_options'], inputs_layers[name]['augmentation_params']);
                    create_images_targets(inputs_layers[name]['image_data']);
                }
            } else {
                reset_wizard();
            }
            $('#modal').show();
        }
    });

    var tappedBefore;
    var tappedTimeout;
    $('#close').on('click', function () {
        clear_input_modal(dict_wizard, true);
        close_modal();
        let input_node = cy.$(':selected').data().name;
        if (inputs_layers.hasOwnProperty(input_node) && !inputs_layers[input_node].is_saved) {
            reset_wizard();
            delete inputs_layers[input_node];

        }

    });
    $('#table_datasets tbody').on('click', 'tr', function (e) {
        clear_input_modal(dict_wizard, false);
        reset_wizard();
        let input_node = cy.$(':selected').data().name;
        if (inputs_layers.hasOwnProperty(input_node) && !inputs_layers[input_node].is_saved) {
            delete inputs_layers[input_node];
        }
        let table_datasets = $('#table_datasets').DataTable();
        if (table_datasets.row(this, {selected: true}).any())
            $('#select_continue').prop('disabled', true);
        else if (table_datasets.page.info().recordsDisplay === 0) {
            $('#select_continue').prop('disabled', true);
        }
        else $("#select_continue").prop('disabled', false);

    });

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
        if (targetNode.data().root === 'Input Layers') {
            addedEles.remove();
        } else if (targetNode.indegree() > 1 && !(targetNode.data().root === 'Merge Layers')) {
            addedEles.remove();
        } else if (sourceNode.data().root === 'Loss Functions') {
            addedEles.remove();
        } else if (targetNode.data().class_name === 'block' || sourceNode.data().class_name === 'block') {
            addedEles.remove();
        }
        disable_submit_button();
    });
    cy.on('drag', 'node', function (e) {
        add_icons_nodes();

    });
    cy.on('expandcollapse', function (e) {
        add_icons_nodes();
    });
    cy.on('expandcollapse.beforecollapse', function (e) {
        e.target.children().filter((n) => (n.isNode())).forEach(function (n) {
            var div = document.getElementById(n.id());
            if (div) {
                div.style.display = "none";
            }

        });
    });
    cy.on('expandcollapse.afterexpand', function (e) {
        e.target.children().filter((n) => (n.isNode())).forEach(function (n) {
            var div = document.getElementById(n.id());
            if (div) {
                div.style.display = "block";
            }

        });
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

    function group_selected_nodes(event) {
        let nodes = cy.nodes().filter((node) => (node.selected()));
        var content = {}
        content['name'] = {'type': 'text'};
        content['name']['value'] = "block_" + counters['block'].toString();
        let grp = cy.add({
            data: {
                name: "block_" + counters['block'].toString(),
                class_name: 'block',
                root: 'block',
                content: content

            }
        });
        counters['block'] += 1;

        //create parent node
        nodes.forEach(function (node) {
            node.move({parent: grp.data().id});
        });
        clean_blocks();


    }


    function clean_blocks() {
        let blocks = cy.nodes().filter((node) => (node.data().class_name === 'block' && node.children().length === 1));
        blocks.forEach(function (n) {
            n.children().forEach(function (c) {
                c.move({'parent': null});
            });
        });
        cy.remove(blocks);
    }


    function add_new_node(event) {
        let radio_checked = document.querySelector('input[name="radio"]:checked');
        if (radio_checked) {

            // ONE INPUT LAYER ALLOW
            if (radio_checked.id === 'InputLayer') {
                let exists = false;
                let c = cy.filter(function (element, i) {
                    if (element.isNode() && element.data().class_name === 'InputLayer') {
                        alert('Input layer already exists');
                        exists = true;
                    }
                });
                if (exists)
                    return false;
            }


            let id_checked = document.querySelector('input[name="radio"]:checked').id;
            let root = Object.keys(corelayers).find(key => id_checked in corelayers[key]);
            Object.keys(corelayers).forEach(function (key) {
                let content = $.extend(true, {}, corelayers[key][id_checked]);
                if (id_checked in corelayers[key]) {
                    if (id_checked === 'InputLayer' && 'input_shape' in content) {
                        content['input_shape']['value'] = appConfig.input_shape;
                    }
                    if (id_checked === 'DNN' && appConfig.hasOwnProperty('hidden_layers')) {
                        content['hidden_layers']['value'] = '[' + appConfig.hidden_layers + ']';
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
        zoom(cy, -0.000001);
    }


    $('#validate_model').on('click', async function (event) {
        validate_save_model(cy, event, api, false);
    });

    $('#save_model').on('click', async function (event) {
        validate_save_model(cy, event, api, true);
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

    loaded_input = cy.filter(function (element, i) {
        if (element.isNode() && 'name' in element.data())
            if (element.data().class_name.includes('InputLayer') && element.data().content.input_shape.value !== undefined)
                return element.data('name');
        return false;
    });
    load_model_input();

});

function check_input_output(cy) {
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

    let canned_nodes = cy.nodes().filter((node) => (node.data().class_name in corelayers["Canned Models"]));
    let all = cy.nodes().filter((node) => ('class_name' in node.data()));

    if (canned_nodes.length === 1 && all.length > 3)
        return 'If you use a canned model it is not posible use another layer (besides input and loss)';
    return true;
}

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


    $('#select_continue').click(function (e) {
        $('#table_datasets').DataTable().rows({selected: true}).every(function () {
            appConfig.dataset = this.data()[0];
        });


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
                'dataset': appConfig.dataset,
            }),
            success: function (data) {
                let input_node = cy.nodes().filter((node) => 'name' in node.data()).roots()[0];
                inputs_layers[input_node.data('name')] = {'dataset': appConfig.dataset, 'is_saved': false};
                if (data.data.hasOwnProperty('height')) {
                    create_image_feature(data.data, dict_wizard);
                    mode = 'image'
                } else {
                    table_feat_created = create_features_table(data.data, null, dict_wizard);
                    mode = 'tabular';
                    inputs_layers[input_node.data('name')]['df'] = data.data;
                }

                appConfig['data_df'] = data.data;
            }
        });
    });

    $('#splitTabContinue').click(function (e) {

        let train = $('#range1').val();
        let val = $('#range2').val();
        let test = $('#range3').val();
        appConfig.dataset_params.split = train + ',' + val + ',' + test;
        let input_node = cy.nodes().filter((node) => node.data().class_name === 'InputLayer')[0];

        inputs_layers[input_node.data('name')]['split'] = appConfig.dataset_params.split;
        inputs_layers[input_node.data('name')]['train'] = train;
        inputs_layers[input_node.data('name')]['test'] = test;
        inputs_layers[input_node.data('name')]['validation'] = val;

        wizard_next(3, dict_wizard);
    });

    $('#featuresContinue').click(function (e) {

        if (mode === 'tabular') {
            tabular_features_continue();
        } else {
            image_features_continue();
        }

    });

    $('#table_features').on('change', '.selfeat', function () {
        let td = $(this).parent('td');
        let cell = $('#table_features').DataTable().cell(td);
        let k = $(this);
        k.find(`
    option[value = ${$(cell.data()).val()}]`).attr('selected', false);
        k.find(`
    option[value = ${$(this).val()}]`).attr('selected', true);
        cell.data(k.prop('outerHTML'));
    });

    $('#targetContinue').click(function (e) {
        if ($('#tabular_target').attr('hidden')) {
            inputs_layers[cy.$(':selected').data().name]['is_saved'] = true;
            close_modal();
            return true;
        }
        var targets = [];
        $('#table_targets').DataTable().rows({selected: true}).every(function () {
            targets.push(this.data()[0]);
        });
        if (targets.length > 0) {
            appConfig.dataset_params.targets = targets;
            inputs_layers[cy.$(':selected').data().name]['targets'] = appConfig.dataset_params.targets;
            let args = {};
            Object.keys(inputs_layers[cy.$(':selected').data().name]).forEach(function (k) {
                args[k] = inputs_layers[cy.$(':selected').data().name][k];
                if (['default_featu', 'cat_column', 'default_column'].contains(k))
                    args[k] = args[k].toArray();
            });
            $.ajax({
                url: "/gui_input",
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                accepts: {
                    json: 'application/json',
                },
                data: JSON.stringify(args),
                success: function (data) {
                    if (data.error === false) {
                        appConfig.num_outputs = data.num_outputs;
                        appConfig.hidden_layers = data.hidden_layers;
                        let input_shape = data.input_shape;
                        $('#input_shape').val(input_shape);
                        cy.$(':selected').data()['content']['input_shape']['value'] = input_shape;
                        inputs_layers[cy.$(':selected').data().name]['targets'] = appConfig.dataset_params.targets;

                        inputs_layers[cy.$(':selected').data().name]['is_saved'] = true;
                        close_modal();
                    } else {
                        alert(data.error);
                    }

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

        let canned_nodes = cy.nodes().filter((node) => (node.data().class_name in corelayers["Canned Models"]));
        $('#mode').val(canned_nodes.length);
    });

    function tabular_features_continue() {
        $('#image_target').attr('hidden', '');
        $('#tabular_target').removeAttr('hidden');
        let table = $('#table_features').DataTable();
        let cat_column = table.column('Category:name').data().map(b => $(b).val());
        let default_features = table.column('Features:name').data();
        let default_column = table.column('Defaults:name').data();

        appConfig.dataset_params.normalize = $('#normalize').is(":checked");

        let targets = null;
        if (appConfig.dataset_params !== null && appConfig.dataset_params.hasOwnProperty('targets'))
            targets = appConfig.dataset_params.targets;

        let cat_dict = {};
        table.rows().every(function () {
            cat_dict[this.data()[0]] = $(this.data()[1]).val();
        });

        table_target_created = create_target_table(appConfig.data_df, cat_dict, targets, dict_wizard);

        let input_node = cy.nodes().filter((node) => node.data().class_name === 'InputLayer')[0];
        inputs_layers[input_node.data('name')]['cat_column'] = cat_column;
        inputs_layers[input_node.data('name')]['category_list'] = cat_dict;
        inputs_layers[input_node.data('name')]['normalize'] = appConfig.dataset_params.normalize;
        inputs_layers[input_node.data('name')]['default_featu'] = default_features;
        inputs_layers[input_node.data('name')]['default_column'] = default_column;

    }

    function image_features_continue() {
        $('#image_target').removeAttr('hidden');
        $('#tabular_target').attr('hidden', '');
        let augmentation_options = [];
        let params = {};

        $.each($('#list2 a'), function (a, b) {
            if (b.id !== "")
                augmentation_options.push(b.id);
        });
        $('#list2 input[type="number"]').each(function () {
            let id_input = $(this)[0].id;
            if ($('#' + id_input).val() !== '')
                params[id_input] = $('#' + id_input).val();
            else {
                alert('Missing parameter value');
                throw 'Missing parameter value';
            }


        });
        $('#list2 input:checkbox, #list2 input[type="radio"]').each(function () {
            let id_input = $(this)[0].id;
            if (id_input !== '')
                params[id_input] = $('#' + id_input).is(":checked");
        });

        data = appConfig.data_df;

        let input_shape = "[" + $('#height').val() + ',' + $('#width').val() + ',' + data['n_channels'] + ']';
        $('#input_shape').val(input_shape);
        appConfig.num_outputs = data['num_outputs'];
        cy.$(':selected').data()['content']['input_shape']['value'] = input_shape;
        inputs_layers[cy.$(':selected').data().name]['normalization'] = $('#normalization').val();
        inputs_layers[cy.$(':selected').data().name]['augmentation_options'] = augmentation_options;
        inputs_layers[cy.$(':selected').data().name]['augmentation_params'] = params;
        inputs_layers[cy.$(':selected').data().name]['image_data'] = data.data;
        inputs_layers[cy.$(':selected').data().name]['height'] = $('#height').val();
        inputs_layers[cy.$(':selected').data().name]['width'] = $('#width').val();
        delete data['n_channels'];
        delete data['num_outputs'];
        create_images_targets(data.data);

    }
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

function sort_nodes(nodes) {
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

    let input_nodes = nodes.filter((node) => 'name' in node.data()).roots();
    input_nodes.forEach(node => {
        if (explored.indexOf(node) < 0)
            dfs(node, explored, s);
    });
    s.reverse().forEach(function (el, idx) {
        el.data()['depth'] = idx;
    });
    return nodes.sort(function (a, b) {
        return a.data('depth') - b.data('depth');
    });
}


function send_canned(cy, dnn_nodes, cy_json, loss) {
    let input_node = cy.nodes().filter((node) => node.data().class_name === 'InputLayer')[0];
    inputs_layers[input_node.data('name')]['targets'] = appConfig.dataset_params.targets;

    let args = {};
    Object.keys(inputs_layers[input_node.data('name')]).forEach(function (k) {
        args[k] = inputs_layers[input_node.data('name')][k];
        if (['default_featu', 'cat_column', 'default_column'].contains(k))
            args[k] = args[k].toArray();
    });
    args['loss'] = loss;
    args['cy_model'] = cy_json;
    args['mode'] = 'canned';
    args['model_name'] = $('#inp').val();
    args['data'] = dnn_nodes.data().content;

    $.ajax({
        url: "/save_model",
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        accepts: {
            json: 'application/json',
        },
        data: JSON.stringify(args),
        success: function (result) {
            $.notify("New model saved", "success");

        }
    });
}

async function validate_save_model(cy, event, api, save_model) {
    cy.remove(cy.nodes().filter((node) => (!('name' in node.data()))));
    let mess = check_input_output(cy);
    if (mess !== true) {
        alert(mess);
        disable_submit_button();
        return false;

    } else {
        let canned_nodes = cy.nodes().filter((node) => (node.data().class_name in corelayers["Canned Models"]));
        let canned_length = canned_nodes.length;
        if (canned_length === 1) {
            let input_canned = cy.filter(function (element, i) {
                if (element.isNode() && 'name' in element.data())
                    if (element.data().class_name.includes('InputLayer') && element.data().content.input_shape.value !== undefined)
                        return element.data();
                return false;
            });
            let is_image = input_canned.data().content.input_shape.value.split(',').length === 3;
            if (!is_image) {
                var loss = canned_nodes.successors().filter((node) => (node.data().hasOwnProperty('class_name') && node.data()['class_name'] === 'Loss')).data().content.function.value;
                $('#submit').removeAttr('hidden')
                    .prop('disabled', false);
                $('#validate_model').attr('hidden', '');
                if (save_model)
                    send_canned(cy, canned_nodes, cy.json(), loss);

            } else {
                alert('Canned Models can not be use with Image Input');
            }


        } else if (canned_length === 0) {
            let enodes = api.expandableNodes();
            api.expandAll();

            let loss_node = cy.nodes().filter((node) => (node.data('name').includes('Loss')));
            let edges = loss_node.connectedEdges();
            let loss_function = loss_node.data('content')['function'].value;

            cy.remove(loss_node);

            try {
                let nodes = cy.nodes().filter((node) => (node.data().class_name !== 'block'));
                let models = create_json_model(sort_nodes(nodes));

                cy.add(loss_node);
                cy.add(edges);

                await tf_load_model(sort_nodes(nodes), models, loss_function, cy.json(), cy, loss_node, save_model);
                api.collapse(enodes);

            } catch (e) {
                cy.add(loss_node);
                cy.add(edges);
                api.collapse(enodes);
            }
            event.preventDefault();
        }
        else {
            alert("Just one Canned Model allowed");
            disable_submit_button();
            return false;
        }
    }

}


async function tf_load_model(nodes, models, loss_function, cy_json, cy, loss_node, save_model) {
    let blob = new Blob([encode(JSON.stringify(models['tensorflowjs_json'], null, 4))], {
        type: 'application/octet-stream'
    });
    let url = URL.createObjectURL(blob);

    try {
        const model = await tf.loadModel(url);
        let topology = model.toJSON(null, false);
        let model_json = {"modelTopology": topology};
        create_poppers(model.layers, nodes, cy, loss_node);

        let check_out = check_output(model.outputs[0].shape);
        if (!(check_out['val'])) {
            alert(check_out['mess']);
            disable_submit_button();
            return false;
        }

        if (save_model) {
            let input_node = cy.nodes().filter((node) => node.data().class_name === 'InputLayer')[0];
            inputs_layers[input_node.data('name')]['targets'] = appConfig.dataset_params.targets;
            let args = {};
            Object.keys(inputs_layers[input_node.data('name')]).forEach(function (k) {
                args[k] = inputs_layers[input_node.data('name')][k];
                if (['default_featu', 'cat_column', 'default_column'].contains(k))
                    args[k] = args[k].toArray();
            });
            args['loss_function'] = loss_function;
            args['model'] = model_json;
            args['cy_model'] = cy_json;
            args['mode'] = 'custom';
            args['model_name'] = $('#inp').val();


            $.ajax({
                url: "/save_model",
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                accepts: {
                    json: 'application/json',
                },
                data: JSON.stringify(args),
                success: function (result) {
                    if (result.explanation !== 'ok') {
                        alert(result.explanation);
                        disable_submit_button();
                        return false;
                    }
                    $.notify("New model saved", "success");

                }

            });
        }

        $('#submit').removeAttr('hidden')
            .prop('disabled', false);
        $('#validate_model').attr('hidden', '');

    } catch (error) {
        alert(error);
        disable_submit_button();
        return false;
    }
}

function disable_submit_button() {
    $('#submit').attr('hidden', '');

    $('#submit').prop('disabled', true);
    let $validate_model = $('#validate_model');
    $validate_model
        .removeAttr('hidden')
        .removeClass('btn-valid')
        .addClass('btn-secondary');
    $("div.popper-div").remove();
}

function check_output(model_shape) {
    let result = {};
    if (model_shape.length < 3) {
        result ['val'] = model_shape[model_shape.length - 1] === appConfig.num_outputs;
        result['mess'] = 'Output shape is not valid. Should be : ' + appConfig.num_outputs;
    } else {
        result ['val'] = false;
        result['mess'] = 'Output shape should have rank 2';
    }
    return result;
}

function create_popper(cy, node, id, text) {
    let makeDiv = function (text, id) {
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

function load_model_input() {
    $("#normalization").change(function () {
        $("#normalization option:selected").each(function () {
            $("#normalization_explain").html(this.title);
        });
    });


    wizard_next(1, dict_wizard);

    // Load model -> modal window
    if (appConfig.data_df !== null) {
        update_split(appConfig.dataset_params.split.split(','));
        wizard_next(2, dict_wizard);
        if ('category_list' in appConfig.dataset_params) {
            wizard_next(3, dict_wizard);

            table_feat_created = create_features_table(appConfig.data_df, appConfig.dataset_params.category_list, dict_wizard);
            table_target_created = create_target_table(appConfig.data_df, appConfig.dataset_params.category_list, appConfig.dataset_params.targets, dict_wizard);
            $('#normalize').prop('checked', appConfig.dataset_params.normalize);
            let table = $('#table_features').DataTable();
            let cat_column = table.column('Category:name').data().map(b => $(b).val());
            let default_features = table.column('Features:name').data();
            let default_column = table.column('Defaults:name').data();

            let input_nodes = cy.nodes().filter((node) => node.data().class_name === 'InputLayer');
            input_nodes.forEach(node => {
                let split = appConfig.dataset_params.split.split(',');
                inputs_layers[node.data('name')] = {
                    'dataset': appConfig.parameters[appConfig.m_name].dataset,
                    'split': appConfig.dataset_params.split,
                    'train': split[0],
                    'validation': split[1],
                    'test': split[2],
                    'df': appConfig.data_df,
                    'category_list': appConfig.dataset_params.category_list,
                    'normalize': appConfig.dataset_params.normalize,
                    'targets': appConfig.dataset_params.targets,
                    'default_featu': default_features,
                    'default_column': default_column,
                    'cat_column': cat_column,
                    'is_saved': true
                };
            });
        } else {
            create_image_feature(appConfig.data_df, dict_wizard);
            restore_features_images(appConfig.dataset_params.height, appConfig.dataset_params.width, appConfig.dataset_params.normalization, appConfig.dataset_params.augmentation_options, appConfig.dataset_params.augmentation_params);
            create_images_targets(appConfig.data_df.data);
            // Supposed one input
            let split = appConfig.dataset_params.split.split(',');
            inputs_layers[loaded_input.data().name] = {
                'dataset': appConfig.dataset_params.name,
                'split': appConfig.dataset_params.split,
                'train': split[0],
                'validation': split[1],
                'test': split[2],
                'height': appConfig.dataset_params.height,
                'width': appConfig.dataset_params.width,
                'normalization': appConfig.dataset_params.normalization,
                'augmentation_options': appConfig.dataset_params.augmentation_options,
                'augmentation_params': appConfig.dataset_params.augmentation_params,
                'image_data': appConfig.data_df.data,
                'is_saved': true
            };
        }
        $('#validate_model').click();

    }
}
