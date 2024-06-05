import argparse as ap
import base64
import json
import os
import time
import requests
import jwt
import hashlib


parser = ap.ArgumentParser()
parser.add_argument("--url", type=str, default='')
parser.add_argument("--query-dir", type=str, default='mme_queries')
parser.add_argument("--output-dir", default='outputs_token', type=str)
parser.add_argument("--output-file", default='mme_results_token.txt', type=str)
parser.add_argument("--mme-image-dir", type=str, default='mme_images')
parser.add_argument("--temperature", type=float, default=0.0)
parser.add_argument("--max-tokens", type=int, default=64)
parser.add_argument('--do-sample', action='store_true', default=False)
args = parser.parse_args()

url_chat = args.url

def get_kc_act():
    url = '' #请填写kc获取access_token的url
    user = '' #请填写用户名
    password = ''  #请填写密码

    client_id = 'kunlun-front'
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = 'grant_type=' + 'password&username=' + user + '&password=' + password + '&scope=openid&client_id=' + client_id
    response = requests.request("POST", url, headers=headers, data=payload)
    access_keys = {}

    access_keys['access_token'] = response.json()["access_token"]
    access_keys['refresh_token'] = response.json()["access_token"]
    #生成的access_keys需记录。尤其refresh_token。
    return access_keys

#检测access_token是否过期，如果过期就生成一个新的
def check_token_expiration(access_keys):
        access_token = access_keys.get('access_token')
        refresh_token = access_keys.get('refresh_token')
        access_token_jwt = jwt.decode(access_token, key='kunlun-front', algorithms='HS256', options={"verify_signature": False})
        refresh_token_jwt = jwt.decode(refresh_token, key='kunlun-front', algorithms='HS256', options={"verify_signature": False})
        exp_access = int(access_token_jwt["exp"])
        exp_refresh = int(refresh_token_jwt["exp"])
        local_time = time.time()
        
        if local_time >= exp_access and local_time >= exp_refresh:
                #print('step1 : All certificates expires')
                #如access_token 和 refresh_token 均失效，需要重新调用get_kc_act()方法生成新的tokens。
                return  get_kc_act()
        elif local_time >= exp_access and local_time <= exp_refresh:
                #print('step2 : Access_token certificate expires')
                #如access_token 失效，refresh_token未失效，可以通过refresh_token重新获取access_token和refresh_token 刷新有有效期。
                return get_access_token_by_refresh_token(refresh_token)
        elif local_time <= exp_access:
                #print('step3 : Access_token certificate works')
                #如 access_token 未失效，返回access_token
                return access_keys
        elif local_time >= exp_refresh:
                #print('step4 : Refresh_token certificate expires')
                #如 refresh_token 失效，返回get_kc_act()
                return get_kc_act()


def get_access_token_by_refresh_token(refresh_token):

        url = ''  #请填写kc获取access_token的url
        payload = 'client_id=kunlun-front&grant_type=refresh_token&scope=openid&refresh_token=' + refresh_token 
        headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        get_accesses = {}
        get_accesses['access_token'] = response.json()["access_token"]
        get_accesses['refresh_token'] = response.json()["access_token"]
        return get_accesses




def send_request_and_resolve(send_data, image_file=None):
    jtvlchat_access_token = get_kc_act()
    jtvlchat_access_token = check_token_expiration(jtvlchat_access_token).get('access_token')
    
    header_dict = {
        'Authorization': 'Bearer ' + jtvlchat_access_token
    }

    finished = False
    num_trys, max_trys = 0, -1
    while not finished and (num_trys < max_trys or max_trys <= 0):
        try:
            if image_file:
                r = requests.post(url_chat, headers=header_dict, data=send_data, files=image_file, timeout=20000)
            else:
                r = requests.post(url_chat, headers=header_dict, data=send_data, timeout=20000)
            if r.status_code == 200 and r.json()['code'] == 20000:
                finished = True
        except requests.exceptions.ConnectionError:
            print('Connection Failed, retrying...')
            num_trys += 1
        except:
            raise
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
    with open(image_path, 'rb') as fmd5:
        hash_md5 = hashlib.md5()
        hash_md5.update(fmd5.read())
        md5_image = str(hash_md5.hexdigest())
    send_data = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "do_sample": do_sample,
        "md5_image": md5_image
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
            image_filepath = os.path.join(args.mme_image_dir, img_folder,'images',img_file)
            print("image_filepath:",image_filepath)
            ori_answer = get_response(prompt=question, image_path=image_filepath, temperature=args.temperature, max_tokens=args.max_tokens, do_sample=args.do_sample)
            answer = ori_answer.replace('\t',' ').replace('\n',' ')
            print("answer:", answer)
            if not os.path.exists(args.output_dir):
                os.makedirs(args.output_dir)
            with open(os.path.join(args.output_dir,txt_file), 'a', encoding='utf-8') as f:
                new_line = line + '\t' + answer
                f.write(new_line+'\n')
    fq.close()
    
from mme_calculator import calculate_metrics
mme_cal = calculate_metrics()
mme_cal.process_result(args.output_dir, output_path=args.output_file)
