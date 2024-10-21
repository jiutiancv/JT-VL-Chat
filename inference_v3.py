#!/usr/bin/env python3
# encoding: utf-8

import os, sys
import base64
import time
import json
import argparse as ap
import requests


url_chat = 'https://jiutian.10086.cn/kunlun/ingress/api/h3t-eeceff/92390745235a40a484d850be19e1f8b4/ai-5d7ae47ec93f4280953273c4001aafee/service-7544ea5ee3e841ad9d01e7af44acef7c/v1/chat/completions'

def send_request_and_resolve(send_data):
    json_data = json.dumps(send_data)
    app_code = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5ZGQwNmQ2ZjU4YTU0ZGY0OGEzNjRhMjQyNGMwODEyNSIsImlzcyI6ImFwaS1hdXRoLWtleSIsImV4cCI6NDg4MjkwNDA3OX0.k5t_T-955xWMndzBbx4WQQNAgm5DpMos9mHm7vkFipQ3yebCFMfyufpSxORSfEVpBaDS3Nly0dd8ygQYGnDgIQcC72vQ1xtkjCP49LNcqlceoET4rGc1zwRi76XLPSGFES4GcwvEmr7Ilth7XtqZNxcDF_Z7HyHyf1-zF0JIQETYSoxenqLU-gNteNfqRUnlyCgaKh03DscAbYvtoMUxEaFa2ZqyRSwekdHI_SPKCq9aC9G19yDPHTjeiwl1ubtyC5uMy5pERn_ClRsZS3Wyb-GmD5QQsFofrWvCiU_fVJuUiez39pYZvEP8awH0R9B7SkpQ4XOzj3fdytTPYy3g6g'
    header_dict = {'Content-Type': 'application/json','Authorization': 'Bearer ' + app_code}

    r = requests.post(url_chat, headers=header_dict, data=json_data, timeout=3000)
    print("status code",r.status_code)
    try:
        r_json = r.json()
        output = r_json['choices'][0]['message']['content']
        print(output)
        return r_json
        # return r_json['choices'][0]['message']['content']
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

def test(prompt, image, temperature, max_tokens):
    return f"prompt: {prompt} ; max_tokens: {max_tokens} ; temperature: {temperature}"

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-i', type=str, default='test.jpg')
    parser.add_argument('-q', type=str, default="describe the image.")
    parser.add_argument('-t', '--temperature', type=float, default=0.7)
    parser.add_argument('-m', '--max-tokens', type=int, default=256)
    args = parser.parse_args()

    if args.i:
        result = get_response(args.q, args.i, args.temperature, args.max_tokens)
    else:
        result = get_response_no_image(args.q, args.temperature, args.max_tokens)
    print(result)
