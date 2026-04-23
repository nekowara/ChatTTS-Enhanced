import os
import sys
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

# 将项目根目录加入 sys.path（Colab 环境需要）
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def main():
    # 预加载 ChatTTS 模型，避免首次生成时因加载超时导致 504
    print("⏳ 正在预加载 ChatTTS 模型（首次启动需要 1-3 分钟）...")
    try:
        from processors.model_processor import load_chat_tts
        load_chat_tts()
        print("✅ ChatTTS 模型预加载完成")
    except Exception as e:
        print(f"⚠️  模型预加载失败: {e}（将在首次生成时重试）")

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

        # 检测是否在 Colab 环境
        import os
        is_colab = 'COLAB_RELEASE_TAG' in os.environ

        if custom_server:
            demo.launch(inbrowser=not is_colab, server_name=ip_address, server_port=port, share=True)
        else:
            # Colab 环境下绑定 0.0.0.0 以确保 frpc 隧道可靠连接
            demo.launch(
                inbrowser=not is_colab,
                server_name="0.0.0.0" if is_colab else "127.0.0.1",
                server_port=7860,
                share=True
            )



if __name__ == '__main__':

    main()
