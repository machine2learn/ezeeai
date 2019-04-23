import configparser
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT, 'app_config.ini')

SQLALCHEMY = 'SQLALCHEMY'
FLASK = 'FLASK'
APP = 'APP'


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


class ConfigApp(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_PATH)

    def get(self, section, param):
        return self.config.get(section, param)

    def database_uri(self):
        return self.get(SQLALCHEMY, 'DATABASE_URI')

    def track_modifications(self):
        return str2bool(self.get(SQLALCHEMY, 'TRACK_MODIFICATIONS'))

    def json_sort_keys(self):
        return str2bool(self.get(FLASK, 'JSON_SORT_KEYS'))

    def debug(self):
        return str2bool(self.get(FLASK, 'DEBUG'))

    def threaded(self):
        return str2bool(self.get(FLASK, 'THREADED'))

    def host(self):
        return self.get(FLASK, 'HOST')

    def port(self):
        return self.get(FLASK, 'PORT')

    # def server_name(self):
    #     return self.config.get(FLASK, 'SERVER_NAME')

    # def app_root(self):
    #     return self.config.get(FLASK, 'APPLICATION_ROOT')

    def sample_data_size(self):
        return int(self.get(APP, 'SAMPLE_DATA_SIZE'))

    def max_features(self):
        return int(self.get(APP, 'MAX_FEATURES'))

    def max_categorical_size(self):
        return int(self.get(APP, 'MAX_CATEGORICAL_SIZE'))

    def max_range_size(self):
        return int(self.get(APP, 'MAX_RANGE_SIZE'))

    def min_range_size(self):
        return int(self.get(APP, 'MIN_RANGE_SIZE'))

    # def get_tabular_args(self):
    #     return {
    #         'max_categorigal_size': self.get(APP, 'MAX_CATEGORICAL_SIZE'),
    #         'max_range_size': self.get(APP, 'MAX_RANGE_SIZE'),
    #         'min_range_size': self.get(APP, 'MIN_RANGE_SIZE')
    #     }

# if __name__ == '__main__':
#     c = ConfigApp()
#     print(c.get_sql_database_uri())
#     print(c.config.sections())
