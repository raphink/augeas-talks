.. include:: <s5defs.txt>

===================================
 Configuration surgery with Augeas
===================================

:Author: Raphaël Pinson
:Event: LSM 2012, Geneva
:Date: 2012-07-11

-----------

.. class:: center large

Are you tired of ugly
``sed`` and ``awk`` one liners?


-----------

.. class:: center large

or of using *tons* of different
parsing libraries
or ``common::line`` tricks?


-----------

.. class:: center large

Become a configuration surgeon with

.. class:: huge

Augeas


The tree
--------

Augeas turns configuration files into a tree structure


.. code-block:: augtool-shell

 /etc/hosts -> /files/etc/hosts


...


The tree can be queried using ``XPath``
----------------------------------------

.. class:: small
.. code-block:: augtool-shell

 augtool> print /files/etc/passwd/*[uid='0'][1]
  /files/etc/passwd/root
  /files/etc/passwd/root/password = "x"
  /files/etc/passwd/root/uid = "0"
  /files/etc/passwd/root/gid = "0"
  /files/etc/passwd/root/name = "root"
  /files/etc/passwd/root/home = "/root"
  /files/etc/passwd/root/shell = "/bin/bash"


But also *modified*
-------------------

.. class:: small
.. code-block:: sh

 $ getent passwd root
 root:x:0:0:root:/root:/bin/bash

.. class:: small
.. code-block:: augtool-shell

 $ augtool
 augtool> set /files/etc/passwd/*[uid='0']/shell /bin/sh
 augtool> match /files/etc/passwd/*[uid='0']/shell
 /files/etc/passwd/root/shell = "/bin/sh"
 augtool> save
 Saved 1 file(s)
 augtool> exit

.. class:: small
.. code-block:: sh

 $ getent passwd root
 root:x:0:0:root:/root:/bin/sh




