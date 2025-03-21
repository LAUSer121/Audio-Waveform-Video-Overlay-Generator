# AudioWave Visualizer 🎧✨

**将音频波形实时渲染为透明视频叠加层的开源解决方案**  
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![FFmpeg Required](https://img.shields.io/badge/FFmpeg-5.0%2B-orange?logo=ffmpeg)](https://ffmpeg.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)

![Waveform Demo](docs/demo.gif)  
*(示例：动态波形叠加在视频上的效果)*

## 🌟 核心特性

- **实时波形渲染**  
  基于音频采样数据生成逐帧动画，精确同步时间轴
- **透明背景支持**  
  输出带Alpha通道的视频文件（MOV/MP4/AVI）
- **专业级视觉效果**  
  - 智能垂直幅度缩放
  - 抗锯齿平滑处理
  - 可定制分辨率（最高8K）
- **跨平台兼容**  
  完美支持Windows/macOS/Linux系统

## 🚀 快速入门

### 安装依赖
```bash
# 基础依赖
pip install numpy matplotlib

# 可选：进度条支持
pip install tqdm
```

### 基本用法
```bash
python main.py -i input.wav -o output.mov
```

### 高级参数
```bash
# 自定义分辨率与颜色
python main.py \
  -i sample.wav \
  -o output.avi \
  --width 2560 \
  --height 600 \
  --color "#00FF00" \
  --fps 60
```

## 🛠️ 技术参数

| 功能               | 支持范围                  |
|--------------------|--------------------------|
| 输入音频格式       | WAV (16/24/32-bit)       |
| 输出视频编码       | ProRes/QTRLE/H.264/VP9   |
| 最大分辨率         | 8192×4320 (8K)           |
| 帧率范围           | 24-120 FPS               |
| 透明度支持         | Alpha Channel (RGBA/YUVA)|

## 🌍 跨平台支持

| 操作系统 | 验证版本 | 注意事项                |
|----------|----------|-----------------------|
| Windows  | 10/11    | 需手动指定FFmpeg路径    |
| macOS    | 12+      | 自带ProRes编码支持      |
| Linux    | Ubuntu 20.04+ | 建议使用AppImage版FFmpeg |

## 🧩 扩展功能

### 自定义波形样式
```python
# 在_render_frame方法中修改以下参数：
self.ax.plot(time, data,
            linewidth=2.0,        # 波形线宽
            color=(0.9, 0.2, 0.4), # RGB颜色 (0-1)
            alpha=0.9,            # 透明度
            linestyle=':')        # 线型样式
```

### 多轨道支持（实验性）
```bash
# 混合多个音频轨道
python main.py -i track1.wav track2.wav -o combined.mp4
```
