"""
SRT 字幕后处理监控脚本
功能：定时扫描 output_audio 目录下的 .srt 文件，
将一个长字幕条目按标点符号拆分为多个短条目（时间按字数比例分配）。
可以独立运行，也可以由 webui.py 以后台线程方式启动。
"""
import os
import time
import srt
import re
from datetime import timedelta

# 监控目录（相对于项目根目录）
WATCH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_audio")
PROCESSED_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_srt_files.log")


def get_processed_files():
    """获取已处理文件列表"""
    if not os.path.exists(PROCESSED_LOG):
        return set()
    with open(PROCESSED_LOG, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)


def mark_processed(filepath):
    """标记文件为已处理"""
    with open(PROCESSED_LOG, "a", encoding="utf-8") as f:
        f.write(filepath + "\n")


def process_subtitle(subtitle):
    """
    将一个长字幕条目按标点符号拆分为多个短条目。
    时间根据字数比例分配。
    """
    text = subtitle.content.strip()
    # 按照常见的中英文标点进行切分，保留标点符号
    parts = re.split(r'([，。！？；：,.!?;:])', text)

    segments_text = []
    current = ""
    for part in parts:
        if part:
            current += part
            if re.match(r'[，。！？；：,.!?;:]', part):
                segments_text.append(current.strip())
                current = ""
    if current.strip():
        segments_text.append(current.strip())

    segments_text = [s for s in segments_text if s]

    if len(segments_text) <= 1:
        return [subtitle]

    total_duration = subtitle.end - subtitle.start
    total_chars = sum(len(s) for s in segments_text)
    if total_chars == 0:
        return [subtitle]

    new_subs = []
    current_start = subtitle.start
    for stext in segments_text:
        char_count = len(stext)
        duration = timedelta(seconds=total_duration.total_seconds() * (char_count / total_chars))
        current_end = current_start + duration
        new_subs.append(srt.Subtitle(index=0, start=current_start, end=current_end, content=stext))
        current_start = current_end

    return new_subs


def process_file(filepath):
    """处理单个 SRT 文件"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        subs = list(srt.parse(content))
        new_subs = []
        for sub in subs:
            new_subs.extend(process_subtitle(sub))

        for i, sub in enumerate(new_subs):
            sub.index = i + 1

        new_content = srt.compose(new_subs)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✅ SRT 已处理: {os.path.basename(filepath)} ({len(subs)} -> {len(new_subs)} 条字幕)")
        return True
    except Exception as e:
        print(f"❌ SRT 处理失败: {filepath} - {e}")
        return False


def watch_loop():
    """主监控循环，每 5 秒扫描一次"""
    print(f"👁️  SRT 监控已启动，监控目录: {WATCH_DIR}")
    while True:
        if os.path.exists(WATCH_DIR):
            processed = get_processed_files()
            for root, _, files in os.walk(WATCH_DIR):
                for file in files:
                    if file.endswith(".srt"):
                        filepath = os.path.join(root, file)
                        if filepath not in processed:
                            if process_file(filepath):
                                mark_processed(filepath)
        time.sleep(5)


if __name__ == "__main__":
    watch_loop()
