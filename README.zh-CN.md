# Common Paper for Codex

[English README](./README.md)

这是一个面向 Codex 的 Common Paper skill，用来查询合同、跟踪续约、查找签署人，并通过 Common Paper REST API 安全执行合同相关操作。

它基于开源项目 [CommonPaper/claude-skill](https://github.com/CommonPaper/claude-skill) 改造而来，但已经针对 Codex 的 skill 格式、安装方式和凭据处理流程做了重写。

## 功能

- 在 Codex 中用自然语言查询 Common Paper 合同
- 统计、搜索和汇总 NDA、CSA、续约、签署人、合同金额等信息
- 对写操作加入明确确认步骤
- 在本地为 Codex 保存并校验 API Token
- 使用内置 Python 工具脚本代替零散的 shell 命令

## 目录结构

- `commonpaper/` — 可安装的 Codex skill 目录
- `commonpaper/SKILL.md` — Codex 工作流、安全规则和使用说明
- `commonpaper/scripts/commonpaper_api.py` — Token 保存、校验和 API 请求工具
- `commonpaper/references/api-cheatsheet.md` — 接口、过滤条件和常见查询速查

## 安装

```bash
mkdir -p ~/.codex/skills
rsync -a ./commonpaper/ ~/.codex/skills/commonpaper/
```

安装后，在 Codex 中通过 `$commonpaper` 调用。

## 配置凭据

进入已安装的 skill 目录后运行：

```bash
python3 scripts/commonpaper_api.py save-token
python3 scripts/commonpaper_api.py validate-token
```

Token 会保存在 `~/.codex/skills/commonpaper/cp-api-token`，权限仅限当前用户读取。

## 示例命令

统计已签署合同数量：

```bash
python3 scripts/commonpaper_api.py request GET /agreements \
  --query 'filter[status_eq]=signed' \
  --query 'page[size]=1'
```

查询与某家公司相关的合同：

```bash
python3 scripts/commonpaper_api.py request GET /agreements \
  --query 'filter[recipient_organization_cont]=Acme' \
  --query 'page[size]=25'
```

## 安全提示

- 不要在聊天输出中暴露 API Token
- 优先使用 `save-token`，不要手动在命令里写 Bearer Token
- 所有写操作都先确认再执行
- `POST` 和 `PATCH` 尽量通过 JSON 文件传参

## 许可证

MIT
