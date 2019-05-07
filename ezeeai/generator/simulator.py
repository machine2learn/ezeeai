from lark import Lark, UnexpectedCharacters, ParseError, v_args
from lark import Transformer
import pandas as pd
import numpy as np
from ..utils.sys_ops import mkdir_recursive, tree_remove
import itertools
import functools
import os

with open('ezeeai/generator/cluster', 'r') as f:
    text = f.read()

with open('ezeeai/generator/grammar', 'r') as f:
    grammar = f.read()

random_generator_parser = Lark(grammar, start='definition', ambiguity='explicit')


def multivariate(means, covs, sample_size):
    if type(covs) != list:
        covs = covs * np.eye(len(means))
    return np.random.multivariate_normal(means, covs, sample_size)


class DataSetGeneratorTransformer(Transformer):
    from operator import add, sub, mul, truediv as div, neg

    @v_args(inline=True)
    def random_variables(self, names, values):
        assert len(names) == values.shape[
            1], f"Value dimension do not agree with variable dimension {names} have " \
                f"{len(names)} whereas values {values.shape[-1]}"
        new_columns = dict(zip(names, values.T))
        new_columns = {k: v.reshape((-1, 1)) for k, v in new_columns.items()}
        self.columns.update(new_columns)

    @v_args(inline=True)
    def create(self, distribution):
        result = distribution()
        if result.ndim == 1:
            result = result.reshape(-1, 1)
        return result

    def sizes(self, parts):
        ratio = self.sample_size / parts
        remainder = self.sample_size % parts

        return [int(ratio + 1)] * remainder + [int(ratio)] * (parts - remainder)

    def stack(self, items):
        shapes = np.array([item.shape[1] for item in items])
        assert all(shapes[0] == shapes)
        sizes = self.sizes(len(items))
        splitted = [i[:s] for i, s in zip(items, sizes)]
        return np.vstack(splitted)

    def stackall(self, items):
        total_dims = sum((item.shape[1] for item in items))
        sizes = self.sizes(total_dims)
        flatten = np.concatenate(items, axis=1).T.tolist()
        splitted = [np.array(i[:s]) for i, s in zip(flatten, sizes)]
        return np.concatenate(splitted).reshape(-1, 1)

    @v_args(inline=True)
    def range(self, lower, upper):
        assert upper >= lower, f"Range lower is larger than upper limit {lower} > {upper}"
        return list(range(lower, upper + 1))

    @v_args(inline=True)
    def multi(self, name, range):
        return [f"{name}{i}" for i in range]

    @v_args(inline=True)
    def single(self, name):
        return [name]

    distribution_fn_map = {
        "normal": np.random.normal,
        "pois": np.random.poisson,
        "uniform": np.random.uniform,
        "constant": lambda v, size: np.array([v] * size),
        "multivariate": multivariate,
        "range_dist": lambda start, size: np.arange(start, start + size),
        'choice': lambda choices, size: np.random.choice(choices, size)
    }

    @v_args(inline=True)
    def distribution(self, args):
        name = args.data
        return lambda: self.distribution_fn_map[name](*args.children, self.sample_size)

    @v_args(inline=True)
    def multi_dist(self, distr_fn, rep):
        temp = [distr_fn() for _ in range(rep)]
        if temp[0].ndim == 1:
            return lambda: np.array(temp).T
        return lambda: np.concatenate(temp, axis=1)

    @v_args(inline=True)
    def tile(self, values, rep):
        return np.tile(values, rep)

    @v_args(inline=True)
    def scalar(self, value):
        return value

    @v_args(inline=True)
    def rv(self, variable):  # also handle noise
        if all(v in self.columns.keys() for v in variable):
            return np.column_stack([self.columns[v] for v in variable])
        else:
            raise ValueError(f'Identifier {variable} not defined')

    @v_args(inline=True)
    def combine(self, left, right):
        def left_or_right(l, r):
            return l if l != 'not_assigned' and r == 'not_assigned' else r

        left = left.reshape(-1, )
        right = right.reshape(-1, )

        result = np.array([left_or_right(l, r) for l, r in zip(left, right)]).reshape((-1, 1))
        return result

    @v_args(inline=True)
    def bool_if(self, array, true_value):
        values = [true_value, "not_assigned"]

        def f(values, x):
            return values[0] if x else values[1]

        f = functools.partial(f, values)
        result = np.array(list(map(f, array))).reshape((-1, 1))
        return result

    @v_args(inline=True)
    def bool_compound(self, array, default_value):
        array = array.reshape(-1, )

        def f(x):
            return default_value if x == 'not_assigned' else x

        result = np.array(list(map(f, array))).reshape((-1, 1))
        return result

    def bool_array(self, values):
        return values[0]

    @v_args(inline=True)
    def equal(self, left, right):
        return left == right

    @v_args(inline=True)
    def inverse(self, item):
        return np.logical_not(item)

    @v_args(inline=True)
    def not_equal(self, left, right):
        return left != right

    @v_args(inline=True)
    def larger_equal(self, left, right):
        return left >= right

    @v_args(inline=True)
    def larger(self, left, right):
        return left > right

    @v_args(inline=True)
    def smaller(self, left, right):
        return left < right

    @v_args(inline=True)
    def smaller_equal(self, left, right):
        return left <= right

    @v_args(inline=True)
    def bool_and(self, left, right):
        return np.logical_and(left, right)

    @v_args(inline=True)
    def bool_or(self, left, right):
        return np.logical_or(left, right)

    @v_args(inline=True)
    def power(self, item, power):
        return np.power(item, power)

    @v_args(inline=True)
    def log(self, item):
        return np.log(item)

    @v_args(inline=True)
    def sqrt(self, item):
        return np.sqrt(item)

    mul = v_args(inline=True)(mul)
    add = v_args(inline=True)(add)
    sub = v_args(inline=True)(sub)
    div = v_args(inline=True)(div)
    neg = v_args(inline=True)(neg)

    @v_args(inline=True)
    def addlist(self, name, low, high):
        return np.sum([self.columns[name + str(i)] for i in range(low, high + 1)], axis=0)

    @v_args(inline=True)
    def mullist(self, name, low, high):
        return np.prod([self.columns[name + str(i)] for i in range(low, high + 1)], axis=0)

    @v_args(inline=True)
    def samplenumber(self, sample_size):
        self.sample_size = sample_size
        self.columns = {}

    def output(self, items):
        columns = {a: self.columns[a] for a in items[0]} if items else self.columns
        flatten = {k: v.squeeze() for k, v in columns.items()}
        self.df = pd.DataFrame.from_dict(flatten)
        # pprint(self.df)

    @v_args(inline=True)
    def id(self, s):
        return s.value

    @v_args(inline=True)
    def string(self, s):
        return s.value[1:-1]

    @v_args(inline=True)
    def seed(self, seed):
        np.random.seed(seed)

    def id_array(self, items):
        return list(itertools.chain.from_iterable(items))

    number = v_args(inline=True)(float)
    int = v_args(inline=True)(int)
    array = list
    string_array = list


def parse(script, path, datsetname):
    try:
        rg_tree = random_generator_parser.parse(script)

        transformer = DataSetGeneratorTransformer()
        transformer.transform(rg_tree)
        mkdir_recursive(path)
        transformer.df.to_csv(os.path.join(path, datsetname + '.csv'), index=False)
        open(os.path.join(path, '.tabular'), 'w')
    except (UnexpectedCharacters, ParseError, ValueError) as e:
        if os.path.isdir(path):
            tree_remove(path)
        raise e


