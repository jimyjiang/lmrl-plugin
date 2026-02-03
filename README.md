# LMRL Plugin

## 项目介绍

面向 Sublime Text 的灵修与查经插件，提供：

- 圣经查询与上下文移动（支持本地命令行与远程 HTTP 引擎）
- 灵命日粮音频播放（远程下载/本地缓存、播放控制、分段跳转）
- 播放状态展示（状态弹窗、状态栏提示）

## 软件架构

- 插件命令与菜单：参见 `Default.sublime-commands` 与 `Main.sublime-menu`
- 快捷键映射：参见 `Default.sublime-keymap`
- 配置加载：用户设置 > 系统默认 > 代码默认，支持嵌套键的逐级回退

## 安装依赖

### 命令定义

`./Default.sublime-commands` 为命令面板的注册文件。修改后需重启 Sublime 生效。

## 安装教程

```bash
> ./build.sh
```

## 使用说明

- 打开命令面板：`Ctrl + Shift + P`
- 输入：`lmrl-plugin`
- 选择对应命令执行

### 命令列表（Command Palette）

- lmrl-plugin: Bible → 查经（根据 `lmrl.bible.engine` 选择引擎）
- lmrl-plugin: BibleGoMove → 查经上下移动（通过 `args: {direction: up|down}`）
- lmrl-plugin: FetchSermons → 拉取并选择灵命日粮讲道，下载并播放
- lmrl-plugin: PlayPauseAudioFf → 播放/暂停
- lmrl-plugin: RewindAudioFf → 后退 8 秒
- lmrl-plugin: ForwardAudioFf → 前进 5 秒
- lmrl-plugin: SkipToPreviousSegmentAudioFf → 回到上一段
- lmrl-plugin: SkipToNextSegmentAudioFf → 跳到下一段
- lmrl-plugin: ShowPlayerStatus → 显示播放状态弹窗（标题、时间、状态）
- lmrl-plugin: HidePlayerStatus → 隐藏播放状态弹窗

## 快捷键

### 灵命日粮播放器

- key:(command + j, command + r): 播放列表
- key:(command + j, command + p): 播放/暂停
- key:(ctrl + option + left/right): 后退/快进
- key:(ctrl + option + shift + left/right): 前一段/后一段

### 查询圣经

- key:(command + j, command + b): 查经
- key:(ctrl + option + up/down): 向上查经/向下查经

## 配置

通过菜单 Preferences → Package Settings → lmrl plugin 打开：

- Settings – Default：系统默认
- Settings – User：用户覆盖

配置优先级：用户设置 > 系统设置 > 代码默认；支持嵌套键的逐级回退。

常用配置项（示例）：

```json
{
  "lmrl": {
    "bible": {
      "engine": "cmd" // 支持 "cmd" 或 "http"
    },
    "remote": {
      "http_base": "http://localhost:3001",
      "fetch_sermon_list": "lmrl/api/sermons"
    },
    "local": {
      "mp3_base_path": "~/doc/基督/灵命日粮",
      "bible_search_cmd": "~/.go/current/gopath/bin/biblego"
    }
  }
}
```

### 圣经查询

- 引擎选择：`lmrl.bible.engine`
  - `cmd`：使用本地可执行文件 `lmrl.local.bible_search_cmd`（如 biblego）
  - `http`：调用远程服务
- 使用方法：
  - 光标所在行或选区作为查询内容
  - 上/下移动：以当前节为基准，向前/向后一节并查询插入

### 灵命日粮播放器

- 拉取列表：从 `lmrl.remote.http_base` + `lmrl.remote.fetch_sermon_list` 获取讲道列表
- 下载与缓存：
  - 本地缓存目录：`lmrl.local.mp3_base_path`
  - 目录结构：`${YYYY}${MM}/filename.mp3`（例如 `202511/mw251126.mp3`）
  - 已存在则直接使用本地文件；否则后台下载到缓存后播放
- 播放控制：播放/暂停、后退/前进、上一段/下一段、状态弹窗展示

## 前置要求

- 需安装 `ffplay`（随 ffmpeg 提供），用于音频播放
- 如使用 `cmd` 查经引擎，需安装并配置 `biblego` 可执行路径
- 如使用 `http` 查经或远程讲道列表，需保证服务可访问

## 参考

1. https://www.sublimetext.com/docs/api_reference.html
