squeezetray
===========

Cross platform Graphical User Interface client for the Logitech squeeze box server.

This application has been developed on debian with icewm and I have one report of soem one trying on ubuntu LTS.

Features
========

 * Supports as many squeezebox's as available.
 * Tray icon changes colour depending on state.
 * Multithreaded request queue.
 * Right click dynamic submenus on traybar.
 * Cross platform code base. (but only tested on Linux so far)
 
Depends on wxPython and a requires a Logitech Squeeze Box Server.

Controls the Logitech squeeze box, with basic commands from the system tray. Based upon wxpython


Getting the source
=============

Check the code out on the command line with:

    git clone git://github.com/osynge/squeezetray.git

Change into the right directory:

    cd squeezetray

Then run the program:
    
    python squeezetray

python squeezetray
==============

Installing squeezetray
================

First generate the icons as PNG from SVG using the following script

    #bin/bash
    sizes="16 22 24 32 48 72 128"
    basedirect="icons"
    for item in `ls icons/*.svg`
    do
       for size in $sizes
       do
           name=$(echo $item | sed -e 's/.*\///' | sed -e 's/\.svg.*$//')
           cmd="convert  -strip -background transparent  -resize ${size}x${size} $item  ${basedirect}/${name}_${size}x${size}.png"
           $cmd
       done
    done

NOw we can install the application.

    #python setup.py install
    /usr/lib/python2.7/distutils/dist.py:267: UserWarning: Unknown distribution option: 'install_requires'
      warnings.warn(msg)
    running install
    running build
    running build_py
    running build_scripts
    running install_lib
    creating /usr/local/lib/python2.7/dist-packages/sqtray
    copying build/lib.linux-x86_64-2.7/sqtray/__init__.py -> /usr/local/lib/python2.7/dist-packages/sqtray
    copying build/lib.linux-x86_64-2.7/sqtray/JrpcServer.py -> /usr/local/lib/python2.7/dist-packages/sqtray
    copying build/lib.linux-x86_64-2.7/sqtray/wxMainApp.py -> /usr/local/lib/python2.7/dist-packages/sqtray
    copying build/lib.linux-x86_64-2.7/sqtray/models.py -> /usr/local/lib/python2.7/dist-packages/sqtray
    copying build/lib.linux-x86_64-2.7/sqtray/__version__.py -> /usr/local/lib/python2.7/dist-packages/sqtray
    copying build/lib.linux-x86_64-2.7/sqtray/wxFrmSettings.py -> /usr/local/lib/python2.7/dist-packages/sqtray
    copying build/lib.linux-x86_64-2.7/sqtray/wxEvents.py -> /usr/local/lib/python2.7/dist-packages/sqtray
    copying build/lib.linux-x86_64-2.7/sqtray/wxTaskBarIcon.py -> /usr/local/lib/python2.7/dist-packages/sqtray
    byte-compiling /usr/local/lib/python2.7/dist-packages/sqtray/__init__.py to __init__.pyc
    byte-compiling /usr/local/lib/python2.7/dist-packages/sqtray/JrpcServer.py to JrpcServer.pyc
    byte-compiling /usr/local/lib/python2.7/dist-packages/sqtray/wxMainApp.py to wxMainApp.pyc
    byte-compiling /usr/local/lib/python2.7/dist-packages/sqtray/models.py to models.pyc
    byte-compiling /usr/local/lib/python2.7/dist-packages/sqtray/__version__.py to __version__.pyc
    byte-compiling /usr/local/lib/python2.7/dist-packages/sqtray/wxFrmSettings.py to wxFrmSettings.pyc
    byte-compiling /usr/local/lib/python2.7/dist-packages/sqtray/wxEvents.py to wxEvents.pyc
    byte-compiling /usr/local/lib/python2.7/dist-packages/sqtray/wxTaskBarIcon.py to wxTaskBarIcon.pyc
    running install_scripts
    copying build/scripts-2.7/squeezetray -> /usr/local/bin
    changing mode of /usr/local/bin/squeezetray to 755
    running install_data
    creating /usr/share/doc/hepixvmilsubscriber-0.0.1
    copying README.md -> /usr/share/doc/hepixvmilsubscriber-0.0.1
    copying LICENSE -> /usr/share/doc/hepixvmilsubscriber-0.0.1
    copying logger.conf -> /usr/share/doc/hepixvmilsubscriber-0.0.1
    copying ChangeLog -> /usr/share/doc/hepixvmilsubscriber-0.0.1
    running install_egg_info
    Writing /usr/local/lib/python2.7/dist-packages/SqueezeWxTray-0.0.1.egg-info







FAQ
===

Question: On Unity with wxpython2.8 and python 2.7.3 the tray icon does not show.

Answer: It seems on some versions of Ubunu tray icons are disabled, the following command line might help.

    $ gsettings set com.canonical.Unity.Panel systray-whitelist "['all']"

A Graphical discusion of this was found here:

    http://www.howtogeek.com/68119/how-to-bring-app-icons-back-into-unitys-system-tray/

Question: The application cannot find icons?

Answer: Sadly no good way exists in python to distribute data files and store thier path.

FOr thsi reason we are installing them in defiened directories that may change with platform.





code structure
==========


I changed the code to be more and more Model, View, Controller Pattern.

The model is updated from the server using json http, using a view as a thread pool.
Callbacks on changes to the model to the Controller can then trigger further things.

In this case another View is triggered to display the model as the StatusBar and Tooltip, 
which shows details about the current track playing, and server status.


Icons svg to png
================

for some reason svg is not yet well supportied in python for this reason all svg icons are cxonverted to png.

   convert  -background transparent  -resize 16x16 ${IMPUT}.svg  ${OUTPUT}.png

Or you can script it with a little bash

    #bin/bash
    sizes="16 22 24 32 48 72 128"
    basedirect="icons"
    for item in `ls icons/*.svg`
    do
       for size in $sizes
       do
           name=$(echo $item | sed -e 's/.*\///' | sed -e 's/\.svg.*$//')
           cmd="convert  -background transparent  -resize ${size}x${size} $item  ${basedirect}/${name}_${size}x${size}.png"
           $cmd
       done
    done


Building from Git
=================


First generate the icons as PNG from SVG using the following script

    #bin/bash
    sizes="16 22 24 32 48 72 128"
    basedirect="icons"
    for item in `ls icons/*.svg`
    do
       for size in $sizes
       do
           name=$(echo $item | sed -e 's/.*\///' | sed -e 's/\.svg.*$//')
           cmd="convert  -background transparent  -resize ${size}x${size} $item  ${basedirect}/${name}_${size}x${size}.png"
           $cmd
       done
    done
