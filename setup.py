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
            ('/usr/share/pixmaps/%s' % (Application),['icons/media_eject_128x128.png',
                'icons/media_eject_16x16.png', 
                'icons/media_eject_22x22.png', 
                'icons/media_eject_24x24.png', 
                'icons/media_eject_32x32.png', 
                'icons/media_eject_48x48.png', 
                'icons/media_eject_72x72.png', 
                'icons/media_playback_pause_128x128.png', 
                'icons/media_playback_pause_16x16.png', 
                'icons/media_playback_pause_22x22.png', 
                'icons/media_playback_pause_24x24.png', 
                'icons/media_playback_pause_32x32.png', 
                'icons/media_playback_pause_48x48.png', 
                'icons/media_playback_pause_72x72.png', 
                'icons/media_playback_start_128x128.png', 
                'icons/media_playback_start_16x16.png', 
                'icons/media_playback_start_22x22.png', 
                'icons/media_playback_start_24x24.png', 
                'icons/media_playback_start_32x32.png', 
                'icons/media_playback_start_48x48.png', 
                'icons/media_playback_start_72x72.png', 
                'icons/media_playback_stop_128x128.png',
                'icons/media_playback_stop_16x16.png', 
                'icons/media_playback_stop_22x22.png', 
                'icons/media_playback_stop_24x24.png', 
                'icons/media_playback_stop_32x32.png', 
                'icons/media_playback_stop_48x48.png', 
                'icons/media_playback_stop_72x72.png', 
                'icons/media_record_128x128.png', 
                'icons/media_record_16x16.png', 
                'icons/media_record_22x22.png', 
                'icons/media_record_24x24.png', 
                'icons/media_record_32x32.png', 
                'icons/media_record_48x48.png', 
                'icons/media_record_72x72.png', 
                'icons/media_seek_backward_128x128.png', 
                'icons/media_seek_backward_16x16.png', 
                'icons/media_seek_backward_22x22.png', 
                'icons/media_seek_backward_24x24.png', 
                'icons/media_seek_backward_32x32.png', 
                'icons/media_seek_backward_48x48.png', 
                'icons/media_seek_backward_72x72.png', 
                'icons/media_seek_forward_128x128.png', 
                'icons/media_seek_forward_16x16.png',
                'icons/media_seek_forward_22x22.png',
                'icons/media_seek_forward_24x24.png',
                'icons/media_seek_forward_32x32.png',
                'icons/media_seek_forward_48x48.png',
                'icons/media_seek_forward_72x72.png',
                'icons/media_skip_backward_128x128.png',
                'icons/media_skip_backward_16x16.png',
                'icons/media_skip_backward_22x22.png',
                'icons/media_skip_backward_24x24.png',
                'icons/media_skip_backward_32x32.png',
                'icons/media_skip_backward_48x48.png',
                'icons/media_skip_backward_72x72.png',
                'icons/media_skip_forward_128x128.png',
                'icons/media_skip_forward_16x16.png',
                'icons/media_skip_forward_22x22.png',
                'icons/media_skip_forward_24x24.png',
                'icons/media_skip_forward_32x32.png',
                'icons/media_skip_forward_48x48.png',
                'icons/media_skip_forward_72x72.png',
                'icons/application_connected_128x128.png',
                'icons/application_connected_16x16.png',
                'icons/application_connected_22x22.png',
                'icons/application_connected_24x24.png',
                'icons/application_connected_32x32.png',
                'icons/application_connected_48x48.png',
                'icons/application_connected_72x72.png',
                'icons/application_disconected_128x128.png',
                'icons/application_disconected_16x16.png',
                'icons/application_disconected_22x22.png',
                'icons/application_disconected_24x24.png',
                'icons/application_disconected_32x32.png',
                'icons/application_disconected_48x48.png',
                'icons/application_disconected_72x72.png',
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
