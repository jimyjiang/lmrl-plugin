
import sublime
import subprocess

def gen_call_chrome_apple_script(target_title, js_code):
    return """
    tell application "Google Chrome"
        set foundTab to null
        set windowList to every window
        
        -- 在所有窗口中查找标题匹配的标签页
        repeat with aWindow in windowList
            set tabList to every tab of aWindow
            repeat with aTab in tabList
                if title of aTab contains "{0}" then
                    set foundTab to aTab
                    exit repeat
                end if
            end repeat
            
            if foundTab is not null then
                exit repeat
            end if
        end repeat
        
        -- 如果找到匹配的标签页则执行JS
        if foundTab is not null then
            execute foundTab javascript {1}
            return "Executed on tab: " & (title of foundTab)
        else
            return "ERROR: No tab with title containing '{0}' found"
        end if
    end tell
    """.format(
        target_title,
        '"{}"'.format(js_code.replace('"', '\\"')))

def gen_call_chrome_apple_script_get_title(target_title, js_code):
    return """
tell application "Google Chrome"
    set foundTab to null
    set windowList to every window
    set maxWaitTime to 30 -- 最大等待时间（秒）
    set waitInterval to 0.5 -- 检查间隔（秒）
    set timeElapsed to 0
    
    -- 在所有窗口中查找标题匹配的标签页
    repeat with aWindow in windowList
        set tabList to every tab of aWindow
        repeat with aTab in tabList
            if title of aTab contains "{0}" then
                set foundTab to aTab
                exit repeat
            end if
        end repeat
        
        if foundTab is not null then
            exit repeat
        end if
    end repeat
    
    -- 如果找到匹配的标签页
    if foundTab is not null then
        -- 等待标签页完成加载
        repeat while loading of foundTab is true and timeElapsed < maxWaitTime
            delay waitInterval
            set timeElapsed to timeElapsed + waitInterval
        end repeat
        
        -- 检查是否因为超时而停止等待
        if loading of foundTab is true then
            return "ERROR: Tab is still loading after " & maxWaitTime & " seconds"
        else
            -- 额外检查标题是否存在（有些加载中的页面可能没有标题）
            if title of foundTab is missing value then
                -- 如果标题缺失，等待一小段时间再检查
                delay 0.5
                if title of foundTab is missing value then
                    return "ERROR: Tab has no title (may still be loading)"
                end if
            end if
            
            try
                -- 执行JavaScript并捕获返回值
                set jsResult to execute foundTab javascript {1}
                
                -- 检查JavaScript返回的结果
                if jsResult is missing value then
                    return "JavaScript executed but returned no value"
                else
                    -- 返回JavaScript执行结果和标签页标题
                    return jsResult
                end if
            on error errMsg
                return "ERROR executing JavaScript: " & errMsg
            end try
        end if
    else
        return "ERROR: No tab with title containing '{0}' found"
    end if
end tell
    """.format(
        target_title,
        '"{}"'.format(js_code.replace('"', '\\"')))

def execute_applescript(app, script):
    try:
        process = subprocess.Popen(
            ['osascript', '-e', script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        # 添加解码处理
        stdout = stdout.decode('utf-8', errors='replace').strip()
        stderr = stderr.decode('utf-8', errors='replace').strip()
        
        if process.returncode == 0:
            result = stdout.strip()
            if result.startswith("ERROR:"):
                sublime.error_message("执行错误: %s" % (result[6:]))
            else:
                sublime.status_message("%s: %s" % (app, result))
        else:
            error_msg = stderr.strip() or "未知错误"
            sublime.error_message("执行失败: %s" % (error_msg))
            
    except Exception as e:
        sublime.error_message("执行错误: %s" % (str(e)))

def execute_applescript_return(app, script):
    try:
        process = subprocess.Popen(
            ['osascript', '-e', script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        # 添加解码处理
        stdout = stdout.decode('utf-8', errors='replace').strip()
        stderr = stderr.decode('utf-8', errors='replace').strip()
        
        if process.returncode == 0:
            result = stdout.strip()
            if result.startswith("ERROR:"):
                sublime.error_message("执行错误: %s" % (result[6:]))
            else:
                sublime.status_message("%s: %s" % (app, result))
                return result
        else:
            error_msg = stderr.strip() or "未知错误"
            sublime.error_message("执行失败: %s" % (error_msg))
            
    except Exception as e:
        sublime.error_message("执行错误: %s" % (str(e)))
    return ""