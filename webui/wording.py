from typing import Any, Dict, Optional

WORDING : Dict[str, Any] =\
{
 'Title': '# ChatTTS-增强版V3⚡️⚡️',
    'VersionDescription': '''
基于Chat-TTS项目制作。

1. 音质增强/降噪解决Chat-TTS生成时的噪音问题。
2. 支持多TXT、SRT文件批量处理。
3. 支持长文本处理，支持中英混读。可自定义切割长度。
4. 支持导出srt文件。
5. 支持调节语速、停顿、笑声、口语化程度等参数。
6. 支持导入ChatTTS Speaker音色。详情看帮助。
7. 支持储存音色配置与选项配置。方便管理。
    ''',
    'default_text':'四川美食确实以辣闻名，但也有不辣的选择。比如甜水面、赖汤圆、蛋烘糕、叶儿粑等，这些小吃口味温和，甜而不腻，也很受欢迎。',
    'BatchProcessing': '批量处理',
    'BatchProcessingInfo': '勾选以启用txt文件上传批量处理',
    'SrtProcessing': '导出Srt',
    'SrtProcessingInfo': '生成后会生成对应srt格式的字幕文件',
    'TextInputLabel': '输入文字',
    'TextInputPlaceholder': '请把字放这里...',
    'TxtFileInputLabel': '上传TXT、SRT文件',
    'TextOptionsTitle': '### 文本选项',
    'RefineText': '提炼文本',
    'RefineTextInfo': '口语化处理文本，会自动添加停顿、调整语气等。',
    'SplitText': '启用文本切分',
    'SplitTextInfo': '文本过长建议开启此选项。设定每段文本长度进行分割处理。默认为50。',
    'SegmentLength': '切分文本长度',
    'SegmentLengthInfo': '设置切分每段文本的最大字符数。',
    'ConcatenateAudio': '合成整段音频',
    'ConcatenateAudioInfo': '启用文本切割或批量时，合成所有片段为一个音频文件。',
    'Nums2Text': '数字转换',
    'Nums2TextInfo': '启用后将数字转换成汉字，避免数字朗读异常问题',
    'SeedOptionsTitle': '### 音色选项',
    'ExperimentalOption': '实验性选项',
    'ExperimentalOptionInfo': '实验性选项。开启后加强固定音色,但是音频增强过程会变慢。具体看帮助。',
    'AudioSeed': 'Audio Seed',
    'AudioSeedInfo': '音频种子',
    'EmbUpload': '上传音色',
    'GenerateAudioSeed': '随机一个音色🎲',
    'TextSeed': 'Text Seed',
    'TextSeedInfo': '文本种子。用来调节说话语气和情感，调节程度较弱，适量调节。默认值:42',
    'GenerateTextSeed': '随机文本情感🎲',
    'AudioOptionsTitle': '### 音频选项',
    'Speed': 'Speed(语速)',
    'SpeedInfo': '用于调节生成音频的总体语速。默认值:5',
    'Oral': 'oral(口语化程度)',
    'OralInfo': '用于调节生成音频的自然程度。比如会添加一些连接词:这个、啊、就，等字，让音频更加自然。默认值:2',
    'Laugh': 'laugh(笑声)',
    'LaughInfo': '用于调节生成音频的笑声程度。比如：会随机在某个地方添加笑声。默认值:0',
    'Break': 'break(停顿)',
    'BreakInfo': '用于调节生成音频的停顿程度。比如：会适当的添加停顿，值越高，停顿频率越大。默认值:0',
    'Temperature': 'Audio temperature(音频采样温度)',
    'TemperatureInfo': '较低值（接近0）会使生成的语音更确定和稳定，调高（接近1）会使生成的语音更具随机性和多样性。默认值:0.3',
    'TopP': 'top_P(音频采样概率阈值)',
    'TopPInfo': '用于控制生成内容的多样性。默认值:0.7',
    'TopK': 'top_K(音频采样词汇率)',
    'TopKInfo': '用于调节词汇概率。默认值:20',
    'AudioEnhancementTitle': '### 音频增强',
    'EnhanceAudio': 'Enhance Audio(音频增强)',
    'EnhanceAudioInfo': '增强生成后的音频质量',
    'DenoiseAudio': 'Denoise Audio(音频降噪)',
    'DenoiseAudioInfo': '对生成后的音频进行降噪处理',
    'Solver': 'ODE Solver',
    'SolverInfo': '音频增强算法。不同的算法在解决音频增强任务时会有不同的性能和效果。(Euler:速度快，质量偏低|Midpoint:速度中等，质量中等|RK4:速度慢，质量最高)',
    'Nfe': 'CFM Number',
    'NfeInfo': '控制在音频增强过程中求解器对函数的评估次数。较高的评估次数通常会带来更好的结果，但也会增加计算时间。',
    'Tau': 'CFM Temperature',
    'TauInfo': '较高的值会使增强过程更加多样化，而较低的温度会使增强结果更加稳定和确定。',
    'OutputFolderButton': '打开输出文件夹',
    'SaveNameInput': '音色名称',
    'SaveSeedButton': '保存音色配置',
    'SaveFeedback': '保存信息',
    'LoadSeedDropdown': '选择音色配置',
    'RefreshSeedsButton': '刷新配置列表',
    'ApplySeedButton': '应用配置',
    'OpenConfigFolderButton': '打开配置文件夹',
    'configmanager':'### 配置管理',
    'HelpTitle': '帮助',
    'HelpContent': '''
## 💡关于批量
批量功能目前支持TXT、SRT格式。
此版本无需注意TXT内容格式。

---

## 💡关于音色导入
支持从ChatTTS Speaker项目下载.pt音色文件导入
https://modelscope.cn/studios/ttwwwaa/ChatTTS_Speaker

---

## 💡关于导出SRT
该功能可在单文本和批量模式下使用，会为生成的音频生成对应的srt字幕文件。

---

## 🚧关于TextSeed
用来控制文本风格、情感。如果生成异常，恢复默认值42。

---

## 💡关于增强/降噪
可同时勾选增强和降噪选项，会增加处理的时长。

---

## 💡关于配置

用于保存音色种子和面板选项配置，方便多次处理。

注意：保存的.pt文件和音色的.pt文件不是同一类型。

保存的.pt文件包含音色、配置信息，所以不能上传到音色里。

保存的.pt文件可在配置管理中使用，会加载已保存的音色。

---

## 📢其他
本项目免费，拒绝倒卖。
更多功能，制作中🚧

'''
}

def get(key : str) -> Optional[str]:
	if '.' in key:
		section, name = key.split('.')
		if section in WORDING and name in WORDING[section]:
			return WORDING[section][name]
	if key in WORDING:
		return WORDING[key]
	return None