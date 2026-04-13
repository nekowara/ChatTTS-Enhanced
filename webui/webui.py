import os
import sys
import threading
import gradio as gr
from wording import get
import batch_option
import text_options
import seed_option
import aduio_option
import enhance_option
import output_option
import config_option
from webuiutils import read_config, get_server_config

# 将项目根目录加入 sys.path，以便导入 srt_watcher
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)



def main():
    # 启动 SRT 字幕后处理监控（后台守护线程）
    try:
        from srt_watcher import watch_loop as srt_watch_loop
        srt_thread = threading.Thread(target=srt_watch_loop, daemon=True)
        srt_thread.start()
        print("✅ SRT 字幕后处理监控已启动")
    except ImportError:
        print("⚠️  srt_watcher.py 未找到，SRT 后处理监控未启动")

    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown(get('Title'))
        gr.Markdown(get('VersionDescription'))
        with gr.Row():
            with gr.Column():
                batch_option.render()
                with gr.Row():
                    gr.Markdown(get('TextOptionsTitle'))
                text_options.render()
                with gr.Row():
                    gr.Markdown(get('SeedOptionsTitle'))
                seed_option.render()
                with gr.Row():
                    gr.Markdown(get('AudioOptionsTitle'))
                aduio_option.render()
                with gr.Row():
                    gr.Markdown(get('AudioEnhancementTitle'))
                enhance_option.render()

            with gr.Column():
                output_option.render()
                gr.Markdown(get('configmanager'))
                config_option.render()
                with gr.Accordion(get('HelpTitle'), open=False):
                    gr.Markdown(get('HelpContent'))
                    with gr.Row():
                        gr.Markdown(" ")
                    with gr.Row():
                        gr.Markdown(" ")
                with gr.Row():
                    gr.Markdown('🔧项目地址:https://github.com/CCmahua/ChatTTS-Enhanced')

        batch_option.listen()
        text_options.listen()
        seed_option.listen()
        aduio_option.listen()
        enhance_option.listen()
        output_option.listen()

        config = read_config('config.ini')
        custom_server, ip_address, port = get_server_config(config)
        if custom_server:
            demo.launch(inbrowser=True, server_name=ip_address, server_port=port, share=True)
        else:
            demo.launch(inbrowser=True, share=True)



if __name__ == '__main__':

    main()
