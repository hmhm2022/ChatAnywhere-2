from openai import OpenAI
import httpx
import winreg

def get_proxy():
    """获取Windows系统代理设置"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings") as key:
            proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
            proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")
            
            if proxy_enable and proxy_server:
                return {
                    "http://": f"http://{proxy_server}",
                    "https://": f"http://{proxy_server}"
                }
    except WindowsError:
        pass
    return None

class ChatSession:
    def __init__(self, api_key: str, base_url: str, model: str, system_prompt: dict):
        """
        初始化聊天会话
        :param api_key: OpenAI API密钥
        :param base_url: API基础URL
        :param model: 使用的模型
        :param system_prompt: 系统提示词，格式为{"role": "system", "content": "xxx"}
        """
        http_client = httpx.Client(
            proxies=get_proxy(),
            timeout=30.0,
            verify=False
        )
        
        self.model = model
        self.system_prompt = system_prompt
        
        base_url = base_url.rstrip('/')
        if not base_url.endswith('/v1'):
            base_url = f"{base_url}/v1"
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client
        )
        
        self.messages_history = []

    def add_to_history(self, message):
        """添加消息到历史记录"""
        self.messages_history.append(message)

    def clear_history(self):  
        """清空历史记录"""      
        self.messages_history = []

    def chat(self, user_input: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        发送消息并获取回复
        :param user_input: 用户输入的消息
        :param temperature: 温度参数
        :param max_tokens: 回复的最大token数量
        :return: AI的回复文本
        """
        try:
            messages = [self.system_prompt] + self.messages_history + [{"role": "user", "content": user_input}]

            print("\n=== 当前对话记录 ===")
            if not self.messages_history:
                print("新对话 或者 未开启记住历史对话")
            for i, msg in enumerate(messages, 1):
                print(f"{i}. {msg['role']}: {msg['content']}")
            print("==================\n")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            reply = response.choices[0].message.content
            
            if not reply.startswith(("\n发生错误", "request error", "API请求错误")):
                self.add_to_history({"role": "user", "content": user_input})
                self.add_to_history({"role": "assistant", "content": reply})
            
            return reply

        except Exception as e:
            error_msg = f"""
发生错误:
- 错误类型: {type(e).__name__}
- 错误信息: {str(e)}
- API地址: {self.client.base_url}
- 使用模型: {self.model}
"""
            return error_msg
