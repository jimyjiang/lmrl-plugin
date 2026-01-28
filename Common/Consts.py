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

    def get(self, key, default=None):
        """支持嵌套键（如 'plugin.timeout'）"""
        keys = key.split('.')
        value = self.settings.get(keys[0]) or self.default_settings.get(keys[0])
        
        for k in keys[1:]:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default  # 路径不完整时返回默认值
        return value if value is not None else default

# 单例配置加载器
_config = _ConfigLoader()

# 对外暴露的常量（动态读取嵌套配置）
TIMEOUT = property(lambda: _config.get("plugin.timeout", 10))  # 默认值10
DEBUG = property(lambda: _config.get("plugin.debug", False))


# 定义常量

# 灵命日粮
# remote
LMRL_HTTP_BASE = property(lambda: _config.get("lmrl.remote.http_base", "http://localhost:3001"))
LMRL_FETCH_SERMON_LIST_URL = property(lambda: _config.get("lmrl.remote.fetch_sermon_list", "lmrl/api/sermons")) 

#local
LMRL_LOCAL_BASE_PATH = property(lambda: _config.get("lmrl.local.mp3_base_path", "~/doc/基督/灵命日粮"))