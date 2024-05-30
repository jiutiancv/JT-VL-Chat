# JT-VL-Chat
JT-VL-Chat是一个多模态大模型。
# 更新日志
2024-05-31：发布推理API。
# 快速上手
## 访问API  
登录https://jiutian.10086.cn/portal/#/home, 右上角注册用户信息。待审核通过后，即可访问API。
## 推理
推理服务可以直接通过代码调用方式访问：<br>
```python
#!/usr/bin/env python3  
#encoding: utf-8  
import base64  
import json  
import requests  
import argparse as ap  
url_chat = '' # 此处填入调用的url  
def send_request_and_resolve(send_data):  
    json_data = json.dumps(send_data)  

    header_dict = {'Content-Type': 'application/json'}  

    r = requests.post(url_chat, headers=header_dict, data=json_data, timeout=300)  
    try:  
        r_json = r.json()  
        return r_json['choices'][0]['message']['content']  
    except:  
        error_msg = f'Error! code {r.status_code} content: {r.content}'  
        return error_msg  

def get_response(prompt, image_path, temperature, max_tokens):  
    image = ''  
    with open(image_path, 'rb') as f:  
        image = str(base64.b64encode(f.read()), 'utf-8')  
    send_data = {  
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "image_base64": image,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    return send_request_and_resolve(send_data)

  def get_response_no_image(prompt, temperature, max_tokens):
    send_data = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
        }
    return send_request_and_resolve(send_data)

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-i', type=str, default='')
    parser.add_argument('-q', type=str, default="图片中是什么？")
    parser.add_argument('-t', '--temperature', type=float, default=0.7)
    parser.add_argument('-m', '--max-tokens', type=int, default=1024)
    args = parser.parse_args()

    if args.i:
        result = get_response(args.q, args.i, args.temperature, args.max_tokens)
    else:
        result = get_response_no_image(args.q, args.temperature, args.max_tokens)
    print(result)
```
请求成功时返回示例：  
```python
{
    "object": "chat.completions",
    "created": 1698913482,
    "code":20000,
    "status": "successful response",
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": "该图像显示了各种颜色的两维或三维（灰色、蓝色和红色）数据在坐标轴上的排列。该图显示了不同颜色对折或分组的各个级别。",
                "role": "assistant"
            }
        }
    ],
    "usage": {
        "completion_tokens": 44,
        "prompt_tokens": 325,
        "total_tokens": 369
    }
}
```
请求失败时返回示例：  
```python
{
    "object": "chat.completions",
    "created": 1698913482,
    "code": 50000,
    "status": "Unknown Error",
    "choices": []
}
```
