.. include:: <s5defs.txt>

===================================
 Configuration surgery with Augeas
===================================

:Author: Raphaël Pinson
:Event: LSM 2012, Geneva
:Date: 2012-07-11

.. slide-design:: Default 1

Tired of ugly **sed** and **awk** one liners?
----------------------------------------------

.. class:: center large


or of using *tons* of different
parsing libraries
or **common::line** tricks?

.. class:: handout

  Everything that is in this block will only be in the notes.
    You can put these on each slide.



Become a configuration surgeon with
------------------------------------

  
.. image:: img/augeas-logo-simple.png
   :align: center
         
.. class:: center huge
        
 Augeas


What is the need?
-----------------

A lot of different syntaxes

Securely editing configuration files with a unified API


A tree
--------

Augeas turns configuration files into a tree structure:

.. class:: small
.. code-block:: augtool-shell

 /etc/hosts -> /files/etc/hosts


Its branches and leaves
------------------------

... and their parameters into branches and leaves:


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


... and uses it for discovery
------------------------------

.. class:: small
.. code-block:: bash

 $ mco find -S "augeas_match(/files/etc/passwd/rip).size = 0"
    

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


Or to write native types
-------------------------

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


The case of sshd_config
------------------------

Custom type:

.. class:: small
.. code-block:: puppet

  define ssh::config::sshd ($ensure='present', $value='') {

    case $ensure {
      'present': { $changes = "set ${name} ${value}" }

      'absent': { $changes = "rm ${name}" }

      'default': { fail("Wrong value for ensure: ${ensure}") }
    }

    augeas {"Set ${name} in /etc/ssh/sshd_config":
      context => '/files/etc/ssh/sshd_config',
      changes => $changes,
    }
  }

Using the custom type for sshd_config
--------------------------------------

.. class:: small
.. code-block:: puppet

    ssh::config::sshd {'PasswordAuthenticator':
      value => 'yes',
    }


The problem with sshd_config
-----------------------------

Match groups:

.. class:: small
.. code-block:: bash

  Match Host example.com
    PermitRootLogin no

=> Not possible with ``ssh::config::sshd``, requires insertions and looping through the configuration parameters.


A native provider for sshd_config (1)
--------------------------------------

The type:

.. class:: tiny
.. code-block:: ruby

  Puppet::Type.newtype(:sshd_config) do
    ensurable
  
    newparam(:name) do
      desc "The name of the entry."
      isnamevar
    end
  
    newproperty(:value) do
      desc "Entry value."
    end
  
    newproperty(:target) do
      desc "File target."
    end
  
    newparam(:condition) do
      desc "Match group condition for the entry."
    end
  end


A native provider for sshd_config (2)
--------------------------------------

The provider:

.. class:: tiny
.. code-block:: ruby

  require 'augeas' if Puppet.features.augeas?
  
  Puppet::Type.type(:sshd_config).provide(:augeas) do
    desc "Uses Augeas API to update an sshd_config parameter"
  
    def self.file(resource = nil)
      file = "/etc/ssh/sshd_config"
      file = resource[:target] if resource and resource[:target]
      file.chomp("/")
    end
  
    confine :true   => Puppet.features.augeas? 
    confine :exists => file

A native provider for sshd_config (3)
--------------------------------------

.. class:: tiny
.. code-block:: ruby

  def self.augopen(resource = nil)
    aug = nil
    file = file(resource)
    begin
      aug = Augeas.open(nil, nil, Augeas::NO_MODL_AUTOLOAD)
      aug.transform(
        :lens => "Sshd.lns",
        :name => "Sshd",
        :incl => file
      )
      aug.load!

      if aug.match("/files#{file}").empty?
        message = aug.get("/augeas/files#{file}/error/message")
        fail("Augeas didn't load #{file}: #{message}")
      end
    rescue
      aug.close if aug
      raise
    end
    aug
  end


A native provider for sshd_config (4)
--------------------------------------

.. class:: tiny
.. code-block:: ruby

  def self.instances
    aug = nil
    path = "/files#{file}"
    entry_path = self.class.entry_path(resource)
    begin
      resources = []
      aug = augopen
      aug.match(entry_path).each do |hpath|
        entry = {}
        entry[:name] = resource[:name]
        entry[:conditions] = Hash[*resource[:condition].split(' ').flatten(1)]
        entry[:value] = aug.get(hpath)

        resources << new(entry)
      end
      resources
    ensure
      aug.close if aug
    end
  end
.. ** relax, vim

