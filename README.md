# 🔐 HStego 图片隐写工具

这是一个基于官方 HStego v0.6.1 的 Streamlit 图片隐写网页应用，用于学习图片隐写与文字提取。

## 在线体验

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://hstego-web.streamlit.app/)

**网站地址：** https://hstego-web.streamlit.app/

## 功能

- 上传原始图片（PNG、BMP、JPG）
- 输入需要隐藏的文字并设置密码
- 生成并下载隐写图片
- 上传隐写图片并使用密码提取隐藏文字

## 技术

- Python
- Streamlit
- 官方 HStego v0.6.1 Linux 可执行程序

## 本地运行

安装依赖：

```bash
pip install -r requirements.txt
```

启动应用：

```bash
streamlit run streamlit_app.py
```

## 测试说明

已在 Streamlit Cloud 部署版本中进行隐藏文字和提取文字的端到端测试。

## 官方项目

https://github.com/daniellerch/hstego
