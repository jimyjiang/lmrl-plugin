import sublime
import sublime_plugin
import threading
import time
from .Common import ChromeCall


class RefreshPageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # 在后台线程执行耗时操作
        thread = threading.Thread(target=self._refresh_and_get_link)
        thread.start()
    def _refresh_and_get_link(self):
        """
        执行浏览器中的location.reload()函数来刷新当前页面
        """
        # 要执行的JavaScript代码
        js_code = self.get_javascript_code()
        # 构建AppleScript
        script = ChromeCall.gen_call_chrome_apple_script("《旷野吗哪》灵修信息", js_code)
        # 执行AppleScript并显示结果
        ChromeCall.execute_applescript("旷野吗哪", script)

        js_code = self.get_javascript_code_for_title()
        script = ChromeCall.gen_call_chrome_apple_script_get_title("《旷野吗哪》灵修信息", js_code)
        print(script)
        # 执行AppleScript并显示结果
        result = ChromeCall.execute_applescript_return("旷野吗哪", script)
        # 插入结果
        range = self.view.sel()[0]
        # 完成后更新UI需要在主线程执行
        sublime.set_timeout(lambda: self._update_ui( range.begin(), result), 0)
    def _update_ui(self, pos, result):
        # 在主线程更新UI
        self.view.run_command("update_content", {"content": result})
    def get_javascript_code(self):
        return """
            (function() {
                window.location.reload();
                return '页面已刷新';
            })();
        """
    def get_javascript_code_for_title(self):
        return """
(function() {
    var links = document.getElementsByTagName("a");
    for(var link of links) {
        if((link.href||"").endsWith(".mp3")) {
            var eles = link.getElementsByTagName("span");
            return eles.length < 1 ? "未找到音频" :  eles[0].innerText;
        }
    }
    return '未找到音频';
})();
        """

class UpdateContentCommand(sublime_plugin.TextCommand):
    def run(self, edit, content):
        range = self.view.sel()[0]
        self.view.insert(edit, range.begin(), content)

class PlayPauseAudioCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        """
        执行浏览器中的playOrPause()函数来控制音频播放/暂停
        """
        # 要执行的JavaScript代码
        js_code = self.get_javascript_code()
        # 构建AppleScript
        script = ChromeCall.gen_call_chrome_apple_script("《旷野吗哪》灵修信息", js_code)
        # 执行AppleScript并显示结果
        ChromeCall.execute_applescript("旷野吗哪", script)
    def get_javascript_code(self):
        return """
(function() {
    var getMp3Link = () => {
        var links = document.getElementsByTagName("a");
        for(var link of links) {
            if((link.href||"").endsWith(".mp3")) {
                return link;
            }
        }
        return null;
    }
    const modalAudioPlayer = document.getElementById('modalAudioPlayer');
    if (modalAudioPlayer) {
        if(modalAudioPlayer.src == "") {
            var link = getMp3Link();
            if(link) {
                link.click();
                return;
            }
        }
        if (modalAudioPlayer.paused) {
            modalAudioPlayer.play();
            return '播放音频';
        } else {
            modalAudioPlayer.pause();
            return '暂停音频';
        }
    }
    return '未找到音频播放器';
})();
        """
class ForwardRewindAudioCommand(sublime_plugin.TextCommand):
    def get_javascript_code(self, move):
        return """
            (function forwardOrRewind(move) {
                    const modalAudioPlayer = document.getElementById('modalAudioPlayer');
                    if(!modalAudioPlayer) { return '未找到音频播放器';}
                    let actionBtn = move == "forward" ? document.getElementById('forwardBtn'): document.getElementById('rewindBtn');
                    actionBtn && actionBtn.click();
                    if (modalAudioPlayer.paused) {
                        modalAudioPlayer.play();
                    }
                    return move+'操作已完成';
            })("%s");
        """ % (move)
    def run(self, edit, move="rewind"):
        """
        执行浏览器中的forwardOrRewind(move)函数来控制音频快进/倒退
        """
        # 要执行的JavaScript代码
        js_code = self.get_javascript_code(move)
        # 构建AppleScript
        script = ChromeCall.gen_call_chrome_apple_script("《旷野吗哪》灵修信息", js_code)
        # 执行AppleScript并显示结果
        ChromeCall.execute_applescript("旷野吗哪", script)
    

    def input(self, args):
        if "move" not in args:
            return MoveInputHandler()
        return None

class MoveInputHandler(sublime_plugin.ListInputHandler):
    def name(self):
        return "move"
    
    def list_items(self):
        return [
            ("快进 15 秒", "forward"),
            ("倒退 15 秒", "rewind")
        ]
    
    def placeholder(self):
        return "选择快进/倒退"