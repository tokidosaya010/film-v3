# Film v3 · 浓郁胶片调色

[简体中文](#简体中文) · [English](#english)

Film v3 是一项可在 Codex 中调用的照片调色技能。配方以富士 **CLASSIC Neg.（经典负片）** 为灵感，采用更深的青蓝阴影、柔和的奶油金高光和较强的中间调反差，适合街拍、夜景人像和日常纪实。

绿叶收向橄榄灰，蓝色偏青，红色相对保留饱和度。暖肤色区域的调色幅度较轻，胶片颗粒随画面亮度变化。此配方为独立实现，成片效果会与富士机内模拟有所差异。

### 在 Codex 中安装

1. 在仓库页面选择 **Code → Download ZIP**，下载并解压。
2. 将解压后的仓库文件夹放到本机的 `~/.agents/skills/film-v3/`。确认技能入口位于 `~/.agents/skills/film-v3/SKILL.md`。
3. 新建一个本机 Codex 对话，上传照片并输入「用 `$film-v3` 给这张照片调色」。

可以直接上传一张或多张 `.CR2`、`.JPG` 或 `.JPEG` 文件。支持图片输出的客户端可以在聊天中显示成片预览。全尺寸成片会另存为独立文件。

### 命令行用法

在仓库目录运行：

```bash
python -m pip install -r requirements.txt
python scripts/grade.py input.CR2 output-film-v3.jpg
```

处理 JPEG 时，将输入路径换为 `input.jpg`。脚本会保留构图和像素尺寸，按正确方向输出，嵌入 sRGB 配置文件，并拒绝覆盖已有文件。

### 格式与验证

已用 **Canon CR2** 和 **JPEG** 实测。脚本也支持读取 PNG 和 TIFF，并可输出 JPEG、PNG 或 TIFF。RAW 使用相机白平衡解码，同一场景的 RAW 与机内 JPEG 调色后可能有不同的亮度和色彩。


Film v3 is a photo-grading skill for Codex inspired by Fujifilm **CLASSIC Neg.** It gives street, nighttime portrait, and documentary photos deeper teal-blue shadows, soft golden highlights, and stronger midtone contrast.

Greens shift toward muted olive, blues lean toward cyan, and reds retain more of their saturation. Warm skin tones receive gentler grading, while fine grain varies with brightness. Film v3 is an independent interpretation, so results can differ from Fujifilm’s in-camera simulation.

### Install in Codex

1. Select **Code → Download ZIP** on the repository page and extract the archive.
2. Place the extracted repository folder at `~/.agents/skills/film-v3/` on your computer. Confirm that `SKILL.md` is at `~/.agents/skills/film-v3/SKILL.md`.
3. Start a local Codex conversation, attach a photo, and ask “Use `$film-v3` to grade this photo.”

Attach one or more `.CR2`, `.JPG`, or `.JPEG` files directly. Clients that support image output can display previews in chat. Full-resolution results are saved as separate files.

### Command-line usage

From the repository directory:

```bash
python -m pip install -r requirements.txt
python scripts/grade.py input.CR2 output-film-v3.jpg
```

For JPEG input, replace `input.CR2` with `input.jpg`. The script preserves framing and pixel dimensions, applies the correct orientation, embeds an sRGB profile, and refuses to overwrite existing files.

### Formats and verification

Tested with **Canon CR2** and **JPEG**. The script also reads PNG and TIFF and can export JPEG, PNG, or TIFF. RAW files are decoded using the camera’s white balance, so grades from RAW and in-camera JPEG versions of the same scene can differ in brightness and color.
