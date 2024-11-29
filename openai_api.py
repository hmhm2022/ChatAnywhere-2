import requests
import winreg
import time


def get_proxy():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings") as key:
            proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
            proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")
            
            if proxy_enable and proxy_server:
                proxy_parts = proxy_server.split(":")
                if len(proxy_parts) == 2:
                    return {"http": f"http://{proxy_server}", "https": f"http://{proxy_server}"}
    except WindowsError:
        pass
    return {"http": None, "https": None}


class ChatSession:
    def __init__(self, api_key, base_url, model, system_prompt):
        """
        初始化聊天会话
        :param api_key: API密钥
        :param base_url: API基础URL
        :param model: 使用的模型名称
        :param system_prompt: 系统提示，用于设定AI角色
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.system_prompt = system_prompt
        self.message_history = []
        
    def get_full_context(self, user_message):
        """构建完整的消息上下文"""
        return [self.system_prompt] + self.message_history + [user_message]
        
    def add_to_history(self, message):
        """添加消息到历史记录"""
        self.message_history.append(message)
        
    def clear_history(self):
        """清空历史记录"""
        self.message_history = []
        
    def chat(self, user_input, temperature=0.7, max_completion_tokens=2000):
        """
        发送消息并获取回复
        :param user_input: 用户输入的消息
        :param temperature: 温度参数，控制回复的随机性
        :param max_completion_tokens: 回复的最大token数量
        """
        if self.api_key is None:
            print("api_key is None")
            return None

        # print("\n=== 当前历史记录 ===")
        # if not self.message_history:
        #     print("暂无历史记录")
        # else:
        #     for i, msg in enumerate(self.message_history, 1):
        #         print(f"{i}. {msg['role']}: {msg['content']}")
        # print("==================\n")

        user_message = {"role": "user", "content": user_input}
        message_context = self.get_full_context(user_message)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model,
            "messages": message_context,
            "temperature": temperature,
            "max_completion_tokens": max_completion_tokens,
            "stream": False
        }

        # print("\nAI: ", end='', flush=True)
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                proxies=get_proxy(),
                verify=True,
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = f"API请求错误: HTTP {response.status_code}\n{response.text}"
                print(error_msg)
                return error_msg

            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                ai_response = response_data["choices"][0]["message"]["content"]
                # print(ai_response)
                # 模拟流式输出
                # for char in ai_response:
                #     print(char, end='', flush=True)
                #     time.sleep(0.01)  # 控制输出速度
                # print("\n")
                
                if not ai_response.startswith("request error") and not ai_response.startswith("API请求错误"):
                    self.add_to_history(user_message)
                    self.add_to_history({"role": "assistant", "content": ai_response})
                
                return ai_response
            
            return None

        except Exception as e:
            error_msg = f"\n发生错误: {str(e)}"
            print(error_msg)
            return error_msg
