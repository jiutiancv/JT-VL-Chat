# JT-VL-Chat
JT-VL-Chat是一个多模态大模型。
# 更新日志
2024-06-03：发布推理API。
# 快速上手
## 访问API  
登录https://jiutian.10086.cn/portal/#/home, 右上角注册用户信息。待审核通过后，在代码中填写用户名和密码，即可获得access_token并访问API。  
API地址：https://jiutian.10086.cn/kunlun/ingress/api/h3t-eeceff/92390745235a40a484d850be19e1f8b4/ai-9072cb8293e94981b0b86aebb87d0002/service-8443a3d1e7af4ca384695b538e945d7f/v1/chat/completions
## 推理   
首先将用户名和密码填写到inference.py中，然后：  
```python
python inference.py --image-file xxx --query xxx --url ${API地址}
```
## MME评测
下载[MME](https://pan.baidu.com/s/1wb0fkmNN_xI1OYvJzuseEA)评估图片和评估问题（提取码：7431），将图片放入mme_images文件夹中，问题放入mme_queries文件夹中  
将用户名和密码填写到mme_eval.py中，然后：  
```python
python mme_eval.py --url ${API地址}
```
结果文件保存在outputs文件夹中，最后的指标结果在mme_results.txt中
