# mp3_player.py
import os
import sys
import subprocess
import time
import tempfile
from threading import Lock
from functools import partial

try:
    import sublime
    _HAS_SUBLIME = True
except ImportError:
    _HAS_SUBLIME = False

from .Common.Consts import LMRL_HTTP_BASE
from urllib.parse import urljoin

# 监测间隔（毫秒）
_WATCHER_INTERVAL_MS = 300

def find_previous_segment(segments, current_pos, last_skip_pos=None):
    """
    在音频分段中找到前一个播放区间的开始位置

    参数:
        segments: 已排序的非负整数数组，表示各段的开始位置
        current_pos: 当前播放位置
        last_skip_pos: 上一次跳转的位置(可选)

    返回:
        前一个区间的开始位置，如果不存在则返回None
    """
    candidates = [s for s in segments if s < current_pos]

    if not candidates:
        return None

    if last_skip_pos is not None:
        candidates = [s for s in candidates if s < last_skip_pos]
        if not candidates:
            return None

    return max(candidates)

def find_next_segment(segments, current_pos):
    """
    找到当前播放位置之后的下一个分段起始点

    参数:
        segments: 已排序的分段起始时间列表
        current_pos: 当前播放位置

    返回:
        下一个分段起始时间，若已是最后分段则返回None
    """
    for seg in sorted(segments):
        if seg > current_pos:
            return seg
    return None


