let selected_color = '#666666';
let white = '#ffffff';


let light_color1 = '#8a93ac';
let light_color2 = '#939eac';
let light_color3 = '#93a8b6';
let light_color4 = '#93a8c0';
let light_color5 = '#93a8ca';
let light_color6 = '#93a8a2';
let light_color7 = '#93a898';
let light_color8 = '#93a88e';
let light_color9 = '#e29a47';


//
// let light_color1 = '#69a6a8';
// let light_color2 = '#a58eac';
// let light_color3 = '#ac7687';
// let light_color4 = '#93a8c0';
// let light_color5 = '#93a8ca';
// let light_color6 = '#93a8a2';
// let light_color7 = '#b3caa7';
// let light_color8 = '#939eac';
// let light_color9 = '#e29a47';
//
//
//

let selected = '#019ebd';

var cyto_styles = [
    {
        selector: 'node',
        style: {
            'text-valign': 'center',
            'color': 'white',
            'width': 200,
            'height': 40,
            'shape': 'roundrectangle'
        }
    },
    // {
    //     selector: 'node:selected',
    //     style: {
    //         'border-width': 2,
    //         'border-color': selected_color
    //
    //     }
    // },
    {
        selector: "node[root = 'Input Layers']",
        style: {
            'background-color': light_color1,
        }
    },
    {
        selector: "node[root = 'Input Layers']:selected",
        style: {
            'background-color': selected,
        }
    },

    {
        selector: "node[root = 'Convolutional Layers']",
        style: {
            'background-color': light_color2,
        }
    },
    {
        selector: "node[root = 'Convolutional Layers']:selected",
        style: {
            'background-color': selected,
        }
    },
    {
        selector: "node[root = 'Merge Layers']",
        style: {
            'background-color': light_color3,
        }
    },
    {
        selector: "node[root = 'Merge Layers']:selected",
        style: {
            'background-color': selected,
        }
    },
    {
        selector: "node[root = 'Normalization Layers']",
        style: {
            'background-color': light_color4,
        }
    },

    {
        selector: "node[root = 'Normalization Layers']:selected",
        style: {
            'background-color': selected,
        }
    },
    {
        selector: "node[root = 'Pooling Layers']",
        style: {
            'background-color': light_color5,
        }
    },
    {
        selector: "node[root = 'Pooling Layers']:selected",
        style: {
            'background-color': selected,
        }
    },
    {
        selector: "node[root = 'Recurrent Layers']",
        style: {
            'background-color': light_color6,
        }
    },
    {
        selector: "node[root = 'Recurrent Layers']:selected",
        style: {
            'background-color': selected,
        }
    },

    {
        selector: "node[root = 'Advanced Activations Layers']",
        style: {
            'background-color': light_color7,
        }
    },
    {
        selector: "node[root = 'Advanced Activations Layers']:selected",
        style: {
            'background-color': selected,
        }
    },


    {
        selector: "node[root = 'Core Layers']",
        style: {
            'background-color': light_color8,
        }
    },
    {
        selector: "node[root = 'Core Layers']:selected",
        style: {
            'background-color': selected,
        }
    },

    {
        selector: "node[root = 'Loss Functions']",
        style: {
            'background-color': light_color3,
        }
    },
    {
        selector: "node[root = 'Loss Functions']:selected",
        style: {
            'background-color': selected,
        }
    },

    {
        selector: "node[root = 'Canned Models']",
        style: {
            'background-color': light_color9,

            'height': 90,
        }
    },
    {
        selector: "node[root = 'Canned Models']:selected",
        style: {
            'background-color': selected,
        }
    },

    {
        selector: 'edge',
        style: {
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle'
        }
    },
    {
        selector: '.eh-handle',
        style: {
            'background-color': selected_color,
            'width': 12,
            'height': 12,
            'shape': 'ellipse',
            'overlay-opacity': 0,
            'border-width': 12, // makes the handle easier to hit
            'border-opacity': 0
        }
    },
    {
        selector: '.eh-hover',
        style: {
            'background-color': selected_color
        }
    },
    {
        selector: '.eh-source',
        style: {
            'border-width': 2,
            'border-color': selected_color
        }
    },
    {
        selector: '.eh-target',
        style: {
            'border-width': 2,
            'border-color': selected_color
        }
    },
    {
        selector: '.eh-preview, .eh-ghost-edge',
        style: {
            'background-color': selected_color,
            'line-color': selected_color,
            'target-arrow-color': selected_color,
            'source-arrow-color': selected_color
        }
    },
    {
        selector: '.eh-ghost-edge .eh-preview-active',
        style: {
            'opacity': 0
        }
    },
    {
        selector: ':parent',
        style: {
            'background-opacity': 0.333,
            "background-color": '#e29a47',
             'border-width': 2,
            'border-color': selected_color,
            // 'z-index': 999999
        }
    },

    {
        selector: "node.cy-expand-collapse-collapsed-node",
        style: {
            "background-color": '#e29a47',
            'height': 90
        }
    }
];