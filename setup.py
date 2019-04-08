from sqtray.__version__ import version
from sys import version_info

try:
    from setuptools import setup, find_packages
except ImportError:
	try:
            from distutils.core import setup
	except ImportError:
            from ez_setup import use_setuptools
            use_setuptools()
            from setuptools import setup, find_packages
# we want this module for nosetests
try:
    import multiprocessing
except ImportError:
    # its not critical if this fails though.
    pass

Application = 'SqueezeWxTray'

setup(name=Application,
    version=version,
    description="GUI client for logitech squeesebox server.",
    long_description="""Squeezebox control from your linux desktop. Based on wxpython and threads this 
application allows control of your squeezeboxes via mouse.""",
    author="O M Synge",
    author_email="owen.synge@desy.de",
    license='Apache License (2.0)',
    install_requires=[],
    url = 'https://github.com/hepix-virtualisation/hepixvmilsubscriber',
    packages = ['sqtray'],
    classifiers=[
        'Development Status :: 1 - UnStable',
        'Environment :: GUI',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ],
    scripts=['squeezetray'],
    data_files=[('/usr/share/doc/%s-%s' % (Application,version),['README.md','LICENSE','logger.conf','ChangeLog']),
            ('/usr/share/pixmaps/%s' % (Application),[
                'icons/application_disconected.svg',
                'icons/application_connected.svg',
                'icons/play.svg', 
                'icons/stop.svg',
                'icons/pause.svg',
                'icons/forward.svg',
                'icons/backward.svg',
                ])],
    tests_require=[
        'coverage >= 3.0',
        'nose >= 1.1.0',
        'mock',
    ],
    setup_requires=[
        'nose',
    ],
    test_suite = 'nose.collector',
    )
