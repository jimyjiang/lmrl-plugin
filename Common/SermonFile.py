import os
import threading
import urllib.request
from urllib.parse import quote
import shutil
from . import Consts
import time

class SermonFile:
    def __init__(self, filename, title):
        self.filename = filename
        self.title = title
        self.basePath = Consts.LMRL_LOCAL_BASE_PATH.fget()
        self.baseUrl = "%s" % (Consts.LMRL_HTTP_BASE.fget())
        
        # 解析文件名中的日期信息
        self.short_year = filename[2:4]  # "25"
        self.month = filename[4:6]       # "11"
        self.day = filename[6:8]         # "26"
        self.full_year = "20" + self.short_year  # "2025"
        
    def get_local_path(self):
        """获取本地文件路径"""
        dir_path = os.path.join(self.basePath, self.full_year + self.month)
        return os.path.join(dir_path, self.filename)
    
    def get_remote_url(self):
        """获取远程下载URL"""
        return "%s/%s/%s" % (self.baseUrl, quote("灵命日粮"), self.filename)
    
    def get_temp_path(self):
        """获取临时文件路径"""
        return os.path.join("/tmp", self.filename)
    
    def is_file_exists(self):
        """检查本地文件是否存在"""
        return os.path.exists(self.get_local_path())
    
    def download_file(self, callback=None):
        """下载文件（在后台线程中执行）"""
        if self.is_file_exists():
            print("文件已存在，无需下载",flush=True)
            return
            
        remote_url = self.get_remote_url()
        temp_path = self.get_temp_path()
        local_path = self.get_local_path()
        
        try:
            # 创建目录（如果不存在）
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # 下载到临时文件
            def progress_callback(count, block_size, total_size):
                if total_size > 0:
                        percent = int(count * block_size * 100 / total_size)
                        print("\r下载中: %d%%" % percent, end='', flush=True)
                else:
                        print("\r下载中: %d bytes" % (count * block_size), end='', flush=True)
            if callback is None:
                callback = progress_callback
            
            urllib.request.urlretrieve(remote_url, temp_path, callback)
            print()  # 换行
            
            # 移动到目标位置
            shutil.move(temp_path, local_path)
            
            print("文件已下载到: %s" % (local_path), flush=True)
        except Exception as e:
               
            print("下载失败: %s" % (e) , flush=True)
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def start_download(self, callback=None):
        """启动后台下载"""
        if not self.is_file_exists():
            thread = threading.Thread(target=self.download_file, args=(callback,))
            thread.daemon = True
            thread.start()
    
    def get_play_path(self):
        """获取播放路径"""
        if self.is_file_exists():
            return self.get_local_path()
        else:
            return self.get_remote_url()
    
    def __str__(self):
        return "SermonFile(title='%s', filename='%s')" % (self.title, self.filename)

# 测试代码
if __name__ == "__main__":
    sf = SermonFile("mw251126.mp3", "标题一定要长")
    print(sf)
    print(sf.get_local_path())
    print(sf.get_remote_url())
    if os.path.exists(sf.get_local_path()):
        os.remove(sf.get_local_path())
    print(sf.get_play_path())
    sf.download_file()
    print(sf.get_play_path())
