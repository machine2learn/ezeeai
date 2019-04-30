from easyai.config.config_reader import CustomConfigParser


class ConfigWriter:

    def __init__(self):
        self.config = CustomConfigParser()

    def itemize(self, form):
        result = []
        for k, value in form.items():
            # print(k, value)
            if 'token' not in k:  # csrf_token
                try:
                    section, key = k.split('-', 1)
                    result.append((section.upper(), key, value))
                except ValueError:
                    continue
        return result

    def populate_config(self, form):
        for section, key, value in self.itemize(form):
            self.add_item(section, key, value)

    def add_item(self, section, key, value):
        if section not in self.config.sections():
            self.config.add_section(section)
        self.config.set(section, key, value)

    def write_config(self, path):
        with open(path, 'w') as f:
            self.config.write(f)

    def append_config(self, path):
        with open(path, 'a') as f:
            self.config.write(f)
