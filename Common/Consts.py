import sublime
import sublime_plugin

class _ConfigLoader:
    def __init__(self):
        self.settings = None
        self.default_settings = None
        self._load_settings()

    def _load_settings(self):
        # 加载默认配置
        default_settings_path = "Packages/lmrl-plugin/lmrl-plugin.sublime-settings"
        self.default_settings = sublime.load_resource(default_settings_path)  # 读取文件内容
        self.default_settings = sublime.decode_value(self.default_settings)   # 转为字典
        # 加载用户配置
        self.settings = sublime.load_settings("lmrl-plugin.sublime-settings")
        self.settings.add_on_change("lmrl_config_onchange", self._on_config_change)

    def _on_config_change(self):
        """配置文件变更时重新加载"""
        self.settings = sublime.load_settings("lmrl-plugin.sublime-settings")

    def _get_nested(self, root, keys):
        cur = root
        for k in keys:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return None
        return cur

    def get(self, key, default=None):
        """支持嵌套键（如 'plugin.timeout'）"""
        keys = key.split('.')
        user_root = self.settings.get(keys[0])
        default_root = self.default_settings.get(keys[0])

        if len(keys) == 1:
            value = user_root if user_root is not None else default_root
        else:
            user_value = self._get_nested(user_root, keys[1:])
            value = user_value if user_value is not None else self._get_nested(default_root, keys[1:])

        return value if value is not None else default

# 单例配置加载器
_config = _ConfigLoader()

# 对外暴露的常量（动态读取嵌套配置）
TIMEOUT = property(lambda: _config.get("plugin.timeout", 10))  # 默认值10
DEBUG = property(lambda: _config.get("plugin.debug", False))


# 定义常量

# bible engine
LMRL_BIBLE_ENGINE = property(lambda: _config.get("lmrl.bible.engine", "cmd"))
# remote
LMRL_HTTP_BASE = property(lambda: _config.get("lmrl.remote.http_base", "http://localhost:3001"))
LMRL_FETCH_SERMON_LIST_URL = property(lambda: _config.get("lmrl.remote.fetch_sermon_list", "lmrl/api/sermons")) 

#local
LMRL_LOCAL_BASE_PATH = property(lambda: _config.get("lmrl.local.mp3_base_path", "~/doc/基督/灵命日粮"))
# bible_search_cmd
LMRL_BIBLE_SEARCH_CMD = property(lambda: _config.get("lmrl.local.bible_search_cmd", "~/.go/current/gopath/bin/biblego"))
