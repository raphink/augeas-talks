.. include:: <s5defs.txt>

===================================
 Configuration surgery with Augeas
===================================

:Author: Raphaël Pinson
:Twitter: @raphink
:Event: LSM 2012, Geneva
:Date: 2012-07-11
:Source: https://github.com/raphink/augeas-talks/

.. slide-design:: Default 1

Tired of ugly **sed** and **awk** one liners?
----------------------------------------------

.. class:: center large


or of using *tons* of different
parsing libraries
or **common::line** tricks?

.. class:: handout

  * Several approaches to configuration management
    - provide the whole file: templa => often ugly
    - in-place replacement : sed/awk
  * Augeas provides a unified API


Become a configuration surgeon with
------------------------------------

  
.. image:: img/augeas-logo-simple.png
   :align: center
         
.. class:: center huge
        
 Augeas

.. class:: handout

  RedHat emerging project, but usable on most Unix systems

What is the need?
-----------------

* A lot of different syntaxes

* Securely editing configuration files with a unified API

.. class:: handout

  * fstab, hosts, sudoers, ntp...
  * tons of different parsers

A tree
--------

Augeas turns configuration files into a tree structure:

.. class:: small
.. code-block:: augtool-shell

 /etc/hosts -> /files/etc/hosts


.. class:: handout

  It is based on studies that aimed to provide mapping
  between XML and native formats


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

.. class:: handout

  * Each node can have one optional value, as well as one or more children
  * There are two root nodes: /augeas and /files (more in version to come)


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


.. class:: handout

  Most basic formats are provided in Augeas
  We encourage projects to make their own lenses
  and provide them with their code (case of e.g. nut)


... as well as generic lenses
-----------------------------

available to build new parsers:

.. class:: small
.. code-block:: bash

 Build          Sep                     Simplelines
 IniFile        Shellvars               Simplevars
 Rx             Shellvars_list          Util

.. class:: handout

  As more and more lenses were written, we saw patterns
  and common needs. These lenses provide generic constructs.


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


.. class:: handout

  It is often recommended to prototype with augtool
  before writing puppet/ruby/perl/whatever code
  as augtool make it much easier.

  You can however also use augtool in shell, 
  or even as an interpreter (with a shebang)


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


.. class:: handout

  It's not really standard XPath, but really inspired.


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


.. class:: handout

  You can modify a single parameter without affecting the rest
  of the file, such as spaces, indentations, comments...

  Hence the idea that augeas is kind of a 'surgeon' tool



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

.. class:: handout

  Often quite slow unless you use "context".

  There is a "onlyif" parameter, but it's hardly ever useful anymore
  since the provider does automatic idempotent changes.
  
  In the new version of Puppet, it will be faster by using context
  to restrict the lenses/files loaded.


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


.. class:: handout

  Users usually don't want to use touch Augeas.

  Keep it deep in the code (ideally, as we'll see, in native providers)
  by wrapping it in definitions.


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

.. class:: handout

  Allows to query augeas with match statements.

  Can be useful to test for existing users, parameters,
  mount points, etc. without writing a custom fact.


... and uses it for discovery
------------------------------

.. class:: small
.. code-block:: bash

 $ mco find -S "augeas_match(/files/etc/passwd/rip).size = 0"
    
.. class:: handout

  Augeas used as a plugin for discovery.

  Allows to filter nodes on Augeas conditions (users, mount points, etc.)


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

.. class:: handout

  I'll only show ruby examples, since this is a Puppetcamp,
  but e.g. Augeas::Validator is written in Perl.


The Ruby bindings can be used in Facter
----------------------------------------

.. class:: small
.. code-block:: ruby

 Facter.add(:augeasversion) do
   setcode do
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

.. class:: handout

  Easy to prototype with mcollective now.
  

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


.. class:: handout

  Dominic Cleal, creator of the Augeas provider for Puppet,
  started this augeasproviders project (on github) to rewrite
  native providers using Augeas as a parsing library.

  I really think this is the best way to use Augeas in Puppet.
 
  I will give a full example of a provider using Augeas next.


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
      conditions.each { |k,v| cond_str += "[Condition/#{k}=\"#{v}\"]" }
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


.. class:: handout

  The ``//`` stands for "any sublevel" (XPath).


Other projects using Augeas
----------------------------

.. class:: incremental

* libvirt
* rpm
* Nut
* guestfs
* ZYpp
* Config::Model
* Augeas::Validator


Future projects
----------------

.. class:: incremental

* more API calls
* improved XPath syntax
* more lenses
* more native providers
* DBUS provider
* content validation in Puppet (validator)
* integration in package managers
* finish the Augeas book
* ...
* your idea/project here...

.. class:: handout

 * API calls: store/retrieve
 * XPath syntax: case insensitive


Questions?
----------

.. class:: center

 http://augeas.net

 augeas-devel@redhat.com

 freenode: #augeas


.. slide-design:: Default 2

--------------

.. that's all folks!