A native provider for sshd_config (5)
--------------------------------------

.. class:: tiny
.. code-block:: ruby

  def self.match_conditions(resource=nil)
    if resource[:condition]
      conditions = Hash[*resource[:condition].split(' ').flatten(1)]
      cond_keys = conditions.keys.length
      cond_str = "[count(Condition/*)=#{cond_keys}]"
      conditions.each do |k,v|
        cond_str += "[Condition/#{k}=\"#{v}\"]"
      end
      cond_str
    else
      ""
    end
  end

  def self.entry_path(resource=nil)
    path = "/files#{self.file(resource)}"
    if resource[:condition]
      cond_str = self.match_conditions(resource)
      "#{path}/Match#{cond_str}/Settings/#{resource[:name]}"
    else
      "#{path}/#{resource[:name]}"
    end
  end


A native provider for sshd_config (6)
--------------------------------------

.. class:: tiny
.. code-block:: ruby

  def self.match_exists?(resource=nil)
    aug = nil
    path = "/files#{self.file(resource)}"
    begin
      aug = self.augopen(resource)
      if resource[:condition]
        cond_str = self.match_conditions(resource)
      else
        false
      end
      not aug.match("#{path}/Match#{cond_str}").empty?
    ensure
      aug.close if aug
    end
  end

A native provider for sshd_config (7)
--------------------------------------

.. class:: tiny
.. code-block:: ruby

  def exists? 
    aug = nil
    entry_path = self.class.entry_path(resource)
    begin
      aug = self.class.augopen(resource)
      not aug.match(entry_path).empty?
    ensure
      aug.close if aug
    end
  end

  def self.create_match(resource=nil, aug=nil)
    path = "/files#{self.file(resource)}"
    begin
      aug.insert("#{path}/*[last()]", "Match", false)
      conditions = Hash[*resource[:condition].split(' ').flatten(1)]
      conditions.each do |k,v|
        aug.set("#{path}/Match[last()]/Condition/#{k}", v)
      end
      aug
    end
  end
.. ** relax, vim

A native provider for sshd_config (8)
--------------------------------------

.. class:: tiny
.. code-block:: ruby

  def create 
    aug = nil
    path = "/files#{self.class.file(resource)}"
    entry_path = self.class.entry_path(resource)
    begin
      aug = self.class.augopen(resource)
      if resource[:condition] 
        unless self.class.match_exists?(resource)
          aug = self.class.create_match(resource, aug)
        end
      else
        unless aug.match("#{path}/Match").empty?
          aug.insert("#{path}/Match[1]", resource[:name], true)
        end
      end
      aug.set(entry_path, resource[:value])
      aug.save!
    ensure
      aug.close if aug
    end
  end

A native provider for sshd_config (9)
--------------------------------------

.. class:: tiny
.. code-block:: ruby

  def destroy
    aug = nil
    path = "/files#{self.class.file(resource)}"
    begin
      aug = self.class.augopen(resource)
      entry_path = self.class.entry_path(resource)
      aug.rm(entry_path)
      aug.rm("#{path}/Match[count(Settings/*)=0]")
      aug.save!
    ensure
      aug.close if aug
    end
  end

  def target
    self.class.file(resource)
  end
.. ** relax, vim

A native provider for sshd_config (10)
--------------------------------------

.. class:: tiny
.. code-block:: ruby

  def value
    aug = nil
    path = "/files#{self.class.file(resource)}"
    begin
      aug = self.class.augopen(resource)
      entry_path = self.class.entry_path(resource)
      aug.get(entry_path)
    ensure
      aug.close if aug
    end
  end

A native provider for sshd_config (11)
--------------------------------------

.. class:: tiny
.. code-block:: ruby

  def value=(thevalue)
    aug = nil
    path = "/files#{self.class.file(resource)}"
    begin
      aug = self.class.augopen(resource)
      entry_path = self.class.entry_path(resource)
      aug.set(entry_path, thevalue)
      aug.save!
    ensure
      aug.close if aug
    end
  end


Using the native provider for sshd_config
------------------------------------------

.. class:: small
.. code-block:: puppet

  sshd_config {'PermitRootLogin':
    ensure    => present,
    condition => 'Host example.com',
    value     => 'yes',
  }

Errors are reported in the ``/augeas`` tree
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
* rpm
* Nut
* guestfs
* ZYpp
* Augeas-validator


Future projects
----------------

.. class:: incremental

* more native providers
* DBUS provider
* content validation in Puppet (validator)
* integration in package managers
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


