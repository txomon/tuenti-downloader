Tuenti downloader
=================

This is a really easy to use tool, just python setup.py install it, be sure to
have your user and password and execute it like `td user_email user_password`

Easy install steps, that will allow you to make changes to the code without
having to do anything else.

Steps to use
------------

 * Install:
   * virtualenv (python2-virtualenv)
   * git (git)
   * optionally libgexiv2 (libgexiv2 in archlinux)
 * Create a folder (mkdir tuenti) and get into it (cd tuenti)
 * Clone like git clone https://github.com/txomon/tuenti-downloader
 * Create virtualenv (virtualenv2 ve or virtualenv ve depending on default)
 * Activate virtualenv (source ve/bin/activate)
 * Remove global package lock (rm ve/lib/python2.7/no-global-site-packages.txt)
 * Get in tuenti-downloader (cd tuenti-downloader)
 * Install it (python setup.py develop)
 * Go one up (cd ..)
 * Use it (td user_name user_password)

To update
---------

 * Get in tuenti/tuenti-downloader
 * Update it with git pull
 * Go one up (cd ..)
 * Use it (td user_name user_password)


Support
=======

I have opened this chat room https://gitter.im/txomon/tuenti-downloader just
in case you want to ask something, as I prefer that to being privately asked.

TODO
====

If you want to contribute, there are some ideas on the TODO file

Disclaimer
==========

I release this because I have been able to backup all my photos with it and
it has been developed using other open source. I firmly believe that you
shouldn't hack into it any more but to polish a little the algorithm because
you could really end up scrapping all Tuenti.

The filter at the moment works by scraping all your albums, seeing who has
talked there and scrapping them looking for photos where you have been tagged
or commented.

The API I was able to find didn't implement anything else to create more logic,
so it's up to you.

Don't do evil
