import srt
import re
from datetime import timedelta
import librosa
import os

# ---- stable-ts 对齐模型（懒加载单例） ----
_align_model = None


def _load_alignment_model():
    """
    懒加载 stable-ts Whisper base 模型（全局单例）。
    仅在首次调用 generate_srt_aligned() 时加载，避免不需要 SRT 时浪费 VRAM。
    """
    global _align_model
    if _align_model is not None:
        return _align_model

    try:
        import stable_whisper
        print("⏳ 正在加载 Whisper base 对齐模型（仅首次需要）...")
        _align_model = stable_whisper.load_model('base')
        print("✅ Whisper 对齐模型加载完成")
        return _align_model
    except ImportError:
        print("⚠️  stable-ts 未安装，将退回字数比例估算方式生成 SRT")
        return None
    except Exception as e:
        print(f"⚠️  Whisper 对齐模型加载失败: {e}，将退回字数比例估算方式生成 SRT")
        return None


def _split_text_for_subtitle(text, max_chars=25):
    """
    将一段长文本拆分为适合字幕显示的短句列表。
    策略：
      1. 优先按句末标点（。！？）拆分
      2. 如果单句仍然超过 max_chars，再按逗号/分号等拆分
      3. 过短的尾巴合并到前一条

    :param text: 原始文本段
    :param max_chars: 每条字幕的建议最大字数
    :return: 短句列表
    """
    if not text or not text.strip():
        return [text]

    text = text.strip()

    # 如果本身就足够短，直接返回
    if len(text) <= max_chars:
        return [text]

    # ---- 第一步：按句末标点拆分 ----
    # 保留标点在前一段末尾
    sentence_parts = re.split(r'([。？！.!?]+)', text)
    sentences = []
    current = ""
    for part in sentence_parts:
        if not part:
            continue
        current += part
        if re.match(r'[。？！.!?]+$', part):
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())

    # ---- 第二步：对过长的句子，在逗号/分号处再拆 ----
    result = []
    for sentence in sentences:
        if len(sentence) <= max_chars:
            result.append(sentence)
        else:
            # 在逗号、分号、冒号处拆分
            comma_parts = re.split(r'([，,；;：:]+)', sentence)
            current = ""
            for part in comma_parts:
                if not part:
                    continue
                if re.match(r'[，,；;：:]+$', part):
                    current += part
                    # 积累到一定长度就切断
                    if len(current) >= max_chars * 0.6:
                        result.append(current.strip())
                        current = ""
                else:
                    if len(current) + len(part) > max_chars and current.strip():
                        result.append(current.strip())
                        current = part
                    else:
                        current += part
            if current.strip():
                result.append(current.strip())

    # ---- 第三步：合并过短的尾巴（< 5字）到前一条 ----
    if len(result) > 1 and len(result[-1]) < 5:
        result[-2] += result[-1]
        result.pop()

    return [s for s in result if s.strip()]


def generate_srt_aligned(audio_path, full_text, output_srt_file):
    """
    使用 stable-ts forced alignment 生成精确时间戳的 SRT 字幕。
    如果 stable-ts 不可用，自动退回按字数比例估算。

    参数:
    - audio_path: 音频文件路径（合并后的完整音频或单个切片）
    - full_text: 完整的原始文本（所有段拼接，用换行符分隔）
    - output_srt_file: 输出的 SRT 文件路径
    """
    model = _load_alignment_model()

    if model is None:
        # fallback: stable-ts 不可用时退回旧方案（按字数比例估算）
        print("⚠️  退回字数比例估算方式生成 SRT")
        _generate_srt_by_ratio(audio_path, full_text, output_srt_file)
        return

    print(f"🔍 正在对音频进行强制对齐: {audio_path}")

    try:
        # 使用 stable-ts 对已知文本做 forced alignment
        result = model.align(
            audio=audio_path,
            text=full_text,
            language='zh'
        )

        # 从 alignment 结果提取 segments，生成 SRT 条目
        subtitles = []
        for segment in result.segments:
            seg_text = segment.text.strip()
            if not seg_text:
                continue

            seg_start = segment.start
            seg_end = segment.end

            # 对过长的 segment 做字幕分行
            sub_texts = _split_text_for_subtitle(seg_text)

            if len(sub_texts) == 1:
                # 短句直接作为一条字幕
                subtitles.append(srt.Subtitle(
                    index=len(subtitles) + 1,
                    start=timedelta(seconds=seg_start),
                    end=timedelta(seconds=seg_end),
                    content=sub_texts[0]
                ))
            else:
                # 长句拆分后，在该 segment 的精确时间范围内按字数比例细分
                total_chars = sum(len(s) for s in sub_texts)
                seg_duration = seg_end - seg_start
                sub_start = seg_start

                for sub_text in sub_texts:
                    char_ratio = len(sub_text) / total_chars if total_chars > 0 else 1.0 / len(sub_texts)
                    sub_duration = seg_duration * char_ratio
                    sub_end = sub_start + sub_duration

                    subtitles.append(srt.Subtitle(
                        index=len(subtitles) + 1,
                        start=timedelta(seconds=sub_start),
                        end=timedelta(seconds=sub_end),
                        content=sub_text
                    ))
                    sub_start = sub_end

        # 写入 SRT 文件
        os.makedirs(os.path.dirname(output_srt_file), exist_ok=True)
        srt_content = srt.compose(subtitles)
        with open(output_srt_file, 'w', encoding='utf-8') as f:
            f.write(srt_content)

        print(f"📝 SRT 字幕已保存（精确对齐）: {output_srt_file} ({len(subtitles)} 条字幕)")

    except Exception as e:
        print(f"⚠️  强制对齐失败: {e}，退回字数比例估算方式")
        _generate_srt_by_ratio(audio_path, full_text, output_srt_file)


