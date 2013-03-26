===============================
montigny-tt.info install script
===============================

`montigny-tt.info <http://montigny-tt.info>`_ web site is powered 
by `Wordpress <http://wordpress.org/>`_.


Fabric installation
===================

Install Python dependencies (`fabric <http://docs.fabfile.org/>`_…) with *buildout* :

.. code-block:: sh

    $ python bootstrap.py
    $ bin/buildout


Vagrant installation
====================

Prerequisites
-------------

On Ubuntu 12.10
~~~~~~~~~~~~~~~

.. code-block:: sh

    $ sudo apt-get install virtualbox rubygem1.8


Install `vagrant-hostmaster <https://github.com/mosaicxm/vagrant-hostmaster>`_ :

.. code-block:: sh

    $ vagrant gem install vagrant-hostmaster


Create VM with Vagrant
----------------------

Download and start *vagrant* VM :

.. code-block:: sh

    $ vagrant up


You can test *ping* command on hostname configured by *vagrant-hostmaster* :

.. code-block:: sh

    $ ping beta.montigny-tt.info
    PING beta.montigny-tt.info (192.168.33.10): 56 data bytes
    64 bytes from 192.168.33.10: icmp_seq=0 ttl=64 time=0.383 ms
    64 bytes from 192.168.33.10: icmp_seq=1 ttl=64 time=0.462 ms


Execute *fabric* install :

.. code-block:: sh

    $ bin/fab vagrant install


Show index forum page :

.. code-block:: sh

    $ curl -s http://beta.montigny-tt.info | grep "<title>"
    <title>Montigny les Metz - Tennis de Table | Un site utilisant WordPress</title>

