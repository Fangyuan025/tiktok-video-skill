# tiktok-video — 一键生成抖音/TikTok 短视频的通用 Agent Skill

**One-line brief in → finished vertical video out.** An [Agent Skills](https://code.claude.com/docs/en/skills)-standard
skill that lets ANY capable AI agent (Claude Code, Cursor, Codex CLI, Gemini CLI, OpenCode…)
produce complete, publish-ready TikTok / 抖音 / Shorts / Reels videos:

> 用户一句话需求 → agent 写文案分镜 → 自动联网搜索并下载素材 → TTS 配音(中/英)→
> 逐字卡拉OK字幕 → 配乐 + 响度标准化 → 直出 1080×1920 成片 MP4

<table><tr>
<td>🎬 端到端全自动</td>
<td>🆓 <b>零 API key 可用</b>(可选 Pexels/Pixabay key 升级实拍视频素材)</td>
<td>🌏 中英双语</td>
</tr></table>

## 效果 / What it makes

- 1080×1920(或 16:9 / 1:1)、30fps、H.264 + AAC、响度 -15 LUFS(平台标准)
- 营销号风格:前 3 秒大字 Hook 标题 → 逐字高亮字幕 → Ken Burns 动效 → BGM 自动闪避人声 → 结尾 CTA
- 免费素材源:Openverse (Flickr/博物馆)、Wikimedia Commons、NASA;音乐:Kevin MacLeod (CC-BY)
- 自动生成素材署名文本,合规使用 CC 素材

## 安装 / Install

需要 `ffmpeg`(任意常规构建,无需 libass)和 `python3`:

```bash
# Claude Code
git clone <this-repo> ~/.claude/skills/tiktok-video
# 其他支持 SKILL.md 标准的 agent:clone 到其对应 skills 目录即可
```

首次使用时 agent 会自动运行 `bash scripts/setup.sh`(创建 venv、安装
edge-tts/requests/pillow、下载 Noto CJK 字体)。

可选环境变量:`PEXELS_API_KEY`、`PIXABAY_API_KEY`(免费申请),有 key 时自动优先使用实拍视频片段。

## 使用 / Use

对你的 agent 说:

> 帮我做一个关于「深海最诡异的生物」的抖音短视频
>
> Make me a TikTok video about 3 mind-blowing space facts

Agent 会按 [SKILL.md](SKILL.md) 的流程:写分镜 → 跑管线 → **用视觉审查素材和成片**(这一步
是达到营销号质量的关键)→ 交付 `final.mp4` + 署名文本。

也可以完全手动使用(不依赖任何 agent):

```bash
bash scripts/setup.sh
cp examples/deep-sea-zh.json projects/my-video/storyboard.json   # 编辑它
.venv/bin/python scripts/pipeline.py projects/my-video
open projects/my-video/final.mp4
```

## 架构 / How it works

```
storyboard.json (agent 创作:文案/分镜/关键词/风格)
   │
   ├─ scripts/tts.py      edge-tts 配音 + 逐字时间戳
   ├─ scripts/assets.py   多源素材搜索/评分/下载/校验 + 预览表(供 agent 目检)
   ├─ scripts/bgm.py      按情绪取 CC-BY 配乐(Wikimedia Commons 镜像,本地缓存)
   ├─ scripts/compose.py  Pillow 渲染字幕 PNG → ffmpeg 核心滤镜合成
   │                      (Ken Burns/裁切/叠加/侧链闪避/loudnorm,无需 libass)
   └─ scripts/check.py    时长/响度/逐帧预览表 + 素材署名块(供 agent 终审)
```

设计原则:**agent 干创意的活,脚本干机械的活**。脚本全部确定性、可单独重跑、
可对单场景重抓素材(`assets.py --scene 3 --keywords "..."`),agent 通过看
`assets_sheet.jpg` / `contact_sheet.jpg` 闭环把控质量。

## 分镜格式 / Storyboard schema

见 [SKILL.md](SKILL.md) 的完整字段表,[examples/](examples/) 有三个实测通过的例子
(中文悬念科普 / English listicle / 中文种草清单)。

## FAQ

- **不装任何 key 能用吗?** 能。免 key 模式用图片素材 + Ken Burns 动效(经典营销号形态);
  Pexels/Pixabay key 免费申请后自动启用实拍视频片段。
- **支持哪些语言?** 中文和英文经过完整测试;edge-tts 支持的其他语言理论可用(欢迎 PR)。
- **商用合规?** 素材全部来自 CC/公有领域源,`check.py` 会输出需随视频发布的署名文本;
  Kevin MacLeod 音乐为 CC-BY(需署名)。请遵守各平台与素材许可条款。
- **Linux 可用吗?** 可以(需系统 ffmpeg;emoji 字幕需安装 NotoColorEmoji,否则自动跳过 emoji)。

## License

代码 MIT([LICENSE](LICENSE))。生成视频中的第三方素材遵循其原始许可(署名信息见
`review/report.txt`)。本项目仅供合法内容创作,请勿用于虚假信息或侵权内容。