class _FFmpegPlayer(object):
    """基于 ffmpeg 命令行的播放器核心（带播放完成自动检测）"""

    def __init__(self):
        self._temp_files = []
        self._start_time = 0
        self._paused_time = 0
        self.playing = False
        self._sermon_file = None
        self.segments = [0, 60, 135, 320, 440, 1640]
        self.last_skip_pos = None
        self.last_skip_time = 0  # 上次回退的时间戳

        # 播放完成监测相关
        self._stop_requested = False   # 是否为主动 stop/pause（非自然播完）
        self._watcher_token = 0        # 代际 token：每次启动新监测递增，旧回调自动失效
        self.on_finish = None          # 可选：自然播完后的回调 hook

    def load(self, sermon_file):
        """
        加载音频文件
        :param sermon_file: 音频文件对象（需实现 get_play_path()）
        :raises: ValueError 如果文件不可用
        """
        self.stop()
        self._sermon_file = sermon_file
        self._paused_time = 0

    def play(self):
        """播放/恢复播放"""
        if self.playing:
            return

        if not self._sermon_file:
            raise ValueError("未指定音频文件")

        # 重置停止标记（本轮开始后，进程退出将被视为自然播完）
        self._stop_requested = False

        # 计算起始位置（用于恢复播放）
        start_pos = self._paused_time
        self._start_time = time.time() - start_pos

        # 构建 ffmpeg 命令
        audio_path = self._sermon_file.get_play_path()
        player_cmd = [
            'ffplay',
            '-autoexit',
            '-nodisp',
            '-ss', str(start_pos),
            audio_path,
        ]
        print(player_cmd)

        self._player_process = subprocess.Popen(
            player_cmd,
            stdin=subprocess.DEVNULL,    # 禁 stdin
            stdout=subprocess.DEVNULL,   # 丢弃 stdout，避免管道满阻塞
            stderr=subprocess.DEVNULL    # 丢弃 stderr，避免管道满阻塞
        )
        self.playing = True

        # 启动监测：定期 poll() 检查进程是否自然结束
        self._start_watcher()

    def _start_watcher(self):
        """使用 sublime.set_timeout_async 启动轮询监测器（代际 token 防竞态）"""
        if not _HAS_SUBLIME:
            return
        self._watcher_token += 1
        token = self._watcher_token
        sublime.set_timeout_async(partial(self._check_process, token), _WATCHER_INTERVAL_MS)

    def _check_process(self, token):
        """轮询回调：检查子进程是否仍在运行。token 不匹配则视为过期回调，直接退出。"""
        # token 不匹配 = 这是旧会话的回调（stop/seek 后已启动新会话），直接丢弃
        if token != self._watcher_token:
            return

        # 没有进程对象，直接结束监测
        if not hasattr(self, '_player_process') or self._player_process is None:
            return

        retcode = self._player_process.poll()

        if retcode is None:
            # 还在运行，下次继续查（携带同一 token）
            if _HAS_SUBLIME:
                sublime.set_timeout_async(partial(self._check_process, token), _WATCHER_INTERVAL_MS)
            return

        # ---- 进程已退出 ----

        # 区分：主动 stop()/pause()  vs  自然播完/异常崩溃
        if self._stop_requested:
            # 主动停止，状态已经在 stop() 中设置过了，这里什么都不做
            return

        # 自然播完（或异常崩溃）：更新 playing 状态并保存位置
        final_pos = self.get_position()
        self._paused_time = max(0, final_pos)
        self.playing = False

        # 清理进程引用（避免重复操作）
        try:
            if hasattr(self, '_player_process'):
                del self._player_process
        except Exception:
            pass

        # 触发可选的播完回调
        if callable(self.on_finish):
            try:
                self.on_finish(final_pos, retcode)
            except Exception as e:
                print("on_finish callback error: %s" % str(e))

    def pause(self):
        """暂停播放"""
        if not self.playing:
            return

        # 先保存位置，再 stop
        self._paused_time = self.get_position()
        self.stop()
        # stop() 已将 playing 置为 False，这里保持一致

    def stop(self):
        """停止播放（主动调用，_stop_requested=True 用于监测器区分）"""
        self._stop_requested = True
        self._watcher_token += 1  # 使旧的 pending 回调失效

        if hasattr(self, '_player_process') and self._player_process is not None:
            try:
                self._player_process.terminate()
                self._player_process.wait()
            except Exception:
                pass
            try:
                del self._player_process
            except Exception:
                pass

        self.playing = False

    def seek(self, seconds):
        """跳转到指定位置（秒）"""
        self.stop()
        self._paused_time = max(0, seconds)
        self.play()

    def skip_to_previous_segment(self):
        now = time.time()
        if now - self.last_skip_time > 1.0:
            self.last_skip_pos = None

        new_pos = find_previous_segment(self.segments, self.get_position(), self.last_skip_pos)
        if new_pos:
            self.last_skip_pos = new_pos
            self.last_skip_time = now
        return new_pos

    def skip_to_next_segment(self):
        new_pos = find_next_segment(self.segments, self.get_position())
        return new_pos

    def get_position(self):
        """获取当前播放位置（秒）"""
        if not self.playing:
            return self._paused_time
        return time.time() - self._start_time

    def cleanup(self):
        """资源清理"""
        self.stop()
        for f in self._temp_files:
            try:
                os.unlink(f)
            except Exception:
                pass
        self._temp_files = []


# 模块级单例
_instance = None
_instance_lock = Lock()

def get_player():
    """获取全局播放器实例"""
    global _instance
    if _instance is None:
        with _instance_lock:
            if _instance is None:
                _instance = _FFmpegPlayer()
    return _instance


# 测试代码（直接运行：python mp3_player.py）
if __name__ == "__main__":
    player = get_player()
    try:
        print("load")
        mp3Url = urljoin(LMRL_HTTP_BASE.fget(), "%E7%81%B5%E5%91%BD%E6%97%A5%E7%B2%AE/mw251125.mp3")
        player.load(mp3Url)
        print("loaded")

        # 注册一个播完回调用于调试
        def finish_hook(pos, code):
            print("playback finished: pos=%.1fs retcode=%s playing=%s" % (pos, code, player.playing))
        player.on_finish = finish_hook

        player.play()
        time.sleep(2)

        # 测试暂停
        player.pause()
        print("pause, 当前位置:", player.get_position(), "playing=", player.playing)
        time.sleep(1)

        # 测试恢复
        player.play()
        print("resume, playing=", player.playing)
        time.sleep(1)

        # 测试跳转
        player.seek(10)
        print("seek(10), playing=", player.playing)
        time.sleep(1)
    finally:
        player.cleanup()
        print("cleanup done, playing=", player.playing)
