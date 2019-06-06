var fa_corelayers = {
    'Advanced Activations Layers': 'fas fa-signature',
    'Convolutional Layers': 'fas fa-th',
    'Core Layers': 'fas fa-sitemap',
    'Input Layers': 'fas fa-arrow-right',
    'Merge Layers': 'fas fa-bezier-curve',
    'Normalization Layers': 'fas fa-chart-bar',
    'Pooling Layers': 'fas fa-th-large',
    'Recurrent Layers': 'fas fa-server',
    'Loss Functions': 'fas fa-arrow-left',
    'Canned Models': 'fas fa-layer-group',
    'block': 'fas fa-box'
};

var initializers = {
    'constant': {
        "value": {"type": "float", "value": 0},
    },
    "identity": {
        "gain": {"type": "float", "value": 1}
    },
    "orthogonal": {
        "gain": {"type": "float", "value": 1}
    },
    "randomNormal": {
        "mean": {"type": "float", "value": 0},
        "stddev": {"type": "float", "value": 1}
    },
    "randomUniform": {
        "minval": {"type": "float", "value": 0},
        "maxval": {"type": "float", "value": 1}
    },
    "truncatedNormal": {
        "mean": {"type": "float", "value": 0},
        "stddev": {"type": "float", "value": 1}
    },
    "varianceScaling": {
        "scale": {"type": "float", "value": 1},
        "mode": {"type": "select", "value": 'fanIn', "options": ["fan_in", "fan_out", "fan_avg"]},
        "distribution": {"type": "select", "value": 'normal', "options": ['normal', 'uniform']}
    },

};

var regularizers = {
    "L1L2": {
        "l1": {"type": "float", "value": 0},
        "l2": {"type": "float", "value": 0}
    }
};

var constraints = {
    "maxNorm": {
        "maxValue": {"type": "float", "value": 2},
        "axis": {"type": "integer", "value": 0}
    },
    "minMaxNorm": {
        "maxValue": {"type": "float", "value": 1},
        "minValue": {"type": "float", "value": 0},
        "axis": {"type": "integer", "value": 0},
        "rate": {"type": "float", "value": 1, "min": 0, "max": 1}
    },
    "unitNorm": {
        "axis": {"type": "integer", "value": 0}
    },
};

