# mp3_player.py
import os
import sys
import subprocess
import time
import threading
import tempfile
from threading import Lock
from .Common.Consts import LMRL_HTTP_BASE
from urllib.parse import urljoin

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
    # 找到所有小于current_pos的段开始位置
    candidates = [s for s in segments if s < current_pos]
    
    if not candidates:
        return None
    
    # 如果有last_skip_pos，我们需要跳过它找到更早的段
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
    """基于 ffmpeg 命令行的播放器核心"""
    def __init__(self):
        self._temp_files = []
        self._start_time = 0
        self._paused_time = 0
        self.playing = False
        self._sermon_file = None
        # self._current_file = None
        self.segments = [0,60,135,320,440,1640]
        self.last_skip_pos = None
        self.last_skip_time = 0 # 上次回退的时间戳
    def load(self, sermon_file):
        """
        加载音频文件
        :param file_path: 音频文件路径（支持MP3/WAV等ffmpeg支持的格式）
        :raises: ValueError 如果文件不可用
        """
        # 停止当前播放
        self.stop()
        # 更新状态
        self._sermon_file = sermon_file
        # self._current_file = file_path
        self._paused_time = 0

    def play(self):
        """播放/恢复播放"""
        if self.playing:
            return

        if not self._sermon_file:
            raise ValueError("未指定音频文件")

        # 计算起始位置（用于恢复播放）
        start_pos = self._paused_time
        self._start_time = time.time() - start_pos

        # 构建 ffmpeg 命令
        player_cmd = [
            'ffplay',
            '-autoexit',
            '-nodisp',
            '-ss', str(start_pos),  # 跳转到指定位置
            self._sermon_file.get_play_path(),
        ]
        # 启动 ffmpeg 进程
        self._player_process = subprocess.Popen(
            player_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.playing = True

    def pause(self):
        """暂停播放"""
        if not self.playing:
            return

        self._paused_time = self.get_position()
        self.stop()
        self.playing = False

    def stop(self):
        """停止播放"""
        if hasattr(self, '_player_process'):
            self._player_process.terminate()
            self._player_process.wait()
            del self._player_process
        self.playing = False

    def seek(self, seconds):
        """跳转到指定位置（秒）"""
        self.stop()
        self._paused_time = max(0, seconds)
        self.play()
    def skip_to_previous_segment(self):
        now = time.time()
        # 如果距离上次回退超过1秒，则重置last_skip_pos
        if now - self.last_skip_time > 1.0:
            self.last_skip_pos = None
        
        new_pos = find_previous_segment(self.segments, self.get_position(), self.last_skip_pos)
        if new_pos:
            self.last_skip_pos = new_pos
            self.last_skip_time = now  # 更新回退时间
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
        """增强的资源清理"""
        self.stop()
        self._current_file = None
        for f in self._temp_files:
            try:
                os.unlink(f)
            except:
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

# 测试代码
if __name__ == "__main__":
    player = get_player()
    try:
        # 测试播放
        print("load") 
        mp3Url = urljoin(LMRL_HTTP_BASE.fget(), "%E7%81%B5%E5%91%BD%E6%97%A5%E7%B2%AE/mw251125.mp3")
        player.load(mp3Url)
        print("loaded")
        player.play()
        time.sleep(2)
        
        # 测试暂停
        player.pause()
        print("当前位置:", player.get_position())
        time.sleep(1)
        
        # 测试恢复
        player.play()
        time.sleep(1)
        
        # 测试跳转
        player.seek(10)
    finally:
        player.cleanup()