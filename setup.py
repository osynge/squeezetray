from sqtray.__version__ import version
from sys import version_info

from distutils.core import setup

Application = 'SqueezeWxTray'

setup(name=Application,
    version=version,
    description="VM Image list subscribing tool.",
    long_description="""This application attempts to be the equivalent of a modern Linux package update
manager but for lists of virtual machines signed with x509. It uses a database
back end, and caches available image lists.""",
    author="O M Synge",
    author_email="owen.synge@desy.de",
    license='Apache License (2.0)',
    install_requires=[
       "wx",
        ],
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
    data_files=[('/usr/share/doc/%s-%s' % (Application,version),['README.md','LICENSE','ChangeLog'])]
    )