var corelayers = {
    "Input Layers": {
        "InputLayer": {
            "input_shape": {"type": "integer_list", "value": "[1,100]"},
            "dtype": {
                "type": "select",
                "options": ["float32", "float64", "int32"],
                "value": "float32"
            },
            "sparse": {"type": "boolean", "value": false},
            "class_name": "InputLayer"
        },
    },

    "Core Layers": {
        "Activation": {
            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh"],
                "value": "relu"
            }, "class_name": "Activation"
        },


        "Dense": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "trainable": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },

            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            //"activity_regularizer": {"type": "select", "options": [null,  "L1L2"], "value": null},
            "class_name": "Dense"
        },

        "Dropout": {
            "rate": {"type": "float", "value": 0, "min": 0, "max": 1},
            "noise_shape": {"type": "integer_list", "value": null},
            // "seed": {"type": "integer", "value": null, "min": 0}, TODO
            "class_name": "Dropout"
        },


        "Embedding": {
            "input_dim": {"type": "integer", "value": 1, "min": 1},
            "output_dim": {"type": "integer", "value": 1, "min": 0},
            "embeddings_initializer": {
                "type": "select",
                "options": [null, "glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": null
            },
            "embeddings_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            //"activity_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "embeddings_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "mask_zero": {"type": "boolean", "value": false},
            "inputLength": {"type": "integer_list", "value": null},
            "class_name": "Embedding"
        },

        "Flatten": {
            "input_shape": {"type": "integer_list", "value": null},
            "batchInputShape": {"type": "integer_list", "value": null},
            "batchSize": {"type": "integer", "value": null, "min": 0},
            "dtype": {
                "type": "select",
                "options": ["float32", "int32", "bool"],
                "value": "float32"
            },
            "trainable": {"type": "boolean", "value": false},
            "updatable": {"type": "boolean", "value": false},
            "inputDType": {
                "type": "select",
                "options": ["float32", "int32", "bool"],
                "value": "float32"
            },
            "class_name": "Flatten"
        },

        "RepeatVector": {
            "n": {"type": "integer", "value": 1, "min": 0},
            "class_name": "RepeatVector"
        },
        "Permute": {
            "dims": {"type": "integer_list", "value": null},
            "class_name": "Permute"
        },
        "Reshape": {
            "targetShape": {"type": "integer_list", "value": null},
            "class_name": "Reshape"
        }
    },


    "Convolutional Layers": {

        "Conv1D": {
            "kernel_size": {"type": "integer_list", "value": null},
            "filters": {"type": "integer", "value": 1, "min": 1},
            "strides": {"type": "integer_list", "value": null},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "dataFormat": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilationRate": {"type": "integer_list", "value": null},

            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            //"activity_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "class_name": "Conv1D"
        },

        "Conv2D": {
            "kernel_size": {"type": "integer_list", "value": null},
            "filters": {"type": "integer", "value": 1, "min": 1},
            "strides": {"type": "integer_list", "value": null},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "dataFormat": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilationRate": {"type": "integer_list", "value": null},

            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            //"activity_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "class_name": "Conv2D"
        },


        "Conv2DTranspose": {
            "kernel_size": {"type": "integer_list", "value": null},
            "filters": {"type": "integer", "value": 1, "min": 1},
            "strides": {"type": "integer_list", "value": null},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "dataFormat": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilationRate": {"type": "integer_list", "value": null},

            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            //"activity_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "class_name": "Conv2DTranspose"
        },
        "Conv3D": {
            "kernel_size": {"type": "integer_list", "value": null},
            "filters": {"type": "integer", "value": 1, "min": 1},
            "strides": {"type": "integer_list", "value": null},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "dataFormat": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilationRate": {"type": "integer_list", "value": null},

            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            //"activity_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "class_name": "Conv3D"
        },


        "DepthwiseConv2D": {
            "kernel_size": {"type": "integer_list", "value": null},
            "filters": {"type": "integer", "value": 1, "min": 1},
            "strides": {"type": "integer_list", "value": null},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "dataFormat": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilationRate": {"type": "integer_list", "value": null},

            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            //"activity_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "class_name": "DepthwiseConv2D"
        },
        "Cropping2D": {
            "axes": {"type": "integer_list", "value": "[0]"},
            "dataFormat": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},

            "class_name": "Cropping2D"
        },
        "SeparableConv2D": {
            "kernel_size": {"type": "integer_list", "value": null},
            "filters": {"type": "integer", "value": 1, "min": 1},
            "strides": {"type": "integer_list", "value": null},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "dataFormat": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilationRate": {"type": "integer_list", "value": null},
            "depth_multiplier": {"type": "integer", "value": 1, "min": 1},

            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "depthwise_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "depthwise_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            //"activity_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "depthwise_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "pointwise_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },

            "pointwise_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},

            "pointwise_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "class_name": "SeparableConv2D"
        },
         "UpSampling2D": {
            "size": {"type": "integer_list", "value": "[2,2]"},
            "dataFormat": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
             "interpolation": {"type": "select", "options": ["nearest", "bilinear"], "value": "nearest"},

            "class_name": "UpSampling2D"
        },


    },


    "Merge Layers": {
        "Add": {
            "dtype": {
                "type": "select",
                "options": ["float32", "int32", "bool"],
                "value": "float32"
            },
            "trainable": {"type": "boolean", "value": false},
            "updatable": {"type": "boolean", "value": false},

            "class_name": "Add"
        },

        "Average": {
            "dtype": {
                "type": "select",
                "options": ["float32", "int32", "bool"],
                "value": "float32"
            },
            "trainable": {"type": "boolean", "value": false},
            "updatable": {"type": "boolean", "value": false},

            "class_name": "Average"
        },

        "Concatenate": {
            "axis": {"type": "integer", "value": -1},
            "class_name": "Concatenate"
        },


        "Maximum": {
            "dtype": {
                "type": "select",
                "options": ["float32", "int32", "bool"],
                "value": "float32"
            },
            "trainable": {"type": "boolean", "value": false},
            "updatable": {"type": "boolean", "value": false},

            "class_name": "Maximum"
        },

        "Minimum": {
            "dtype": {
                "type": "select",
                "options": ["float32", "int32", "bool"],
                "value": "float32"
            },
            "trainable": {"type": "boolean", "value": false},
            "updatable": {"type": "boolean", "value": false},

            "class_name": "Minimum"
        },


        "Multiply": {
            "dtype": {
                "type": "select",
                "options": ["float32", "int32", "bool"],
                "value": "float32"
            },
            "trainable": {"type": "boolean", "value": false},
            "updatable": {"type": "boolean", "value": false},
            "class_name": "Multiply"
        },
        "Dot": {
            "axes": {"type": "integer_list", "value": "[-1]"},
            "normalize": {"type": "boolean", "value": false},
            "class_name": "Dot"
        },

    },

    "Normalization Layers": {
        "BatchNormalization": {
            "axis": {"type": "integer", "value": -1},
            "momentum": {"type": "float", "value": 0.99},
            "epsilon": {"type": "float", "value": 0.001},
            "center": {"type": "boolean", "value": true},
            "scale": {"type": "boolean", "value": true},
            "beta_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "gamma_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "ones"
            },
            "moving_mean_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "moving_variance_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "ones"
            },
            "beta_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "gamma_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "beta_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "gamma_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "class_name": "BatchNormalization"
        },
    },


    "Pooling Layers": {
        "AveragePooling1D": {
            "pool_size": {"type": "integer", "value": null},
            "strides": {"type": "integer", "value": null},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "class_name": "AveragePooling1D"
        },
        "AveragePooling2D": {
            "pool_size": {"type": "integer_list", "value": null},
            "strides": {"type": "integer_list", "value": null},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "AveragePooling2D"
        },

        "GlobalAveragePooling1D": {

            "dtype": {
                "type": "select",
                "options": ["float32", "int32", "bool"],
                "value": "float32"
            },
            "trainable": {"type": "boolean", "value": false},
            "updatable": {"type": "boolean", "value": false},

            "class_name": "GlobalAveragePooling1D"
        },


        "GlobalAveragePooling2D": {
            "data_format": {
                "type": "select",
                "options": [null, "channels_last", "channels_first"],
                "value": null
            }, "class_name": "GlobalAveragePooling2D"
        },

        "GlobalMaxPooling1D": {

            "dtype": {
                "type": "select",
                "options": ["float32", "int32", "bool"],
                "value": "float32"
            },
            "trainable": {"type": "boolean", "value": false},
            "updatable": {"type": "boolean", "value": false},

            "class_name": "GlobalMaxPooling1D"
        },

        "GlobalMaxPooling2D": {
            "data_format": {
                "type": "select",
                "options": [null, "channels_last", "channels_first"],
                "value": null
            }, "class_name": "GlobalMaxPooling2D"
        },

        "MaxPooling1D": {
            "pool_size": {"type": "integer", "value": null},
            "strides": {"type": "integer", "value": null},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "class_name": "MaxPooling1D"
        },
        "MaxPooling2D": {
            "pool_size": {"type": "integer_list", "value": null},
            "strides": {"type": "integer_list", "value": null},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "MaxPooling2D"
        }

    },

    "Recurrent Layers": {
        "GRU": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "recurrent_activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "hardSigmoid"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            //"activity_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "return_sequences": {"type": "boolean", "value": false},
            "return_state": {"type": "boolean", "value": false},
            "go_backwards": {"type": "boolean", "value": false},
            // "stateful": {"type": "boolean", "value": false},
            "unroll": {"type": "boolean", "value": false},
            "reset_after": {"type": "boolean", "value": false},
            "class_name": "GRU"
        },

        "GRUCell": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "recurrent_activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "hardSigmoid"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "reset_after": {"type": "boolean", "value": false},
            "class_name": "GRUCell"
        },

        "LSTM": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "recurrent_activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "hard_sigmoid"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "unit_forget_bias": {"type": "boolean", "value": true},
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            //"activity_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "return_sequences": {"type": "boolean", "value": false},
            "return_state": {"type": "boolean", "value": false},
            "go_backwards": {"type": "boolean", "value": false},
            "stateful": {"type": "boolean", "value": false},
            "unroll": {"type": "boolean", "value": false},
            "class_name": "LSTM"
        },
        "LSTMCell": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "recurrent_activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "hard_sigmoid"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "unit_forget_bias": {"type": "boolean", "value": true},
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "class_name": "LSTMCell"
        },

        "RNN": {
            "return_sequences": {"type": "boolean", "value": false},
            "return_state": {"type": "boolean", "value": false},
            "go_backwards": {"type": "boolean", "value": false},
            "stateful": {"type": "boolean", "value": false},
            "unroll": {"type": "boolean", "value": false},
            "class_name": "RNN"
        },
        "SimpleRNN": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            //"activity_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "return_sequences": {"type": "boolean", "value": false},
            "return_state": {"type": "boolean", "value": false},
            "go_backwards": {"type": "boolean", "value": false},
            "stateful": {"type": "boolean", "value": false},
            "unroll": {"type": "boolean", "value": false},
            "class_name": "SimpleRNN"
        },

        "SimpleRNNCell": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "class_name": "SimpleRNNCell"
        },

        "StackedRNNCells": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["elu", "hardSigmoid", "linear", "relu", "selu", "sigmoid", "softmax", "softplus", "softsign", "tanh", null],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "maxNorm", "minMaxNorm", "nonNeg", "unitNorm"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "class_name": "StackedRNNCells"
        },
    },
    //TODO
    // "Layers wrappers": {
    //     "Bidirectional": {
    //         "merge_mode": {
    //             "type": "select",
    //             "options": ["concat", "sum", "mul", "ave", null],
    //             "value": "concat"
    //         }, "class_name": "Bidirectional"
    //     },
    //     "TimeDistributed": {"class_name": "TimeDistributed"}
    //
    // },

    "Advanced Activations Layers": {
        "ELU": {
            "alpha": {
                "type": "float",
                "value": 1.0
            },
            "class_name": "ELU"
        },
        "LeakyReLU": {
            "alpha": {
                "type": "float",
                "value": 1.0
            },
            "class_name": "LeakyReLU"
        },
        "Softmax": {
            "axis": {
                "type": "integer",
                "value": -1
            },
            "class_name": "Softmax"
        },
        "ThresholdedReLU": {
            "theta": {
                "type": "float",
                "value": null
            },
            "class_name": "ThresholdedReLU"
        },
        "PReLU": {
            "alpha_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "zeros"
            },
            "alpha_regularizer": {"type": "select", "options": [null, "L1L2"], "value": null},
            "shared_axes": {"type": "integer_list", "value": null},
            "class_name": "PReLU"
        },

    },

    "Loss Functions": {
        "Loss": {
            "function": {
                "type": "select",
                "options": ["mean_squared_error", "absolute_difference", "cosine_distance", "hinge_loss", "huber_loss", "log_loss", "sigmoid_cross_entropy", "softmax_cross_entropy", "sparse_softmax_cross_entropy", "mean_pairwise_squared_error"],
                "value": "mean_squared_error"
            },
            "class_name": "Loss"
        },
    },


    "Canned Models": {
        "DNN": {
            "hidden_layers": {"type": "integer_list", "value": "[100]"},
            "activation_fn": {
                "type": "select",
                "options": ["elu", "relu", "selu", "sigmoid", "softmax", "softsign", "tanh", null],
                "value": "relu"
            },
            "kernel_initializer": {
                "type": "select",
                "options": ["glorotNormal", "glorotUniform", "heNormal", "identity", "leCunNormal", "ones", "orthogonal", "randomNormal", "randomUniform", "truncatedNormal", "varianceScaling", "zeros"],
                "value": "glorotUniform"
            },

            "l1_regularization": {
                "type": "float",
                "value": 0,
            },
            "l2_regularization": {
                "type": "float",
                "value": 0,
            },
            "dropout": {
                "type": "float",
                "value": 0,
            },
            "batch_norm": {
                "type": "boolean",
                "value": false,
            },
            "class_name": "DNN"
        },
        "Linear": {
            "sparse_combiner": {
                "type": "select",
                "value": "sum",
                "options": ["sum", "mean", "sqrtn"],
            },
            "class_name": "Linear"
        }

    },

};
