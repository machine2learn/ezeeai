from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()
setup(
    name='ezeeai',
    version='1.0',
    packages=['ezeeai', 'ezeeai.core', 'ezeeai.core.model', 'ezeeai.core.extensions', 'ezeeai.data',
              'ezeeai.data.utils', 'ezeeai.forms', 'ezeeai.utils', 'ezeeai.config', 'ezeeai.database',
              'ezeeai.generator', 'ezeeai.app_config'],
    url='',
    license='',
    author='machine2learn',
    author_email='',
    description='',
    include_package_data=True,
    install_requires=required,
)
