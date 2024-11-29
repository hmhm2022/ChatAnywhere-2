import json
import os
import time
import tkinter as tk
from tkinter import ttk
import keyboard
import win32clipboard
from openai_api import ChatSession

class ChatAnywhereApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ChatAnywhere 2")
        self.master.iconbitmap("chatgpt.ico")
        
        self.config_file = "config.json"
        self.load_config()
        self.chat_session = None
        self.master.minsize(400, 500)
        
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        
        ttk.Label(main_frame, text="ChatAnywhere", font=("Arial", 20)).grid(row=0, column=0, pady=10)
        ttk.Label(main_frame, text="使用方法:", font=("Arial", 18)).grid(row=1, column=0, pady=5)
        ttk.Label(main_frame, text="选中文字，按下Ctrl+Alt+\\开始补全\n长按Ctrl停止当前补全", 
                 font=("Arial", 15)).grid(row=2, column=0, pady=5)
        
        ttk.Label(main_frame, 
                 text="\n使用ChatAnywhere时请保证该窗口后台运行\n-----------------------------------\n设置",
                 font=("Arial", 12),
                 justify="center",
                 anchor="center").grid(row=3, column=0, pady=10, sticky="ew")
        
        settings_frame = ttk.Frame(main_frame)
        settings_frame.grid(row=4, column=0)
        main_frame.grid_columnconfigure(0, weight=1)
        
        inner_frame = ttk.Frame(settings_frame)
        inner_frame.grid(row=0, column=0, padx=20)
        settings_frame.grid_columnconfigure(0, weight=1)
        
        current_row = 0
        
        # API Key
        ttk.Label(inner_frame, text="API Key:").grid(row=current_row, column=0, sticky=tk.W)
        current_row += 1
        self.ent_apikey = ttk.Entry(inner_frame, width=52) 
        self.ent_apikey.insert(0, self.apikey)
        self.ent_apikey.grid(row=current_row, column=0, pady=(0, 10))
        current_row += 1
        
        # Base URL
        ttk.Label(inner_frame, text="API URL:").grid(row=current_row, column=0, sticky=tk.W)
        current_row += 1
        self.ent_base_url = ttk.Entry(inner_frame, width=52) 
        self.ent_base_url.insert(0, self.base_url)
        self.ent_base_url.grid(row=current_row, column=0, pady=(0, 10))
        current_row += 1
        
        # Model
        ttk.Label(inner_frame, text="Model:").grid(row=current_row, column=0, sticky=tk.W)
        current_row += 1
        self.ent_model = ttk.Entry(inner_frame, width=52) 
        self.ent_model.insert(0, self.model)
        self.ent_model.grid(row=current_row, column=0, pady=(0, 10))
        current_row += 1
        
        # 补全文字数量限制
        ttk.Label(inner_frame, text="补全文字数量限制:").grid(row=current_row, column=0, sticky=tk.W)
        current_row += 1
        self.ent_number = ttk.Entry(inner_frame, width=52) 
        self.ent_number.insert(0, str(self.complete_number))
        self.ent_number.grid(row=current_row, column=0, pady=(0, 10))
        current_row += 1
        
        # Temperature
        ttk.Label(inner_frame, text="Temperature:").grid(row=current_row, column=0, sticky=tk.W)
        current_row += 1
        self.ent_temperature = ttk.Entry(inner_frame, width=52) 
        self.ent_temperature.insert(0, str(self.temperature))
        self.ent_temperature.grid(row=current_row, column=0, pady=(0, 10))
        current_row += 1
        
        # 保持历史记录
        ttk.Label(inner_frame, text="保持历史记录:").grid(row=current_row, column=0, sticky=tk.W)
        current_row += 1
        self.keep_history_var = tk.BooleanVar(value=self.keep_history)
        self.chk_keep_history = ttk.Checkbutton(inner_frame, text="启用", variable=self.keep_history_var)
        self.chk_keep_history.grid(row=current_row, column=0, pady=(0, 10), sticky=tk.W)
        current_row += 1
        
        # 提交按钮
        self.btn_submit = ttk.Button(inner_frame, text="修改", command=self.submit)
        self.btn_submit.grid(row=current_row, column=0, pady=10)

        # 绑定快捷键
        keyboard.add_hotkey('ctrl+alt+\\', self.complete)

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.apikey = config.get('api_key')
                    self.base_url = config.get('api_url')
                    self.model = config.get('model')
                    self.complete_number = config.get('complete_number', 150)
                    self.temperature = config.get('temperature', 0.9)
                    self.keep_history = config.get('keep_history', False)
            else:
                self.apikey = "sk-xxxx"
                self.base_url = "https://api.chatanywhere.org/v1/chat/completions"
                self.model = "gpt-4o-mini"
                self.complete_number = 150
                self.temperature = 0.9
                self.keep_history = False
                self.save_config()
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")

    def save_config(self):
        config = {
            'api_key': self.apikey,
            'api_url': self.base_url,
            'model': self.model,
            'complete_number': self.complete_number,
            'temperature': self.temperature,
            'keep_history': self.keep_history
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print("配置已保存")
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")

    def submit(self):
        self.apikey = self.ent_apikey.get()
        self.base_url = self.ent_base_url.get()
        self.model = self.ent_model.get()
        self.complete_number = int(self.ent_number.get())
        self.temperature = float(self.ent_temperature.get())
        self.keep_history = self.keep_history_var.get()
        
        self.save_config()
        
        self.chat_session = None
        
        self.btn_submit["text"] = "修改成功"
        def reset():
            self.btn_submit["text"] = "修改"
        self.master.after(700, reset)
        print("修改成功")

    def get_selected_text(self):
        win32clipboard.OpenClipboard()
        try:
            old_clipboard = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except:
            old_clipboard = ''
        win32clipboard.CloseClipboard()

        while keyboard.is_pressed('alt') or keyboard.is_pressed('\\') or keyboard.is_pressed('ctrl'):
            time.sleep(0.1)

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()

        time.sleep(0.3)
        keyboard.press_and_release('ctrl+c')
        time.sleep(0.5)

        max_attempts = 3
        selected_text = ''
        for _ in range(max_attempts):
            try:
                win32clipboard.OpenClipboard()
                selected_text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                if selected_text.strip():
                    break
            except:
                win32clipboard.CloseClipboard()
                time.sleep(0.3)

        if old_clipboard:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(old_clipboard)
            win32clipboard.CloseClipboard()

        return selected_text

    def complete(self):
        try:
            selected_text = self.get_selected_text()
            if not selected_text:
                print("未能获取到选中的文本，请重试")
                return

            print("您选择补全的文本:\t", selected_text)
            keyboard.press_and_release('right')
            msg = "【请稍等，等待补全】"
            keyboard.write(msg)

            if self.chat_session is None:
                prompt_content = f"""你是一个专业的文本续写助手。
                任务要求：
                1. 仔细分析用户文本的写作风格、情感和主题
                2. 保持相同的语言风格和表达方式
                3. 确保内容的连贯性和逻辑性
                4. 补全内容控制在{self.complete_number}字以内
                """
                
                if self.keep_history:
                    prompt_content += """
                    5. 本次对话将保持历史记录
                    6. 请注意与之前的补全内容保持连贯性
                    7. 考虑整体文章的风格和主题统一
                    """
                else:
                    prompt_content += """
                    5. 本次是独立的补全
                    6. 专注于当前文本的延续
                    """
                
                prompt_content += """
                注意：直接续写，不要重复用户的输入内容，不要添加任何解释或评论。
                """
                
                self.chat_session = ChatSession(
                    api_key=self.apikey,
                    base_url=self.base_url,
                    model=self.model,
                    system_prompt={
                        "role": "system", 
                        "content": prompt_content
                    }                    
                )

            for i in range(len(msg)):
                keyboard.press_and_release('backspace')
            msg = " << 请勿其它操作，长按ctrl键终止】"
            keyboard.write("【" + msg)
            for i in range(len(msg)):
                keyboard.press_and_release('left')

            if not self.keep_history:
                self.chat_session.clear_history()
            
            response = self.chat_session.chat(selected_text)

            if response.startswith(("\n发生错误", "request error", "API请求错误")):
                print(f"\n{response}")
                keyboard.write(f" >> {response}")
                return

            for char in response:
                if keyboard.is_pressed('ctrl'):
                    print("\n--用户终止")
                    keyboard.write(" >> 用户终止")
                    return
                print(char, end="", flush=True)
                keyboard.write(char)
                time.sleep(0.01)

            print()
            keyboard.write("】")
            for i in range(len(msg)):
                keyboard.press_and_release('delete')

        except Exception as e:
            print(f"发生错误: {str(e)}")
            return

if __name__ == '__main__':
    root = tk.Tk()
    app = ChatAnywhereApp(root)
    root.mainloop()
    keyboard.unhook_all_hotkeys()
