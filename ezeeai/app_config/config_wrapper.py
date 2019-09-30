import configparser
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT, 'app_config.ini')

SQLALCHEMY = 'SQLALCHEMY'
FLASK = 'FLASK'
APP = 'APP'
PARAMS = 'DEFAULT_PARAMS'
PATHS = 'PATHS'


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


class ConfigApp(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_PATH)

    def get(self, section, param):
        return self.config.get(section, param)

    def user_root(self):
        if 'USER_ROOT' in os.environ:
            return os.environ['USER_ROOT']

        user_root = self.get(PATHS, 'USER_ROOT')

        if user_root != 'None' and not os.path.isdir(os.path.join(user_root)):
            os.makedirs(os.path.join(user_root))

        if user_root != 'None':
            return user_root

        return None

    def database_uri(self):
        # CHECK ENVIROMENT VARIABLES
        if 'DB_HOST' in os.environ and 'DB_NAME' in os.environ and 'DB_USER' in os.environ and 'DB_PASSWORD' in os.environ and 'DB_NAME' in os.environ:
            user = os.environ['DB_USER']
            password = os.environ['DB_PASSWORD']
            name = os.environ['DB_NAME']
            host = os.environ['DB_HOST']
            return f'postgresql+psycopg2://{user}:{password}@{host}/{name}'
        elif 'DB_HOST' in os.environ:
            return os.environ['DB_HOST']

        # CHECK app_config.ini
        if self.get(SQLALCHEMY, 'POSTGRES_DB') not in [None, 'None', 'none']:
            print('using postgres db')
            user = self.get(SQLALCHEMY, 'POSTGRES_USER')
            password = self.get(SQLALCHEMY, 'POSTGRES_PW')
            name = self.get(SQLALCHEMY, 'POSTGRES_DB')
            host = self.get(SQLALCHEMY, 'POSTGRES_URL')
            return f'postgresql+psycopg2://{user}:{password}@{host}/{name}'

        return self.get(SQLALCHEMY, 'DB_HOST')

    def track_modifications(self):
        return str2bool(self.get(SQLALCHEMY, 'TRACK_MODIFICATIONS'))

    def json_sort_keys(self):
        return str2bool(self.get(FLASK, 'JSON_SORT_KEYS'))

    def debug(self):
        if 'DEBUG' in os.environ:
            return str2bool(os.environ['DEBUG'])
        return str2bool(self.get(FLASK, 'DEBUG'))

    def threaded(self):
        return str2bool(self.get(FLASK, 'THREADED'))

    def host(self):
        return self.get(FLASK, 'HOST')

    def port(self):
        return self.get(FLASK, 'PORT')

    # def server_name(self):
    #     return self.config.get(FLASK, 'SERVER_NAME')

    # def USER_ROOT(self):
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

    def num_epochs(self):
        return int(self.get(PARAMS, 'num_epochs'))

    def batch_size(self):
        return int(self.get(PARAMS, 'batch_size'))

    def optimizer(self):
        return self.get(PARAMS, 'optimizer')

    def learning_rate(self):
        return float(self.get(PARAMS, 'learning_rate'))

    def throttle(self):
        return int(self.get(PARAMS, 'throttle'))

    def save_summary_steps(self):
        return int(self.get(PARAMS, 'save_summary_steps'))

    def save_checkpoints_steps(self):
        return int(self.get(PARAMS, 'save_checkpoints_steps'))

    def keep_checkpoint_max(self):
        return int(self.get(PARAMS, 'keep_checkpoint_max'))

    def secret_key(self):
        if 'SECRET_KEY' in os.environ:
            return os.environ['SECRET_KEY']
        return os.urandom(42)

# if __name__ == '__main__':
#     c = ConfigApp()
#     print(c.get_sql_database_uri())
#     print(c.config.sections())
