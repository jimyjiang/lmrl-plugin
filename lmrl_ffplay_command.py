import sublime
import sublime_plugin
import sys
import os
import tempfile
from . import mp3_player 
from . import sermons
from .Common.SermonFile import SermonFile
import requests
from .Common.Consts import LMRL_HTTP_BASE, LMRL_FETCH_SERMON_LIST_URL
from urllib.parse import urljoin


def progress_callback(count, block_size, total_size):
    msg = ""
    if total_size > 0:
        percent = int(count * block_size * 100 / total_size)
        msg = "下载中: %d%%" % percent
    else:
        msg = "下载中: %d bytes" % (count * block_size)
    print(msg, end='\n', flush=True)
    sublime.status_message(msg)

class FetchSermonsCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.selected_sermon = None
        # 1. 弹出选择窗口
        list = self.list_sermons()
        
        if not list:
                sublime.error_message("No sermons.")
                return
        self.sermons = [SermonFile(s['Filename'],s['Title']) for s in list]
        items = [s.title for s in self.sermons]
        self.window.show_quick_panel(
            items,
            self.on_select,
            sublime.MONOSPACE_FONT,
            0,  # 默认选中第0项
            self.on_highlight
        )
    def list_sermons(self):
        try:
            url = urljoin(LMRL_HTTP_BASE.fget(), LMRL_FETCH_SERMON_LIST_URL.fget())
            print(url)
            resp = sermons.fetch_sermons(url)
            return resp['list']
        except Exception as e:
            sublime.error_message("Error: %s" % (str(e)))
    def on_select(self, index):
        if index == -1:
                return
        self.selected_sermon = self.sermons[index]
        self.selected_sermon.start_download(progress_callback)
       
        self.on_done()
    def on_highlight(self, index):
        """用户高亮某文件时的预览（可选）"""
        pass
    def on_done(self):
        view = self.window.active_view()
        if view:
            view.run_command("insert_text", {"text": self.selected_sermon.title})
            sublime.set_clipboard(self.selected_sermon.title)
            sublime.status_message("Text copied to clipboard")
        try:
            player = mp3_player.get_player()
            player.load(self.selected_sermon)
            player.play()
            
        except Exception as e:
            sublime.error_message("Error: %s" % (str(e)))

class PlayPauseAudioFfCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            player = mp3_player.get_player()
            if player.playing:
                player.pause()
            else:
                player.play()
        except Exception as e:
            sublime.error_message("%s" % (str(e)))
        

class StopAudioFfCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            player = mp3_player.get_player()
            player.stop()
        except Exception as e:
            sublime.error_message("%s" % (str(e)))

class RewindAudioFfCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            player = mp3_player.get_player()
            new_pos = max(0, player.get_position() - 8)  # 后退8秒
            player.seek(new_pos)
        except Exception as e:
            sublime.error_message("%s" % (str(e)))

class ForwardAudioFfCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            player = mp3_player.get_player()
            new_pos = player.get_position() + 5  # 前进5秒
            player.seek(new_pos)
        except Exception as e:
            sublime.error_message("%s" % (str(e)))

class SkipToPreviousSegmentAudioFfCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            player = mp3_player.get_player()
            new_pos = player.skip_to_previous_segment()
            if new_pos is None:
                new_pos = 0
            player.seek(new_pos)
        except Exception as e:
            sublime.error_message("%s" % (str(e)))

class SkipToNextSegmentAudioFfCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            player = mp3_player.get_player()
            new_pos = player.skip_to_next_segment()
            if new_pos is None:
                return
            player.seek(new_pos)
        except Exception as e:
            sublime.error_message("%s" % (str(e)))