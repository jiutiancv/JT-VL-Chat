import argparse as ap
import base64
import json
import os
import time
import requests
import jwt

parser = ap.ArgumentParser()
parser.add_argument("--url", type=str, default='')
parser.add_argument("--image-dir", type=str, required=False)
parser.add_argument("--image-file", type=str, required=False)
parser.add_argument("--query", type=str, default="describe the image")
parser.add_argument("--temperature", type=float, default=0.7)
parser.add_argument("--max-tokens", type=int, default=128)
parser.add_argument("--output", default='', type=str)
parser.add_argument('--do-sample', action='store_true', default=False)
args = parser.parse_args()

url_chat = args.url

def get_kc_act():
    url = 'https://jiutian.10086.cn/auth/realms/TechnicalMiddlePlatform/protocol/openid-connect/token' #kc获取access_token的url
    user = '' #请填写用户名
    password = ''  #请填写密码

    client_id = 'kunlun-front'
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = 'grant_type=' + 'password&username=' + user + '&password=' + password + '&scope=openid&client_id=' + client_id    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()["access_token"]

#检测access_token是否过期，如果过期就生成一个新的
def check_token_expiration(access_token):
    token_jwt_info = jwt.decode(access_token, key='kunlun-front', algorithms='HS256', options={"verify_signature": False})
    exp = int(token_jwt_info["exp"])
    if time.time() >= exp:
        print('The certificate expires')
        return get_kc_act()
    else:
        return access_token

jtvlchat_access_token = get_kc_act()

def send_request_and_resolve(send_data, image_file=None):
    global jtvlchat_access_token
    jtvlchat_access_token = check_token_expiration(jtvlchat_access_token)
    header_dict = {
        'Authorization': 'Bearer ' + jtvlchat_access_token
    }
    if image_file:
        r = requests.post(url_chat, headers=header_dict, data=send_data, files=image_file, timeout=20000)
    else:
        r = requests.post(url_chat, headers=header_dict, data=send_data, timeout=20000)
        
    if r.status_code == 200:
        try:
            r_json = r.json()
            return r_json['choices'][0]['message']['content'].replace('#', '')
        except:
            error_msg = f'Error! code {r.status_code} content: {r.content}'
            return error_msg
    else:
        try:
            r_json = r.json()
            error_msg = f'Error! code {r.status_code} content: {r_json}'
            return error_msg
        except:
            error_msg = f'Error! code {r.status_code} content: {r.content}'
            return error_msg


def get_response(prompt, image_path, temperature, max_tokens, do_sample):
    f = open(image_path, 'rb')
    image_file = {
        'image_file': (image_path, f)
    }
    send_data = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "do_sample": do_sample
    }
    response = send_request_and_resolve(send_data, image_file=image_file)
    f.close()
    return response

def get_response_no_image(prompt, temperature, max_tokens, do_sample):
    send_data = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "do_sample": do_sample
        }
    return send_request_and_resolve(send_data)

output_file = open(args.output, 'w', encoding='utf-8') if args.output else None
if args.image_dir:
    total_time, num_images = 0, 0
    for image_name in os.listdir(args.image_dir):
        image_path = os.path.join(args.image_dir, image_name)
        if not os.path.isfile(image_path):
            continue
        num_images += 1
        time0 = time.time()
        model_response = get_response(args.query, image_path, args.temperature, args.max_tokens, do_sample=not args.do_sample)
        print(model_response)

        if output_file is not None:
            output_file.write(f'{image_path} ({args.query}): {model_response} \n')
        timed = time.time() - time0
        print(f'Time elapesed: {timed * 1000} ms')
        total_time += timed
    if num_images > 0:
        print(f'Average time elapsed: {total_time * 1000 / num_images} ms / sample')
elif args.image_file:
    model_response = get_response(args.query, args.image_file, args.temperature, args.max_tokens, do_sample=not args.do_sample)
    print(model_response)
    if output_file is not None:
        output_file.write(f'{args.image_file} ({args.query}): {model_response} \n')
else:
    model_response = get_response_no_image(args.query, args.temperature, args.max_tokens, do_sample=not args.do_sample)
    print(model_response)
    if output_file is not None:
        output_file.write(f'[Text Only] {args.query}: {model_response} \n')
if output_file is not None:
    output_file.close()
