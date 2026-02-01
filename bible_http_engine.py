import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urljoin,quote
from .Common.Consts import LMRL_HTTP_BASE

def SearchBible(query, timeout=10.0):
    """
    从LMRL API搜索信息
    
    Args:
        query (str): 搜索查询字符串
        timeout (float): 请求超时时间，默认为10秒
        
    Returns:
        dict: 解析后的JSON响应数据
        
    Raises:
        HTTPError: 当HTTP请求失败时
        ValueError: 当响应数据无效时
    """
    base_url = urljoin(LMRL_HTTP_BASE.fget(), "lmrl/api/search")
    url = "%s?q=%s" % (base_url, quote(query))
    print(url)
    headers = {
        'Accept': 'application/json'
    }
    req = Request(url, headers=headers)
    
    try:
        with urlopen(req, timeout=timeout) as response:
            if response.code != 200:
                raise HTTPError(
                    response.url,
                    response.code,
                    response.msg,
                    response.headers,
                    None
                )
            
            content = response.read().decode('utf-8')
            data = json.loads(content)
            
            # 基本数据验证
            if not isinstance(data, dict):
                raise ValueError("返回的JSON格式不符合预期")
            return format_bible_verses(data)
            
    except json.JSONDecodeError as e:
        raise ValueError("无效的JSON响应") from e
    except URLError as e:
        raise HTTPError(url, 500, str(e), {}, None) from e

def format_bible_verses(data):
    """
    格式化圣经经文数据为指定输出格式，多项内容用换行符分隔
    
    参数:
        data (dict): 包含经文数据的字典，格式如:
                    {'results': [
                        {'reference': '箴10:17', 'text': '谨守训诲的，乃在生命的道上...'},
                        {'reference': '箴10:18', 'text': '隐藏怨恨的，有说谎的嘴...'}
                    ]}
    
    返回:
        str: 格式化后的字符串，每段经文为"引用 内容"，用换行符分隔
    """
    try:
        verses = data['results']
        formatted_verses = []
        for verse in verses:
            formatted_verses.append("%s %s" % (verse['reference'], verse['text']))
        if len(formatted_verses) == 0:
            return "未找到结果"
        return '\n'.join(formatted_verses)
    except (KeyError, TypeError):
        return "无效的输入格式"

# 测试代码
if __name__ == "__main__":
    query = "按他的信实审判万民"  # 等同于URL编码的"%E6%8C%89%E4%BB%96%E7%9A%84%E4%BF%A1%E5%AE%9E%E5%AE%A1%E5%88%A4%E4%B8%87%E6%B0%91"
    try:
        result = SearchBible(query)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except HTTPError as e:
        print("HTTP错误: %s" % (e.reason))
    except ValueError as e:
        print("数据错误: %s" % (str(e)))