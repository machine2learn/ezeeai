import inspect
from keras.engine import Layer
import json

core_layers = {}
data = open("corelayers").read()
json_data = json.loads(data)


def _all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in _all_subclasses(s)]


subclasses = _all_subclasses(Layer)

for subclass in subclasses:
    sig = inspect.signature(subclass.__init__)
    name_class = subclass.__name__
    if name_class[0] != '_':
        core_layers[name_class] = {}
        for k, v in sig.parameters.items():
            if k in json_data.keys():
                core_layers[name_class][k] = json_data[k]
        core_layers[name_class]['class_name'] = name_class

del core_layers['Network']

print(core_layers)
with open('keraslayers', 'w') as fp:
    json.dump(core_layers, fp)



#---- NOT ADDED YET
# //  "arguments",
#   //  "axes",
#   //  "batch_size",
#   //  "cells",
#   //  "cell",
#   //  "depth_multiplier",
#   //  "dims",
#   //  "function",
#   //  "implementation",
#   //  "input_length",
#   //  "input_tensor",
#   //  "layer",
#   //  "layers",
#   //  "mask",
#   //  "n",
#   //  "nb_feature",
#   //  "rank",
#   //  "rate",
#   //  "shared_axes",
#   //  "size",
#   //  "weights",
#
#   "max_value": {
#     "type": "float",
#     "value": None
#   },
#   "seed": {
#     "type": "integer",
#     "value": None
#   },
#   "target_shape": {
#     "type": "integer_list",
#     "value": None
#   },
#   "input_shape": {
#     "type": "integer_list",
#     "value": None
#   },
#   "batch_input_shape": {
#     "type": "integer_list",
#     "value": None
#   },
#
#   "output_shape": {
#     "type": "integer_list",
#     "value": None
#   },
#

    # "Wrapper": {"class_name": "Wrapper"},
    #
    # "Highway": {
    #     "init": {
    #         "type": "select",
    #         "options": ["glorot_uniform", "he_uniform", "lecun_normal", "he_normal", "glorot_normal", "lecun_uniform", "identity", "orthogonal", "variance_scaling", "truncated_normal", "random_uniform", "random_normal", "constant", "ones", "zeros", "initializer"],
    #         "value": "glorot_uniform"
    #     },
    #     "activation": {
    #         "type": "select",
    #         "options": ["tanh", "softmax", "selu", "softplus", "softsign", "relu", "sigmoid", "hard_sigmoid", "linear"],
    #         "value": "relu"
    #     },
    #     "W_regularizer": {"type": "select", "options": ["None", "l1", "l2", "l1_l2"], "value": "None"},
    #     "b_regularizer": {"type": "select", "options": ["None", "l1", "l2", "l1_l2"], "value": "None"},
    #     "activity_regularizer": {"type": "select", "options": ["None", "l1", "l2", "l1_l2"], "value": "None"},
    #     "W_constraint": {
    #         "type": "select",
    #         "options": ["None", "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
    #         "value": "None"
    #     },
    #     "b_constraint": {
    #         "type": "select",
    #         "options": ["None", "max_norm(max_value=2, axis=0)", "non_neg()", "unit_norm(axis=0)", "min_max_norm(min_value=0.0, max_value=1.0, rate=1.0, axis=0)"],
    #         "value": "None"
    #     },
    #     "bias": {"type": "boolean", "value": true},
    #     "input_dim": {"type": "integer", "value": 1, "min": 1},
    #     "class_name": "Highway"
    # },
#---- NOT ADDED YET






#
# params_string = {}
# params_none = {}
# params_bool = {}
# params_empty = {}
# params_float= {}
# params_int= {}
# for subclass in subclasses:
#     sig = inspect.signature(subclass.__init__)
#     name_class = subclass.__name__
#
#     core_layers[name_class] = {}
#
#     for k, v in sig.parameters.items():
#         if v.default == None:
#             params_none[k] = ""
#
#         else:
#             if isinstance(v.default, float):
#                 params_float[k] = v.default
#             if isinstance(v.default, str):
#                 params_string[k] = v.default
#             if isinstance(v.default, bool):
#                 params_bool[k] = v.default
#             else:
#                 if k not in params_float and k not in params_string and k not in params_bool:
#                     params_empty[k] = ''
#
# del params_empty['self']
# del params_empty['args']
# del params_empty['kwargs']
#
#
# print('string ' + str(len(params_string.keys())))
# print(params_string)
# print('none ' + str(len(params_none.keys())))
# print(params_none.keys())
# print('empty ' + str(len(params_empty.keys())))
# print(params_empty.keys())
# print('bool ' + str(len(params_bool.keys())))
# print(params_bool)
# print('float ' + str(len(params_float.keys())))
# print(params_float)
#
# # print(core_layers)
