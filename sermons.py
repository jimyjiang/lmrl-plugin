import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from .Common.Consts import LMRL_HTTP_BASE
from urllib.parse import urljoin

def fetch_sermons(url, timeout=10.0):
    """
    从HTTP服务获取讲道信息
    """
    req = Request(
        url,
        headers={
            'Accept': 'application/json'
        }
    )
    
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
            if not isinstance(data, dict) or 'list' not in data:
                raise ValueError("返回的JSON格式不符合预期")
                
            if not isinstance(data['list'], list):
                raise ValueError("'list' 字段应该是数组")
                
            return data
            
    except json.JSONDecodeError as e:
        raise ValueError("无效的JSON响应") from e
# 测试代码
if __name__ == "__main__":
    url = urljoin(LMRL_HTTP_BASE.fget(), lmrl/api/sermons)
    sermons = fetch_sermons(url)
    print(sermons)