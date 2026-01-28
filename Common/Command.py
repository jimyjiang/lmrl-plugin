

import os, subprocess

def run_command(cmd):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,  # 如果命令是字符串而非列表
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        return "错误: %s" % (stderr.decode('utf-8'))
    return stdout.decode("utf-8")