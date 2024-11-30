# ChatAnywhere 2
使用GPT API的Copilot，支持office、word、wps等软件中使用  
在任意软件内使用快捷键补全选中文本，word和wps中都可以方便的使用  

##  在[ChatAnywhere](https://github.com/LiangYang666/ChatAnywhere)  的基础上修改的
## 特性
> 在任意软件内使用  
> 编写文档的好助手  

## 演示动图
选中文本作为上下文提示，按下快捷键`Ctrl+Alt+\`激活补全，开始后将会自动逐字输出补全的内容
1. word中使用  
![word补全演示](https://user-images.githubusercontent.com/38237931/230600283-d0b5e55f-5b07-44fa-b8e6-751ce300d1ee.gif)

2. 微信聊天中使用  
![微信补全演示](https://user-images.githubusercontent.com/38237931/230600251-4a39728c-6689-49d5-9b05-9bec6df0b6cc.gif)

## 设置界面
![image](https://github.com/user-attachments/assets/cbdc199a-e6d1-47be-bf7c-b78ced6e0e0c)

## 部署方法
```
git clone https://github.com/hmhm2022/ChatAnywhere-2
pip install -r requirements.txt 
```

## 使用方法（目前仅支持Windows）
> 1. 申请 OpenAI 官方KEY
> 2. 或者 NewAPI 等支持 OpenAI 官方调用方法的第三方中转 API KEY，这里推荐一个，[立即申请](https://github.com/chatanywhere/GPT_API_free)
> 3. 执行`main.py`，在设置窗口填写 KEY 和 URL （可以带'/v1'也可以不带），配置其他参数，点击 ‘修改’ 按钮保存设置
> 4. 任意可输入文字界面，选中文字作为上下文提示,`Ctrl+Alt+\`激活补全



