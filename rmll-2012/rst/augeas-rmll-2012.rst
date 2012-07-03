.. include:: <s5defs.txt>

===================================
 Configuration surgery with Augeas
===================================

:Author: Raphaël Pinson
:Event: LSM 2012, Geneva
:Date: 2012-07-11

.. slide-design:: Default 1

-----------

.. class:: center large

Are you tired of ugly
``sed`` and ``awk`` one liners?

or of using *tons* of different
parsing libraries
or ``common::line`` tricks?


-----------

.. class:: center large

Become a configuration surgeon with

.. class:: huge

Augeas

.. image:: img/augeas-logo-simple.png
   :align: right


A tree
--------

Augeas turns configuration files into a tree structure

.. class:: small
.. code-block:: augtool-shell

 /etc/hosts -> /files/etc/hosts


Its branches and leaves
------------------------

... and their parameters into branches and leaves


.. class:: small
.. code-block:: augtool-shell

 augtool> print /files/etc/hosts
   /files/etc/hosts
   /files/etc/hosts/1
   /files/etc/hosts/1/ipaddr = "127.0.0.1"
   /files/etc/hosts/1/canonical = "localhost"


Augeas provides many stock parsers
----------------------------------

They are called *lenses*:

.. class:: small
.. code-block:: bash

 Access          Cron            Host_Conf
 Aliases         Crypttab        Hostname
 Anacron         debctrl         Hosts_Access
 Approx          Desktop         IniFile
 AptConf         Dhcpd           Inputrc
 Automaster      Dpkg            Iptables
 Automounter     Exports         Kdump
 BackupPCHosts   FAI_DiskConfig  Keepalived
 cgconfig        Fonts           Keepalived
 cgrules         Fuse            Login_defs
 Channels        Grub            Mke2fs
 ...


... as well as generic lenses
-----------------------------

available to build new parsers:

.. class:: small
.. code-block:: bash

 Build          Sep                     Simplelines
 IniFile        Shellvars               Simplevars
 Rx             Shellvars_list          Util


``augtool`` lets you inspect the tree
--------------------------------------

.. class:: small
.. code-block:: bash

 $ augtool

.. class:: small
.. code-block:: augtool-shell

 augtool> ls /
  augeas/ = (none)
  files/ = (none)

.. class:: small
.. code-block:: augtool-shell
 
 augtool> print /files/etc/passwd/root/
  /files/etc/passwd/root
  /files/etc/passwd/root/password = "x"
  /files/etc/passwd/root/uid = "0"
  /files/etc/passwd/root/gid = "0"
  /files/etc/passwd/root/name = "root"
  /files/etc/passwd/root/home = "/root"
  /files/etc/passwd/root/shell = "/bin/bash"


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
.. ** Relax, vim


But also *modified*
-------------------

.. class:: small
.. code-block:: sh

 $ getent passwd root
 root:x:0:0:root:/root:/bin/bash

 $ augtool
.. class:: small
.. code-block:: augtool-shell

 augtool> set /files/etc/passwd/*[uid='0']/shell /bin/sh
 augtool> match /files/etc/passwd/*[uid='0']/shell
 /files/etc/passwd/root/shell = "/bin/sh"
 augtool> save
 Saved 1 file(s)
 augtool> exit
.. ** Relax, vim


.. class:: small
.. code-block:: sh

 $ getent passwd root
 root:x:0:0:root:/root:/bin/sh



Puppet has a native provider
-----------------------------

.. class:: small
.. code-block:: puppet

 augeas {'export foo': 
     context => '/files/etc/exports',
     changes => [
         "set dir[. = '/foo'] /foo",
         "set dir[. = '/foo']/client weeble",
         "set dir[. = '/foo']/client/option[1] ro",
         "set dir[. = '/foo']/client/option[2] all_squash",
     ],
 } 


It is better to wrap things up
-------------------------------


.. class:: small
.. code-block:: puppet

 define kmod::generic(
   $type, $module, $ensure=present,
   $command='', $file='/etc/modprobe.d/modprobe.conf'
 ) {
   augeas {"${type} module ${module}":
     context => "/files${file}",
     changes => [
       "set ${type}[. = '${module}'] ${module}",
       "set ${type}[. = '${module}']/command '${command}'",
     ],
   }
 }

mcollective has an agent
-------------------------

.. class:: small
.. code-block:: bash

 $ mco augeas match /files/etc/passwd/rpinson/shell
 
  * [ ======================================> ] 196 / 196
 
 ...
 wrk1                                    
 saja-map-dev                            
     /files/etc/passwd/rpinson/shell = /bin/bash
 wrk3                                    
 wrk4                                    
     /files/etc/passwd/rpinson/shell = /bin/bash
 ...
    

Bindings include Perl, Python, Java, PHP, Haskell, Ruby...
-----------------------------------------------------------

.. class:: small
.. code-block:: ruby

 require 'augeas'
 aug = Augeas.open
 if aug.match('/augeas/load'+lens).length > 0
    aug.set('/augeas/load/'+lens+'incl[last()+1]', path)
 else
    aug.set('/augeas/load/'+lens+'/lens', lens+'.lns')
 end

.. class:: tiny center

 (From the mcollective agent)


The Ruby bindings can be used in Facter
----------------------------------------

.. class:: small
.. code-block:: ruby

 Facter.add(:augeasversion) do setcode do
     begin
       require 'augeas'
       aug = Augeas::open('/', nil, Augeas::NO_MODL_AUTOLOAD)
       ver = aug.get('/augeas/version')
       aug.close
       ver
     rescue Exception
       Facter.debug('ruby-augeas not available')
     end
   end
 end
    
.. class:: tiny center

 (From the augeasversion fact)


Or to write native types (recommended)
--------------------------------------

.. class:: small
.. code-block:: ruby

 def ip
     aug = nil
     path = "/files#{self.class.file(resource)}"
     begin
       aug = self.class.augopen(resource)
       aug.get("#{path}/*[canonical =
          '#{resource[:name]}']/ipaddr")
     ensure
       aug.close if aug
     end
   end
.. ** Relax, vim
    

.. class:: tiny center

 (See https://github.com/domcleal/augeasproviders)


Augeas reports its errors in the ``/augeas`` tree
--------------------------------------------------

.. class:: small
.. code-block:: augtool-shell

 augtool> print /augeas//error
  /augeas/files/etc/mke2fs.conf/error = "parse_failed"
  /augeas/files/etc/mke2fs.conf/error/pos = "82"
  /augeas/files/etc/mke2fs.conf/error/line = "3"
  /augeas/files/etc/mke2fs.conf/error/char = "0"
  /augeas/files/etc/mke2fs.conf/error/lens = \
     "/usr/share/augeas/lenses/dist/mke2fs.aug:132.10-.49:"
  /augeas/files/etc/mke2fs.conf/error/message = \
     "Get did not match entire input"


Other projects using Augeas
----------------------------

.. class:: incremental

* libvirt
* Nut
* guestfs
* ZYpp
* Augeas-validator


Future projects
----------------

.. class:: incremental

* better integration in Mcollective 2.0
* content validation in Puppet
* ...
* your idea/project here...


Questions?
----------

.. class:: center

 http://augeas.net

 augeas-devel@redhat.com

 freenode: #augeas


.. slide-design:: Default 2


--------------

.. that's all folks!


