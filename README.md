# GitHub Project Manager

<p align="center">
  <strong>一个面向个人开发者的 GitHub 项目本地管理工具</strong><br/>
  从本地仓库管理到线上 Release 发布，一站式完成。
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" />
  <img alt="PyQt5" src="https://img.shields.io/badge/GUI-PyQt5-41CD52?logo=qt&logoColor=white" />
  <img alt="GitHub API" src="https://img.shields.io/badge/API-GitHub-181717?logo=github" />
  <img alt="Platform" src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4c8bf5" />
</p>

---

## 项目亮点

- 本地与线上仓库统一管理：同一界面查看本地项目和你账号下的 GitHub 项目。
- 可视化项目浏览：支持双击展开目录、搜索文件、预览内容、双击系统编辑器打开。
- Release 工作流内置：创建 Release、填写说明、上传多个附件一步完成。
- Windows 11 风格 UI：浅色/深色主题可切换，视觉一致、上手轻松。
- 凭据更安全：Token 使用系统 Keyring 存储，不写入仓库文件。

## 为什么值得 Fork

如果你想基于它快速做成自己的 GitHub 桌面客户端，这个项目已经具备了可扩展骨架：

- 清晰分层：`gui / github_manager / git_manager / config_manager`
- 功能可拆：项目列表、文件浏览、Release 发布、主题系统相互独立
- 扩展成本低：新增功能时只需在对应模块补逻辑，不需要大规模重构

适合二次开发方向：

- Issues / Pull Requests 管理
- Actions 日志查看
- 多账号切换
- 组织仓库与协作权限视图
- 一键打包（Windows/macOS/Linux）

## 功能总览

### 1) 项目管理
- 创建本地 Git 项目
- 本地项目上传到 GitHub
- 本地项目删除与目录打开

### 2) 在线仓库加载
- 登录后自动读取“你拥有且非 fork”的仓库
- 与本地项目合并展示（Local / GitHub / Local + GitHub）

### 3) 项目内容查看
- 双击项目直接展开目录树
- 文件名搜索
- 文件预览（文本）
- 双击文件使用系统默认编辑器打开

### 4) Release 发布
- 创建 Release（Tag、名称、说明）
- 上传多个 Release 资产文件
- 成功/失败上传状态反馈

### 5) 界面体验
- Windows 11 风格浅色主题
- Windows 11 风格深色主题
- 统一控件风格与图标

---

## 快速开始

### 环境要求
- Python 3.10+
- Git

### 安装与运行

```bash
pip install -r requirements.txt
python main.py
```

### 首次使用
1. 点击 `Login`，输入 GitHub Personal Access Token。
2. 在 `Projects` 页查看本地项目和线上项目。
3. 双击项目浏览目录；需要发布时点击 `Publish Release`。

---

## 目录结构

```text
.
├─ main.py
├─ config_manager.py
├─ git_manager.py
├─ github_manager.py
├─ requirements.txt
└─ gui/
   ├─ main_window.py
   ├─ dialogs.py
   └─ __init__.py
```

## 安全说明

- GitHub Token 存储在系统 Keyring（凭据管理器）中。
- 应用配置位于用户目录 `~/.github_project_manager`。
- 发布仓库中不包含用户 Token 与本地历史配置。

## Roadmap

- [ ] 仓库克隆与拉取状态可视化
- [ ] Commit 历史查看与对比
- [ ] Release 模板与自动生成更新日志
- [ ] 多语言切换（中/英）
- [ ] 自动更新检查

## 贡献指南

欢迎提交 Issue / PR，推荐从以下方向开始：

1. UI 细节优化（交互反馈、空状态、快捷键）
2. GitHub API 能力扩展（Issues/PR/Actions）
3. 稳定性增强（异常处理、网络重试、日志）
4. 打包发布流程（PyInstaller / CI）

如果你 fork 了项目并做了功能增强，欢迎发 PR 回来，一起把它打磨成更实用的桌面工具。

---

## License

MIT（详见仓库根目录 [LICENSE](./LICENSE)）
