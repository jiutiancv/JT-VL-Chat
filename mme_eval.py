import argparse as ap
import base64
import json
import os
import time
import requests
import jwt

parser = ap.ArgumentParser()
parser.add_argument("--url", type=str, default='https://jiutian.10086.cn/kunlun/ingress/api/h3t-eeceff/92390745235a40a484d850be19e1f8b4/ai-9072cb8293e94981b0b86aebb87d0002/service-8443a3d1e7af4ca384695b538e945d7f/v1/chat/completions')
parser.add_argument("--query-dir", type=str, default='mme_queries')
parser.add_argument("--output-dir", default='outputs', type=str)
parser.add_argument("--output-file", default='mme_results.txt', type=str)
parser.add_argument("--mme-image-dir", type=str, default='mme_images')
parser.add_argument("--temperature", type=float, default=0.0)
parser.add_argument("--max-tokens", type=int, default=64)
parser.add_argument('--do-sample', action='store_true', default=False)
args = parser.parse_args()

url_chat = args.url

def get_kc_act():
    url = 'https://jiutian.10086.cn/auth/realms/TechnicalMiddlePlatform/protocol/openid-connect/token' #kc获取access_token的url
    user = '' #kunlun 用户名
    password = ''  #kunlun 密码

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

def send_request_and_resolve(send_data):
    json_data = json.dumps(send_data)
    global jtvlchat_access_token
    jtvlchat_access_token = check_token_expiration(jtvlchat_access_token)
    header_dict = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + jtvlchat_access_token
    }

    finished = False
    num_trys, max_trys = 0, 3
    r = None
    while not finished and (num_trys < max_trys or max_trys <= 0):
        try:
            r = requests.post(url_chat, headers=header_dict, data=json_data, timeout=20000)
            finished = True
        except requests.exceptions.ConnectionError:
            print('Connection Failed, retrying...')
            num_trys += 1
        except:
            raise
    if r is not None and r.status_code == 200:
        try:
            r_json = r.json()
            return r_json['choices'][0]['message']['content'].replace('#', '')
        except:
            error_msg = f'Error! code {r.status_code} content: {r.content}'
            return error_msg
    else:
        # try:
        #     r_json = r.json() if r is not None else None
        #     error_msg = f'Error! code {r.status_code} content: {r_json}'
        #     return error_msg
        # except:
        #     error_msg = f'Error! code {r.status_code} content: {r.content}'
        #     return error_msg
        try:
            r_json = r.json() if r is not None else None  # 如果 r 是 None，则不尝试调用 json()
            error_msg = f'Error! code {r.status_code if r is not None else "N/A"} content: {r_json if r_json is not None else "N/A"}'
            return error_msg
        except:
            error_msg = f'Error! code {r.status_code if r is not None else "N/A"} content: {r.content if r is not None else "N/A"}'
            return error_msg


def get_response(prompt, image_path, temperature, max_tokens, do_sample):
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
        "temperature": temperature,
        "do_sample": do_sample
    }
    return send_request_and_resolve(send_data)

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


print("query_dir-------",args.query_dir)
for txt_file in os.listdir(args.query_dir):
    img_folder = txt_file.split(".")[0]
    #print(img_folder)
    fq = open(os.path.join(args.query_dir ,txt_file),'r',encoding='utf-8')
    for line in fq.readlines():
        line = line.strip(' ').strip("\n")
        #print(line)
        content = line.split("\t")
        img_file = content[0]
        question = content[1].replace('Please answer yes or no', '\nAnswer the question using a single word or phrase')
        print("img_file,question:",img_file,question)
        if args.mme_image_dir:
            #print("mme_dir:",args.mme_image_dir)
            image_filepath = os.path.join(args.mme_image_dir, img_folder,'images',img_file)
            print("image_filepath:",image_filepath)
            ori_answer = get_response(prompt=question, image_path=image_filepath, temperature=args.temperature, max_tokens=args.max_tokens, do_sample=args.do_sample)
            answer = ori_answer.replace('\t',' ').replace('\n',' ')
            if not os.path.exists(args.output_dir):
                os.makedirs(args.output_dir)
            with open(os.path.join(args.output_dir,txt_file), 'a', encoding='utf-8') as f:
                new_line = line + '\t' + answer
                f.write(new_line+'\n')
    fq.close()
    
from mme_calculator import calculate_metrics
mme_cal = calculate_metrics()
mme_cal.process_result(args.output_dir, output_path=args.output_file)