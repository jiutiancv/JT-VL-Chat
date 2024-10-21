# JT-VL-Chat
JT-VL-Chat是一个多模态大模型。
# 更新日志
2024-06-05: V1.0版本模型，同时发布推理API。  

2024-08-31: V2.0版本模型。

2024-10-21: V3.0版本模型，更新了推理API的访问方式。
# 快速上手
## 访问API  
V2.0版本模型：登录https://jiutian.10086.cn/portal/#/home, 右上角注册用户信息。待审核通过后，在代码中填写用户名、密码以及获取access_token的url，即可访问服务API。  
V3.0版本模型：直接使用代码中提供的app_code和url，即可访问服务API。

## 推理 
V2.0版本模型：
首先将用户名、密码以及获取access_token的url填写到inference.py中，然后：  
```python
python inference_v2.py --image-file xxx --query xxx --url ${服务API地址}
```
V3.0版本模型：
```python
python inference_v3.py --image-file xxx --query xxx 
```
## V2.0版本模型MME评测
下载[MME](https://pan.baidu.com/s/1wb0fkmNN_xI1OYvJzuseEA)评估图片和评估问题（提取码：7431），将图片放入mme_images文件夹中，问题放入mme_queries文件夹中  
将用户名和密码填写到mme_eval_v2.py中，然后：  
```python
python mme_eval_v2.py --url ${服务API地址}
```
结果文件保存在outputs文件夹中，最后的指标结果在mme_results.txt中  
JT-VL-Chat-V2.0在perception任务上得到了1743.11分，cognition任务上得到了461.43分。

