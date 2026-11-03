# Ansible role: Cockpit

Install Cockpit on Fedora/RHEL-family and Debian/Ubuntu systems, with explicit
listener, plugin, metrics, and firewall configuration. Requires Ansible Core
2.15+ and `ansible.posix` (see `requirements.yml`). MIT licensed.

## Safe defaults

- Listen only on **127.0.0.1:9090**, not all IPv4/IPv6 interfaces.
- Do not add firewall permissions automatically.
- Disallow root login through Cockpit.
- Install packages with `state: present`, not a blanket upgrade.
- Do not install/start PCP history collection unless requested.
- Use distribution repositories; Debian backports are opt-in and never used on Ubuntu.

**These listener/firewall/metrics defaults differ from earlier revisions.**
Upgrade deliberately: existing web sessions may be disconnected when the socket
is reconfigured. Existing firewall rules, metrics packages/services, old backports
repositories, and unrelated drop-ins are not automatically removed. Review them
separately. `cockpit_config` must now be a mapping (`{}`), not a list (`[]`).

## Use

```yaml
- name: Configure the web console
  hosts: servers
  become: true
  roles:
    - role: quiquecmtt.cockpit
      vars:
        cockpit_plugins:
          - cockpit-podman
        cockpit_disallowed_users:
          - containers
```

For loopback-only access, tunnel over SSH:

```sh
ssh -N -L 9090:127.0.0.1:9090 user@server
```

Browse to `https://localhost:9090`. The default self-signed certificate is not
automatically trusted by the tunnel; verify it or provision a trusted certificate.
Login uses your host credentials. This role does not create users or change
their SSH/sudo policy. Cockpit is administrative software, not a read-only dashboard.

## Variables

See `defaults/main.yml` for the complete defaults.

| Variable | Default | Purpose |
| --- | --- | --- |
| `cockpit_packages` | `[cockpit]` | Base distro packages |
| `cockpit_plugins` | `[]` | Additional packages such as `cockpit-podman` |
| `cockpit_pkg_state` | `present` | `present` or `latest` |
| `cockpit_listen_streams` | `[127.0.0.1:9090]` | systemd TCP socket endpoints |
| `cockpit_manage_firewall` | `false` | Opt in to a firewalld service rule |
| `cockpit_firewall_zone` | empty | Required explicit zone when managing firewalld |
| `cockpit_metrics_enabled` | `false` | Install PCP packages and start pmcd/pmlogger |
| `cockpit_metrics_packages` | pcp, python3-pcp | Override for distro requirements |
| `cockpit_debian_backports` | `false` | Opt-in Debian-only repository and package selection |
| `cockpit_allow_root_login` | `false` | Permit root web login |
| `cockpit_disallowed_users` | `[]` | Other accounts blocked from web login |
| `cockpit_config_dir` | `/etc/cockpit` | Cockpit config directory |
| `cockpit_config` | `{}` | INI section-to-option mapping |

The role owns `cockpit.conf`, `disallowed-users`, and
`/etc/systemd/system/cockpit.socket.d/50-ansible-listen.conf`. The socket drop-in
clears the vendor `ListenStream` list before setting explicit listeners. Later
local drop-ins can override it: verify the actual listening addresses after deployment.
Other drop-ins are preserved. Ports other than 9090 may require separate SELinux
policy configuration; this role does not disable SELinux or manage port labels.

Example configuration:

```yaml
cockpit_config:
  Session:
    IdleTimeout: 15
```

Socket activation means `cockpit.socket` should be active/enabled, while
`cockpit.service` can legitimately be inactive when idle. Configuration changes
stop the worker so the next connection loads the new settings.

`cockpit-podman` uses the Podman API. This role only installs its package; the
workload owner's Unix socket and account policy belong to the Podman role.
No Podman TCP endpoint is created. Cross-user visibility depends on the installed
Cockpit Podman version and administrative permissions; inactive other-user
Quadlets have upstream limitations.

Fedora 44 no longer ships the separate `cockpit-pcp` package. Older Cockpit builds
that need it for the history UI can add it to `cockpit_plugins` or override
`cockpit_metrics_packages`; PCP collection itself is controlled by the metrics flag.

## Development and tests

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
ansible-galaxy collection install -r requirements.yml
ansible-lint
python -m unittest discover -s tests -v
MOLECULE_DISTRO=fedora44 molecule test
```

Molecule needs Docker with systemd-capable privileged test containers. CI tests
Fedora 44, Rocky Linux 9, Debian 12/13, and Ubuntu 22.04/24.04; it exercises optional
metrics on Fedora and backports on Debian 13. `molecule test` includes idempotency,
actual socket binding, HTTPS activation, and root-login policy checks.
