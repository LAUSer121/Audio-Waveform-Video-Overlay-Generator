#!/usr/bin/env python3
"""
Audio Waveform Video Overlay Generator
将音频波形转换为透明背景视频的独立脚本
"""

import argparse
import os
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

# 默认参数配置
DEFAULT_CONFIG = {
    "width": 1920,          # 视频宽度
    "height": 400,          # 视频高度
    "wave_color": "#C04851",# 波形颜色
    "fps": 30,              # 默认帧率
    "temp_dir": "_frames",  # 临时帧目录
    "ffmpeg_path": "ffmpeg" # 自动检测系统路径
}

class AudioWaveformConverter:
    def __init__(self, config):
        """初始化转换器"""
        self.config = config
        self._validate_ffmpeg()
        self._setup_matplotlib()
        
    def _validate_ffmpeg(self):
        """验证FFmpeg是否可用"""
        try:
            subprocess.run([self.config["ffmpeg_path"], "-version"],
                          check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(f"错误：找不到FFmpeg，请安装或使用绝对路径指定")
            print("下载地址：https://ffmpeg.org/download.html")
            sys.exit(1)
    
    def _setup_matplotlib(self):
        """配置Matplotlib生成透明图像"""
        plt.ioff()
        self.fig = plt.figure(
            figsize=(self.config["width"]/100, self.config["height"]/100),
            dpi=100,
            facecolor=(0,0,0,0)  # 透明背景
        )
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.axis('off')
    
    def _hex_to_rgba(self, hex_color):
        """将十六进制颜色转换为Matplotlib支持的RGBA元组"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4)) + (1,)
    
    def _render_frame(self, data, frame_idx, sample_rate):
        """生成单个透明帧"""
        self.ax.clear()
        
        # 计算时间轴（秒）
        duration = len(data) / sample_rate
        time = np.linspace(0, duration, len(data))
        
        # 绘制波形
        self.ax.plot(time, data,
                    color=self._hex_to_rgba(self.config["wave_color"]),
                    linewidth=1.5,
                    antialiased=True,
                    solid_joinstyle='round')
        
        # 设置坐标范围
        self.ax.set_xlim(0, duration)
        self.ax.set_ylim(np.min(data)*1.1, np.max(data)*1.1)
        
        # 保存为透明PNG
        frame_path = Path(self.config["temp_dir"]) / f"frame_{frame_idx:05d}.png"
        plt.savefig(frame_path, 
                   transparent=True,
                   bbox_inches='tight',
                   pad_inches=0)
    
    def convert(self, input_wav, output_video):
        """执行转换流程"""
        # 准备临时目录
        temp_dir = Path(self.config["temp_dir"])
        temp_dir.mkdir(exist_ok=True)
        
        try:
            with wave.open(str(input_wav), 'rb') as wav:
                # 读取音频参数
                sample_rate = wav.getframerate()
                num_channels = wav.getnchannels()
                total_frames = wav.getnframes()
                chunk_size = sample_rate // self.config["fps"]
                
                frame_count = 0
                while True:
                    # 读取音频数据块
                    raw_data = wav.readframes(chunk_size)
                    if not raw_data:
                        break
                    
                    # 转换为numpy数组
                    data = np.frombuffer(raw_data, dtype=np.int16)
                    
                    # 多声道转单声道
                    if num_channels > 1:
                        data = data.reshape(-1, num_channels).mean(axis=1)
                    
                    # 生成波形帧
                    self._render_frame(data, frame_count, sample_rate)
                    frame_count += 1
                    print(f"进度: {wav.tell()/total_frames:.1%}", end='\r')
            
            # 使用FFmpeg合成视频
            self._encode_video(input_wav, output_video, frame_count)
            
        finally:
            # 清理临时文件
            for f in temp_dir.glob("*.png"):
                f.unlink()
            temp_dir.rmdir()
    
    def _encode_video(self, input_wav, output_video, total_frames):
        """调用FFmpeg编码视频"""
        ffmpeg_cmd = [
            self.config["ffmpeg_path"], '-y',
            '-framerate', str(self.config["fps"]),
            '-i', str(Path(self.config["temp_dir"]) / "frame_%05d.png"),
            '-i', str(input_wav),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '20',
            '-pix_fmt', 'yuva420p',
            '-shortest',
            '-s', f'{self.config["width"]}x{self.config["height"]}',
            str(output_video)
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"\n成功生成视频：{output_video}")
        except subprocess.CalledProcessError as e:
            print(f"\n视频编码失败：{str(e)}")
            sys.exit(1)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="生成透明背景的音频波形视频叠加层",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-i', '--input', required=True,
                      help="输入WAV音频文件路径")
    parser.add_argument('-o', '--output', default="output.mov",
                      help="输出视频文件路径")
    parser.add_argument('-w', '--width', type=int, default=DEFAULT_CONFIG["width"],
                      help="视频宽度（像素）")
    parser.add_argument('--height', type=int, default=DEFAULT_CONFIG["height"],
                      help="视频高度（像素）")
    parser.add_argument('--color', default=DEFAULT_CONFIG["wave_color"],
                      help="波形颜色（十六进制值，如#C04851）")
    parser.add_argument('--fps', type=int, default=DEFAULT_CONFIG["fps"],
                      help="输出视频帧率")
    parser.add_argument('--ffmpeg', default=DEFAULT_CONFIG["ffmpeg_path"],
                      help="FFmpeg可执行文件路径")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # 初始化配置
    config = {
        "width": args.width,
        "height": args.height,
        "wave_color": args.color,
        "fps": args.fps,
        "ffmpeg_path": args.ffmpeg,
        "temp_dir": DEFAULT_CONFIG["temp_dir"]
    }
    
    # 验证输入文件
    if not Path(args.input).exists():
        print(f"错误：输入文件 {args.input} 不存在")
        sys.exit(1)
    
    # 执行转换
    converter = AudioWaveformConverter(config)
    converter.convert(args.input, args.output)
