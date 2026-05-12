# ================= 1. 环境准备 =================
!git clone -q https://github.com/nekowara/ChatTTS-Enhanced
%cd /content/ChatTTS-Enhanced

# 安装依赖
!pip install torch==2.5.1 torchaudio==2.5.1 torchvision --index-url https://download.pytorch.org/whl/cu118
!pip install transformers==4.44.2
!pip install -q omegaconf vocos vector_quantize_pytorch gradio==5.49.1 cn2an pypinyin openai jieba WeTextProcessing python-dotenv deepspeed srt stable-ts openai-whisper

# ================= 2. 建立隧道并启动 =================
import subprocess
import urllib
import time

print("\n🚀 正在配置环境并获取双通道链接...")
# 安装 localtunnel
!npm install -q -g localtunnel

# 获取并打印验证密码
ip_password = urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip("\n")
print("\n==================================================================")
print(f"👉 【备用通道密码】: {ip_password}")

# 将 localtunnel 挂在后台运行，并将链接输出到一个文件
subprocess.Popen("npx localtunnel --port 7860 > lt_url.txt", shell=True)

# 稍微等 3 秒钟让 localtunnel 生成网址
time.sleep(3)
with open("lt_url.txt", "r") as f:
    lt_url = f.read().strip()

print(f"👇 【备用通道网址】: {lt_url}")
print("==================================================================\n")

print("🔥 正在正常启动 ChatTTS 服务 (你将在这里看到进度和官方 gradio 链接)")
# 在前台正常启动服务！
!python webui/webui.py