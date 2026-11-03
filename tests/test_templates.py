"""Offline tests of actual role defaults and rendered configuration."""

import unittest
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent.parent


class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.defaults = yaml.safe_load((ROOT / "defaults/main.yml").read_text())
        self.environment = Environment(
            loader=FileSystemLoader(ROOT / "templates"),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            trim_blocks=True,
        )

    def render(self, name, **overrides):
        return self.environment.get_template(name).render(
            {**self.defaults, "ansible_managed": "Managed by Ansible", **overrides}
        )

    def test_safe_defaults(self):
        self.assertFalse(self.defaults["cockpit_manage_firewall"])
        self.assertFalse(self.defaults["cockpit_metrics_enabled"])
        self.assertFalse(self.defaults["cockpit_allow_root_login"])
        self.assertFalse(self.defaults["cockpit_debian_backports"])
        self.assertEqual(self.defaults["cockpit_config"], {})

    def test_socket_resets_wildcard_before_binding_loopback(self):
        rendered = self.render("cockpit.socket.conf.j2")
        self.assertIn("ListenStream=\nListenStream=127.0.0.1:9090", rendered)
        self.assertNotIn("0.0.0.0", rendered)
        self.assertNotIn("[::]", rendered)

    def test_multiple_explicit_listeners(self):
        rendered = self.render("cockpit.socket.conf.j2", cockpit_listen_streams=["127.0.0.1:9090", "[::1]:9090"])
        self.assertIn("ListenStream=[::1]:9090", rendered)

    def test_configuration_mapping_and_booleans(self):
        rendered = self.render("cockpit.conf.j2", cockpit_config={"WebService": {"AllowUnencrypted": False}})
        self.assertIn("[WebService]\nAllowUnencrypted=false", rendered)

    def test_disallowed_users(self):
        rendered = self.render("disallowed-users.j2", cockpit_disallowed_users=["containers"])
        self.assertIn("root", rendered.splitlines())
        self.assertIn("containers", rendered.splitlines())


if __name__ == "__main__":
    unittest.main()
