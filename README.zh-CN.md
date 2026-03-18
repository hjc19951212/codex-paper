# Codex Paper

[English README](./README.md)

`codex-paper` 是一个面向 Codex 的论文学习 skill，改造自 [`alaliqing/claude-paper`](https://github.com/alaliqing/claude-paper)。

它可以帮助 Codex：

- 接受本地 PDF、直接 PDF 链接或 arXiv 链接
- 在 `~/codex-papers/` 下准备可复用的论文工作区
- 解析元数据并提取图像
- 生成 `summary.md`、`insights.md`、`qa.md`、代码 demo 和交互式 `index.html`
- 启动一个本地 web UI 来浏览论文库

## 包含内容

- `codex-paper/` — 可安装的 Codex skill 目录
- `codex-paper/SKILL.md` — 论文学习与深挖工作流
- `codex-paper/scripts/prepare_paper.py` — 论文工作区初始化脚本
- `codex-paper/scripts/start_webui.sh` — 本地 Nuxt web UI 启动脚本
- `codex-paper/assets/webui/` — 内置论文库浏览器

## 安装

```bash
mkdir -p ~/.codex/skills
rsync -a ./codex-paper/ ~/.codex/skills/codex-paper/
```

安装后通过 `$codex-paper` 使用。

## 首次运行

```bash
cd ~/.codex/skills/codex-paper
bash scripts/ensure_deps.sh
```

## 准备论文

```bash
python3 scripts/prepare_paper.py ~/Downloads/paper.pdf
python3 scripts/prepare_paper.py https://arxiv.org/abs/1706.03762
```

## 启动 Web UI

```bash
bash scripts/start_webui.sh
```

默认地址：

- `http://localhost:5815`

默认论文库目录：

- `~/codex-papers`

## 来源说明

这个项目把原来的 Claude 插件改造成了 Codex skill，去掉了 plugin-only 的包装层，保留了可复用的论文工作流、PDF 辅助脚本和本地浏览器界面。
