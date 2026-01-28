import sublime, sublime_plugin
import os, subprocess
import locale
from .Common import Command
import re

biblego_path = "~/.go/current/gopath/bin/biblego"

def insert_after_selection(self, edit, region, word):
    end_point = region.end()
    line_region = self.view.line(end_point)
    line_end = line_region.end()
    
    # 判断是否是文件最后一行
    is_end_of_file = (line_end == self.view.size())
    
    # 计算插入位置和换行前缀
    insert_point = line_end if is_end_of_file else line_end + 1
    newline_prefix = "\n" if is_end_of_file else ""
    
    # 执行插入
    self.view.insert(edit, insert_point, "%s%s\n" % (newline_prefix, word))
    # 移动光标，到新增的word 末尾
    self.view.sel().clear()
    self.view.sel().add(sublime.Region(line_end+len(word)+1))

def insert_header_selection(self, edit, region, word):
    start_point = region.begin()
    line_region = self.view.line(start_point)
    line_start = line_region.begin()
     # 执行插入
    self.view.insert(edit, line_start, "%s" % (word+"\n"))
    # 移动光标，移到行首
    self.view.sel().clear()
    self.view.sel().add(sublime.Region(self.view.line(line_start).begin()))

"""
BibleGo 命令
command + b + b
""" 
class BibleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        range = self.view.sel()[0]
        print(range.begin(), range.end())
        content = ""
        if range.empty():
            # 如果区域是空的（没有选择），获取当前行
            line_region = self.view.line(range)
            content = self.view.substr(line_region)
        else:
            content = self.view.substr(range)
        cmd = "%s \"%s\"" % (biblego_path, content)
        word = Command.run_command(cmd)
        insert_after_selection(self, edit, range, word)

"""
BibleGo 上/下移
ctrl + option + up/down
"""
class BibleGoMoveCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction="up"):
        range = self.view.sel()[0]
        content = ""
        if range.empty():
            # 如果区域是空的（没有选择），获取当前行
            line_region = self.view.line(range)
            content = self.view.substr(line_region)
        else:
            content = self.view.substr(range)
        result = content.split(' ')[0]  # 默认取第一个空格前的部分，如果没有空格，split(' ') 会返回 [content]
        verse = self.getVerse(result, direction)
        cmd = "%s \"%s\"" % (biblego_path, verse)
        word = Command.run_command(cmd)
        if direction == "up":
            insert_header_selection(self, edit, range, word)
        else:
            insert_after_selection(self, edit, range, word)
    def getVerse(self, verse, direction):
        # 解析字符串，提取书、章、节
        book_end = 0
        while book_end < len(verse) and not verse[book_end].isdigit():
            book_end += 1
            book = verse[:book_end]
            # 剩余部分按 ':' 分割章和节
            remaining = verse[book_end:]
        if ':' not in remaining:
            raise ValueError("Invalid verse format (missing ':')")
        chapter_part, verse_part = remaining.split(':', 1)
        chapter = int(chapter_part)
        verse_num = int(verse_part)

        # 根据 direction 调整节数
        if direction == "up":
            verse_num = max(1, verse_num - 1)  # 最小为0
        elif direction == "down":
            verse_num += 1
        else:
            raise ValueError("Invalid direction (use 'up' or 'down')")

        # 返回格式化字符串
        return "%s%d:%d" % (book, chapter, verse_num) 

booksMap = {
    "创":"旧约 p1",
    "出":"旧约 p53",
    "利":"旧约 p94",
    "民":"旧约 p123",
    "申":"旧约 p165",
    "书":"旧约 p203",
    "士":"旧约 p229",
    "得":"旧约 p254",
    "撒上":"旧约 p258",
    "撒下":"旧约 p290",
    "王上":"旧约 p318",
    "王下":"旧约 p349",
    "代上":"旧约 p379",
    "代下":"旧约 p410",
    "拉":"旧约 p444",
    "尼":"旧约 p454",
    "斯":"旧约 p469",
    "伯":"旧约 p476",
    "诗":"旧约 p512",
    "箴":"旧约 p613",
    "传":"旧约 p643",
    "歌":"旧约 p651",
    "赛":"旧约 p658",
    "耶":"旧约 p732",
    "哀":"旧约 p803",
    "结":"旧约 p812",
    "但":"旧约 p864",
    "何":"旧约 p879",
    "珥":"旧约 p891",
    "摩":"旧约 p896",
    "俄":"旧约 p905",
    "拿":"旧约 p907",
    "弥":"旧约 p909",
    "鸿":"旧约 p916",
    "哈":"旧约 p919",
    "番":"旧约 p923",
    "该":"旧约 p927",
    "亚":"旧约 p929",
    "玛":"旧约 p939",
    "太":"新约 p1",
    "可":"新约 p40",
    "路":"新约 p64",
    "约":"新约 p104",
    "徒":"新约 p133",
    "罗":"新约 p168",
    "林前":"新约 p184",
    "林后":"新约 p199",
    "加":"新约 p209",
    "弗":"新约 p215",
    "腓":"新约 p220",
    "西":"新约 p224",
    "帖前":"新约 p228",
    "帖后":"新约 p232",
    "提前":"新约 p234",
    "提后":"新约 p238",
    "多":"新约 p241",
    "门":"新约 p243",
    "来":"新约 p244",
    "雅":"新约 p256",
    "彼前":"新约 p260",
    "彼后":"新约 p265",
    "约一":"新约 p268",
    "约壹":"新约 p268",
    "约二":"新约 p272",
    "约贰":"新约 p272",
    "约三":"新约 p273",
    "约叁":"新约 p273",
    "犹":"新约 p274",
    "启":"新约 p276",
}