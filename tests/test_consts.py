import sys
import types
import json
import importlib
from pathlib import Path
 
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


class MockSettings:
    def __init__(self, data):
        self._data = data or {}

    def get(self, key):
        return self._data.get(key)

    def add_on_change(self, *_args, **_kwargs):
        pass


def make_sublime(user_settings, default_settings):
    m = types.ModuleType("sublime")

    def load_resource(_path):
        return json.dumps(default_settings or {})

    def decode_value(s):
        return json.loads(s)

    def load_settings(_name):
        return MockSettings(user_settings or {})

    m.load_resource = load_resource
    m.decode_value = decode_value
    m.load_settings = load_settings
    return m


def import_consts(mock_sublime):
    sys.modules["sublime"] = mock_sublime
    sys.modules["sublime_plugin"] = types.ModuleType("sublime_plugin")
    if "Common.Consts" in sys.modules:
        importlib.reload(sys.modules["Common.Consts"])
    else:
        import Common.Consts  # noqa: F401
    return sys.modules["Common.Consts"]


def run_case(user_settings, default_settings, checks):
    consts = import_consts(make_sublime(user_settings, default_settings))
    loader = consts._ConfigLoader()
    for key, default, expected in checks:
        assert loader.get(key, default) == expected


def main():
    run_case(
        {"plugin": {"debug": True}},
        {"plugin": {"timeout": 5, "debug": False}},
        [
            ("plugin.timeout", 10, 5),
            ("plugin.debug", False, True),
        ],
    )

    run_case(
        {"plugin": {}},
        {"plugin": {"timeout": 5}},
        [
            ("plugin.timeout", 10, 5),
            ("plugin.debug", False, False),
        ],
    )

    run_case(
        {},
        {},
        [
            ("missing.key", 42, 42),
        ],
    )

    run_case(
        {"plugin": {"timeout": 1}},
        {"plugin": {"timeout": 5}},
        [
            ("plugin", {}, {"timeout": 1}),
        ],
    )

    run_case(
        {"lmrl": {"remote": {"http_base": "https://example"}}},
        {"lmrl": {"remote": {"fetch_sermon_list": "default_url"}}},
        [
            ("lmrl.remote.http_base", "y", "https://example"),
            ("lmrl.remote.fetch_sermon_list", "x", "default_url"),
        ],
    )


if __name__ == "__main__":
    main()
