import sublime
import sublime_plugin
from . import mp3_player 
from .shared_phantom import get_phantom_set, clear_phantom_set, set_timeout_async

refresh_status_popup_command = "show_player_status"
class HidePlayerStatusCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        clear_phantom_set(self.view)

class ShowPlayerStatusCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        super().__init__(view)
        self.update_timer = None

    def run(self, edit):
        self.update_phantom()
        # 设置定时更新
        set_timeout_async(self.view, self.run_timer, 1)

    def run_timer(self):
        if self.view.is_valid():
            self.view.run_command(refresh_status_popup_command)
    
    def update_phantom(self):
        player = mp3_player.get_player()
        if player._sermon_file is None:
            sublime.error_message("未播放")
            raise Exception("未播放")
        region = sublime.Region(0, 0)  # 固定在文档开头
        # row = self.view.visible_region().a
        # region = sublime.Region(row*10, 0)

        title = player._sermon_file.title
        timeSeconds = player.get_position()
        status = "播放中" if player.playing else "暂停中"
        if not player.playing:
            player._paused_time
        time = "%02d:%02d" % (int(timeSeconds/60) , timeSeconds%60)
        content = """
        <body>
            <h1>{title}</h1>
            <div style="background:rgba(30,60,90,0.8);color:white;padding:8px;">
                播放时间: {time}<br>
                播放状态: {status}<br>
            </div>
        </body>
        """.format(
            title=title,
            time=time,  # 示例：使用剪贴板内容
            status=status, 
        )
        
        get_phantom_set(self.view).update([sublime.Phantom(
            region,
            content,
            sublime.LAYOUT_BLOCK
        )])

    def __del__(self):
        if self.update_timer:
            sublime.cancel_timeout(self.update_timer)