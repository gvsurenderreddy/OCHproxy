from distutils.core import setup

setup(
    name='OCHproxy',
    version='0.1',
    packages=['hoster', 'modules'],
    install_requires=[
        'requests', 'pluginbase',
    ],
    url='',
    license='Apache License',
    author='bauerj',
    author_email='bauerj@bauerj.eu',
    description='OCHproxy is an API that eases downloading from one-click hosters.'
)
