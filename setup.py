from sys import version_info


if version_info < (2, 7):
    from distutils.core import setup
    import sys
    print("Please use a newer version of python")
    sys.exit(1)


if version_info > (2, 7):
    try:
        from setuptools import setup, find_packages
    except ImportError:
        try:
                from distutils.core import setup
        except ImportError:
                from ez_setup import use_setuptools
                use_setuptools()
                from setuptools import setup, find_packages


# Get version without importing the module.
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('sqtray/__version__.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)


from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        try:
            # import here, because outside the eggs aren't loaded
            import pytest
        except ImportError:
            raise RuntimeError("py.test is not installed, "
                               "run: pip install pytest")
        errno = pytest.main([self.pytest_args])
        sys.exit(errno)



Application = 'SqueezeWxTray'

setup_args = {'name': Application,
    'version': main_ns['version'],
    'description': "GUI client for logitech squeesebox server.",
    'long_description': """Squeezebox control from your linux desktop. Based on wxpython and threads this 
application allows control of your squeezeboxes via mouse.""",
    'author': "O M Synge",
    'author_email': "owen.synge@desy.de",
    'license': 'Apache License (2.0)',
    'install_requires': [],
    'url' :  'https://github.com/hepix-virtualisation/hepixvmilsubscriber',
    'packages' :  ['sqtray'],
    'classifiers': [
        'Development Status :: 1 - UnStable',
        'Environment :: GUI',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ],
    'scripts': ['squeezetray'],
    'data_files': [('/usr/share/doc/%s-%s' % (Application,main_ns['version']),['README.md','LICENSE','logger.conf','ChangeLog']),
            ('/usr/share/pixmaps/%s' % (Application),[
                'icons/application_disconected.svg',
                'icons/application_connected.svg',
                'icons/play.svg', 
                'icons/stop.svg',
                'icons/pause.svg',
                'icons/forward.svg',
                'icons/backward.svg',
                ])],
    'tests_require': [
        'coverage >= 3.0',
        'pytest >= 2.1.3',
        'mock >= 1.0b1',
    ],
    'setup_requires': [
        'pytest',
    ],
    "cmdclass": {'test': PyTest},
}

setup_args['tests_require'] = setup_args.get('install_requires', []).extend(
    setup_args.get('tests_require', []))
setup(**setup_args)
