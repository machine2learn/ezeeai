var corelayers = {
    "Core Layers": {
        "Dense": {
            "name": {"type": "text", "value": ""},
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "trainable": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },

            "class_name": "Dense"
        },

        "Activation": {
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            }, "class_name": "Activation"
        },


        "Masking": {"mask_value": {"type": "float", "value": 0.0}, "class_name": "Masking"},


        "InputLayer": {
            "name": {"type": "text", "value": ""},
            "dtype": {
                "type": "select",
                "options": ["float32", "float64", "int32"],
                "value": "float32"
            },
            "sparse": {"type": "boolean", "value": false},

            "input_shape": {"type": "integer_list", 'value': '[1,100]'},
            "class_name": "InputLayer"
        },


        "Dropout": {
            "rate": {"type": "float", "value": 0, "min": 0, "max": 1},
            "noise_shape": {"type": "integer_list", "value": '[1]'},
            "seed": {"type": "integer", "value": null, "min": 0},
            "class_name": "Dropout"
        },

        "Reshape": {"target_shape": {"type": "integer_list", "value": '[1]'}, "class_name": "Reshape"},
        "Permute": {"dims": {"type": "integer_list", "value": '[1]'}, "class_name": "Permute"},
        "Flatten": {
            "data_format": {
                "type": "select",
                "options": [null, "channels_last", "channels_first"],
                "value": null
            }, "class_name": "Flatten"
        },
        "RepeatVector": {"class_name": "RepeatVector"},
        "Lambda": {"class_name": "Lambda"},

        "ActivityRegularization": {
            "l1": {"type": "float", "value": 0.0},
            "l2": {"type": "float", "value": 0.0},
            "class_name": "ActivityRegularization"
        },
        "SpatialDropout1D": {
            "rate": {"type": "float", "value": 0, "min": 0, "max": 1},
            "class_name": "SpatialDropout1D"
        },
        "SpatialDropout2D": {
            "rate": {"type": "float", "value": 0, "min": 0, "max": 1},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "SpatialDropout2D"
        },
        "SpatialDropout3D": {
            "rate": {"type": "float", "value": 0, "min": 0, "max": 1},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "SpatialDropout3D"
        },

        "MaxoutDense": {
            "output_dim": {"type": "integer", "value": 1, "min": 0},
            "init": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "W_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "b_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "W_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "b_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias": {"type": "boolean", "value": true},
            "input_dim": {"type": "integer", "value": 1, "min": 1},
            "class_name": "MaxoutDense"
        },
    },

    "Convolutional Layers": {
        "SeparableConv1D": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilation_rate": {"type": "integer_list", "value": "[1]"},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "depthwise_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "pointwise_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "depthwise_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "pointwise_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "depthwise_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "pointwise_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "SeparableConv1D"
        },
        "SeparableConv2D": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilation_rate": {"type": "integer_list", "value": "[1]"},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "depthwise_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "pointwise_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "depthwise_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "pointwise_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "depthwise_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "pointwise_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "SeparableConv2D"
        },

        "UpSampling1D": {"class_name": "UpSampling1D"},
        "UpSampling2D": {
            "data_format": {
                "type": "select",
                "options": [null, "channels_last", "channels_first"],
                "value": null
            }, "class_name": "UpSampling2D"
        },
        "UpSampling3D": {
            "data_format": {
                "type": "select",
                "options": [null, "channels_last", "channels_first"],
                "value": null
            }, "class_name": "UpSampling3D"
        },
        "ZeroPadding1D": {
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "class_name": "ZeroPadding1D"
        },
        "ZeroPadding2D": {
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "ZeroPadding2D"
        },
        "ZeroPadding3D": {
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "ZeroPadding3D"
        },
        "Conv1D": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilation_rate": {"type": "integer_list", "value": "[1]"},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "Conv1D"
        },
        "Conv2D": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilation_rate": {"type": "integer_list", "value": "[1]"},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "Conv2D"
        },
        "Conv3D": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilation_rate": {"type": "integer_list", "value": "[1]"},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "Conv3D"
        },
        "Conv2DTranspose": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "Conv2DTranspose"
        },

        "Cropping1D": {"cropping": {"type": "integer_list", "value": "(1,1)"}, "class_name": "Cropping1D"},
        "Cropping2D": {
            "cropping": {"type": "integer_list", "value": "(1,1)"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "Cropping2D"
        },
        "Cropping3D": {
            "cropping": {"type": "integer_list", "value": "(1,1)"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "Cropping3D"
        },

        "DepthwiseConv2D": {
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "depthwise_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "depthwise_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "depthwise_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "DepthwiseConv2D"
        },

    },


    "Pooling Layers": {

        "MaxPooling1D": {
            "pool_size": {"type": "integer_list", "value": "[2,2]"},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "class_name": "MaxPooling1D"
        },
        "AveragePooling1D": {
            "pool_size": {"type": "integer_list", "value": "[2,2]"},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "class_name": "AveragePooling1D"
        },
        "MaxPooling2D": {
            "pool_size": {"type": "integer_list", "value": "[2,2]"},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "MaxPooling2D"
        },
        "AveragePooling2D": {
            "pool_size": {"type": "integer_list", "value": "[2,2]"},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "AveragePooling2D"
        },
        "MaxPooling3D": {
            "pool_size": {"type": "integer_list", "value": "[2,2]"},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "MaxPooling3D"
        },
        "AveragePooling3D": {
            "pool_size": {"type": "integer_list", "value": "[2,2]"},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "class_name": "AveragePooling3D"
        },
        "GlobalAveragePooling1D": {"class_name": "GlobalAveragePooling1D"},
        "GlobalMaxPooling1D": {"class_name": "GlobalMaxPooling1D"},
        "GlobalAveragePooling2D": {
            "data_format": {
                "type": "select",
                "options": [null, "channels_last", "channels_first"],
                "value": null
            }, "class_name": "GlobalAveragePooling2D"
        },
        "GlobalMaxPooling2D": {
            "data_format": {
                "type": "select",
                "options": [null, "channels_last", "channels_first"],
                "value": null
            }, "class_name": "GlobalMaxPooling2D"
        },
        "GlobalAveragePooling3D": {
            "data_format": {
                "type": "select",
                "options": [null, "channels_last", "channels_first"],
                "value": null
            }, "class_name": "GlobalAveragePooling3D"
        },
        "GlobalMaxPooling3D": {
            "data_format": {
                "type": "select",
                "options": [null, "channels_last", "channels_first"],
                "value": null
            }, "class_name": "GlobalMaxPooling3D"
        },


    },


    "Locally-connected Layers": {
        "LocallyConnected1D": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "LocallyConnected1D"
        },
        "LocallyConnected2D": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "LocallyConnected2D"
        },


    },


    "Recurrent Layers": {
        "Recurrent": {
            "return_sequences": {"type": "boolean", "value": false},
            "return_state": {"type": "boolean", "value": false},
            "go_backwards": {"type": "boolean", "value": false},
            "stateful": {"type": "boolean", "value": false},
            "unroll": {"type": "boolean", "value": false},
            "class_name": "Recurrent"
        },


        "RNN": {
            "return_sequences": {"type": "boolean", "value": false},
            "return_state": {"type": "boolean", "value": false},
            "go_backwards": {"type": "boolean", "value": false},
            "stateful": {"type": "boolean", "value": false},
            "unroll": {"type": "boolean", "value": false},
            "class_name": "RNN"
        },
        "SimpleRNNCell": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "class_name": "SimpleRNNCell"
        },

        "SimpleRNN": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
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
        "GRU": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "recurrent_activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "hard_sigmoid"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "return_sequences": {"type": "boolean", "value": false},
            "return_state": {"type": "boolean", "value": false},
            "go_backwards": {"type": "boolean", "value": false},
            "stateful": {"type": "boolean", "value": false},
            "unroll": {"type": "boolean", "value": false},
            "reset_after": {"type": "boolean", "value": false},
            "class_name": "GRU"
        },
        "LSTM": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "recurrent_activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "hard_sigmoid"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "unit_forget_bias": {"type": "boolean", "value": true},
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
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
        "GRUCell": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "recurrent_activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "hard_sigmoid"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "reset_after": {"type": "boolean", "value": false},
            "class_name": "GRUCell"
        },
        "LSTMCell": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "recurrent_activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "hard_sigmoid"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "unit_forget_bias": {"type": "boolean", "value": true},
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "class_name": "LSTMCell"
        },
        "CuDNNGRU": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "return_sequences": {"type": "boolean", "value": false},
            "return_state": {"type": "boolean", "value": false},
            "stateful": {"type": "boolean", "value": false},
            "class_name": "CuDNNGRU"
        },
        "CuDNNLSTM": {
            "units": {"type": "integer", "value": 100, "min": 1},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "unit_forget_bias": {"type": "boolean", "value": true},
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "return_sequences": {"type": "boolean", "value": false},
            "return_state": {"type": "boolean", "value": false},
            "stateful": {"type": "boolean", "value": false},
            "class_name": "CuDNNLSTM"
        },
        "ConvLSTM2D": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilation_rate": {"type": "integer_list", "value": "[1]"},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "recurrent_activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "hard_sigmoid"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "unit_forget_bias": {"type": "boolean", "value": true},
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "return_sequences": {"type": "boolean", "value": false},
            "go_backwards": {"type": "boolean", "value": false},
            "stateful": {"type": "boolean", "value": false},
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "class_name": "ConvLSTM2D"
        },
        "ConvLSTM2DCell": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilation_rate": {"type": "integer_list", "value": "[1]"},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "recurrent_activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "hard_sigmoid"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "recurrent_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Orthogonal"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "unit_forget_bias": {"type": "boolean", "value": true},
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "recurrent_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "recurrent_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "dropout": {"type": "float", "value": 0.0},
            "recurrent_dropout": {"type": "float", "value": 0.0},
            "class_name": "ConvLSTM2DCell"
        },
        "Model": {"class_name": "Model"},

        "ConvRecurrent2D": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "dilation_rate": {"type": "integer_list", "value": "[1]"},
            "return_sequences": {"type": "boolean", "value": false},
            "go_backwards": {"type": "boolean", "value": false},
            "stateful": {"type": "boolean", "value": false},
            "class_name": "ConvRecurrent2D"
        },


        "Conv3DTranspose": {
            "filters": {"type": "integer", "value": 1, "min": 1},
            "kernel_size": {"type": "integer", "value": 1},
            "strides": {"type": "integer_list", "value": "[1]"},
            "padding": {"type": "select", "options": ["valid", "causal", "same"], "value": "valid"},
            "data_format": {"type": "select", "options": [null, "channels_last", "channels_first"], "value": null},
            "activation": {
                "type": "select",
                "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
                "value": "relu"
            },
            "use_bias": {"type": "boolean", "value": true},
            "kernel_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "glorot_uniform"
            },
            "bias_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "kernel_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "bias_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "kernel_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "bias_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "Conv3DTranspose"
        },

        "ConvRNN2D": {
            "return_sequences": {"type": "boolean", "value": false},
            "return_state": {"type": "boolean", "value": false},
            "go_backwards": {"type": "boolean", "value": false},
            "stateful": {"type": "boolean", "value": false},
            "unroll": {"type": "boolean", "value": false},
            "class_name": "ConvRNN2D"
        },
        "StackedRNNCells": {"class_name": "StackedRNNCells"},
    },

    "Embedding Layers": {
        "Embedding": {
            "input_dim": {"type": "integer", "value": 1, "min": 1},
            "output_dim": {"type": "integer", "value": 1, "min": 0},
            "embeddings_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "uniform"
            },
            "embeddings_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "activity_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "embeddings_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "mask_zero": {"type": "boolean", "value": false},
            "class_name": "Embedding"
        },
    },

    "Merge Layers": {
        "Add": {"class_name": "Add"},
        "Subtract": {"class_name": "Subtract"},
        "Multiply": {"class_name": "Multiply"},
        "Average": {"class_name": "Average"},
        "Maximum": {"class_name": "Maximum"},
        "Minimum": {"class_name": "Minimum"},
        "Concatenate": {"axis": {"type": "integer", "value": -1}, "class_name": "Concatenate"},
        "Dot": {"normalize": {"type": "boolean", "value": false}, "class_name": "Dot"},

    },


    "Advanced Activations Layers": {
        "LeakyReLU": {"alpha": {"type": "float", "value": 1.0}, "class_name": "LeakyReLU"},
        "PReLU": {
            "alpha_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "alpha_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "alpha_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "PReLU"
        },
        "ELU": {"alpha": {"type": "float", "value": 1.0}, "class_name": "ELU"},
        "ThresholdedReLU": {"theta": {"type": "float", "value": 1.0}, "class_name": "ThresholdedReLU"},
        "Softmax": {"axis": {"type": "integer", "value": -1}, "class_name": "Softmax"},
        "ReLU": {"class_name": "ReLU"},

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
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "gamma_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Ones"
            },
            "moving_mean_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Zeros"
            },
            "moving_variance_initializer": {
                "type": "select",
                "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "Identity", "Orthogonal", "VarianceScaling", "TruncatedNormal", "RandomUniform", "RandomNormal", "Constant", "Ones", "Zeros"],
                "value": "Ones"
            },
            "beta_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "gamma_regularizer": {"type": "select", "options": [null, "l1", "l2", "l1_l2"], "value": null},
            "beta_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "gamma_constraint": {
                "type": "select",
                "options": [null, "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
                "value": null
            },
            "class_name": "BatchNormalization"
        },
    },


    "Noise Layers": {

        "GaussianNoise": {"stddev": {"type": "float", "value": 0.05}, "class_name": "GaussianNoise"},
        "GaussianDropout": {"rate": {"type": "float", "value": 0, "min": 0, "max": 1}, "class_name": "GaussianDropout"},
        "AlphaDropout": {
            "rate": {"type": "float", "value": 0, "min": 0, "max": 1},
            "noise_shape": {"type": "integer_list", "value": '[1]'},
            "seed": {"type": "integer", "value": null},
            "class_name": "AlphaDropout"
        },

    },

    "Layers wrappers": {

        "TimeDistributed": {"class_name": "TimeDistributed"},
        "Bidirectional": {
            "merge_mode": {
                "type": "select",
                "options": ["concat", "sum", "mul", "ave", null],
                "value": "concat"
            }, "class_name": "Bidirectional"
        }

    },

};