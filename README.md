Role Name
=========

Ansible role to install Cockpit and related packages in RHEL and Debian based distributions.

Requirements
------------

Modules used are from `ansible.builtin` and `ansible.posix`.

Role Variables
--------------

Currently, the default variables are:
```yaml
# defaults file for ansible-role-cockpit
cockpit_packages:     # Packages being installed
  - cockpit           # Main cockpit package
  - cockpit-storaged  # Installed automatically in Debian and Ubuntu, manually installed en RHEL based
  - udisks2-lvm2      # Needed for managing LVM through Cockpit
  - pcp               # Needed for performance metrics
  - python3-pcp       # Needed for performance metrics

cockpit_allow_root_login: false # Allow root login through Cockpit Web UI

cockpit_config_dir: /etc/cockpit # Cockpit configuration directory

cockpit_config: [] # Cockpit configuration variables

cockpit_disallowed_users: [] # Server users other than root that shouldn't be allowed to login

cockpit_plugins: [] # Extra cockpit plugins you want to install through distro's package manager
```

An example for the `cockpit_config` could be the following:
```yaml
cockpit_config:
  WebService: # This level is the section
    Origins: 'https://example.com https://example.org' # This level is the key=value
    ProtocolHeader: 'X-Forwarded-Proto'
  Session:
    IdleTimeout: 0
```

This would result in the following INI file:
```toml
[WebService]
Origins=https://example.com https://example.org
ProtocolHeader=X-Forwarded-Proto

[Session]
IdleTimeout=0
```
For further information in Cockpit configuration file, you can enter the following [link](https://cockpit-project.org/guide/latest/cockpit.conf.5).

Dependencies
------------

You shouldn't need any variable change, unless you want to change the configuration. Here is an example you may want for using in your inventory.

```yaml
cockpit_allow_root_login: true

cockpit_disallowed_users:
  - juan
  - pepe
  - moni
  - paola

cockpit_config:
  WebService:
    Origins: 'https://example.com https://example.org'
    ProtocolHeader: 'X-Forwarded-Proto'
  Session:
    IdleTimeout: 0
```

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: quiquecmtt.cockpit }

License
-------

BSD

Author Information
------------------

Enrique Cametti
GitHub: https://github.com/quiquecmtt