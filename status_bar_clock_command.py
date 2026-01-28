import sublime
import sublime_plugin
import datetime
import threading

class StatusBarClockCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        # 更新时间的函数
        def update_time():
            now = datetime.datetime.now()
            time_str = now.strftime("%Y-%m-%d %H:%M:%S")
            sublime.status_message(time_str)
            # 1秒后再次调用自己
            threading.Timer(1.0, update_time).start()
        
        # 开始更新时间
        update_time()

# 插件加载时自动启动时钟
def plugin_loaded():
    sublime.run_command("status_bar_clock")