import sublime
import sublime_plugin

class InsertTextCommand(sublime_plugin.TextCommand):
        """辅助命令：在光标位置插入文本"""
        def run(self, edit, text):
                for region in self.view.sel():
                        self.view.insert(edit, region.begin(), text)