def _generate_srt_by_ratio(audio_path, full_text, output_srt_file):
    """
    Fallback：当 stable-ts 不可用时，按字数比例估算时间戳生成 SRT。
    使用整段音频时长 + 整段文本做比例分配。
    """
    y, sr = librosa.load(audio_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)

    sub_texts = _split_text_for_subtitle(full_text)
    total_chars = sum(len(s) for s in sub_texts)

    if total_chars == 0:
        print("⚠️  文本为空，跳过 SRT 生成")
        return

    subtitles = []
    sub_start = 0.0
    for sub_text in sub_texts:
        char_ratio = len(sub_text) / total_chars
        sub_duration = duration * char_ratio
        sub_end = sub_start + sub_duration

        subtitles.append(srt.Subtitle(
            index=len(subtitles) + 1,
            start=timedelta(seconds=sub_start),
            end=timedelta(seconds=sub_end),
            content=sub_text
        ))
        sub_start = sub_end

    os.makedirs(os.path.dirname(output_srt_file), exist_ok=True)
    srt_content = srt.compose(subtitles)
    with open(output_srt_file, 'w', encoding='utf-8') as f:
        f.write(srt_content)

    print(f"📝 SRT 字幕已保存（比例估算）: {output_srt_file} ({len(subtitles)} 条字幕)")


def generate_srt_from_audio_segments(audio_segments, text_segments, output_srt_file):
    """
    [旧方案 - 保留用于兼容] 基于多个音频切片 + 字数比例生成 SRT。

    流程：
    1. 用 librosa 获取每个音频切片的真实时长
    2. 将对应的文本段拆分为短句（适合字幕显示）
    3. 在该切片的时间范围内，按字数比例分配每条短句的时间
    4. 输出标准 SRT 文件

    参数:
    - audio_segments: 每段音频文件的路径列表
    - text_segments: 每段音频对应的原始文本内容列表
    - output_srt_file: 输出的 SRT 文件路径
    """
    subtitles = []
    current_time = 0.0  # 全局时间游标（秒）

    for audio_path, text in zip(audio_segments, text_segments):
        # 获取音频切片的真实时长
        y, sr = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)

        segment_start = current_time
        segment_end = segment_start + duration

        # 将这段文本拆分为适合字幕的短句
        sub_texts = _split_text_for_subtitle(text)

        # 按字数比例分配时间
        total_chars = sum(len(s) for s in sub_texts)
        if total_chars == 0:
            current_time = segment_end
            continue

        sub_start = segment_start
        for sub_text in sub_texts:
            char_ratio = len(sub_text) / total_chars
            sub_duration = duration * char_ratio
            sub_end = sub_start + sub_duration

            subtitles.append(srt.Subtitle(
                index=len(subtitles) + 1,
                start=timedelta(seconds=sub_start),
                end=timedelta(seconds=sub_end),
                content=sub_text
            ))
            sub_start = sub_end

        current_time = segment_end

    # 写入 SRT 文件
    os.makedirs(os.path.dirname(output_srt_file), exist_ok=True)
    srt_content = srt.compose(subtitles)
    with open(output_srt_file, 'w', encoding='utf-8') as f:
        f.write(srt_content)

    print(f"📝 SRT 字幕已保存: {output_srt_file} ({len(subtitles)} 条字幕)")


# ---- 以下为批量模式读取文件的工具函数（不变） ----

def process_srt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()
    subtitles = list(srt.parse(srt_content))
    subtitle_text = "\n".join([subtitle.content for subtitle in subtitles])
    return subtitle_text


def process_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def process_file(file_path):
    results = ''
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.srt':
        results = process_srt_file(file_path)
    elif file_ext == '.txt':
        results = process_txt_file(file_path)
    else:
        results = "Unsupported file type"
    return results