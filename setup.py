from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()
setup(
    name='easyai',
    version='1.0',
    packages=['easyai', 'easyai.core', 'easyai.core.model', 'easyai.core.extensions', 'easyai.data',
              'easyai.data.utils', 'easyai.forms', 'easyai.utils', 'easyai.config', 'easyai.database',
              'easyai.generator', 'easyai.app_config'],
    url='',
    license='',
    author='machine2learn',
    author_email='',
    description='',
    include_package_data=True,
    install_requires=required,
)
