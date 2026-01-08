# PDF Catalogue Generator (PDF 智能目录生成器)

基于多模态大模型的 PDF 目录自动生成工具。只需简单的几步操作，即可将 PDF 书籍的目录页转换为可跳转的 PDF 书签。

## 📖 项目简介

很多扫描版 PDF 电子书缺乏目录（书签），导致阅读体验不佳。传统的 OCR 方案往往难以处理复杂的目录排版（如层级缩进、点线引导符等）。

本项目利用 **多模态大模型** 的强大视觉能力，直接“看”懂目录页的视觉结构，将其提取为精确的层级数据，并自动写入 PDF 文件中。

## ✨ 核心功能

*   **AI 智能识别**: 能够处理复杂的目录排版，精准识别章节标题、页码及层级关系。
*   **可视化交互**: 使用 Streamlit 构建的 Web 界面，操作简单直观。
*   **人工校对**: 提供表格化的编辑界面，允许用户在生成前对识别结果进行微调。
*   **页码偏移修正**: 内置页码偏移计算功能，完美解决 PDF 物理页码与书籍印刷页码不一致的问题。
*   **批量写入**: 基于 PyMuPDF 高效写入书签，不破坏原文件画质。

## 🛠️ 技术栈

*   **UI 框架**: [Streamlit](https://streamlit.io/)
*   **PDF 处理**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
*   **图像处理**: Pillow
*   **数据处理**: Pandas

## 🚀 快速开始

### 1. 环境要求

*   Python 3.8 或更高版本
*   一个有效的 OpenAI API Key

### 2. 安装依赖

建议创建一个虚拟环境来运行本项目：

```bash
# 创建并激活虚拟环境 (可选)
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 运行应用

```bash
streamlit run main.py
```

启动成功后，浏览器会自动打开 `http://localhost:8501`。

## 📖 使用指南

1.  **配置 API**: 在左侧边栏输入你的 OpenAI API Key 、 Base URL（如果使用中转服务）和 Model Name。

![image-20260107114916153](E:\A_doc\Code\PDFCatalogueGenerator\README.assets\image-20260107114916153.png)

1.  **上传文件**: 点击上传你需要处理的 PDF 文件。这里以一本目录错乱的《吉米多维奇数学高等数学》为例。

![image-20260107115026731](E:\A_doc\Code\PDFCatalogueGenerator\README.assets\image-20260107115026731.png)

1.  **指定目录页**: 输入目录所在的 PDF 页码范围（支持 `7-10` 或 `7,8,9,10` 格式）。
2.  **设置偏移量**:
    *   找到正文第 1 页在 PDF 播放器中的实际页码（例如第 11 页）。
    *   计算偏移量：`11 - 1 = 10`。
    *   在界面 "Page Offset" 输入框中填入 `10`。

![image-20260107115223325](E:\A_doc\Code\PDFCatalogueGenerator\README.assets\image-20260107115223325.png)

3. **提取与编辑**: 点击 **"Extract TOC from PDF"**。等待 AI 识别完成后，你可以在右侧表格中查看结果。如有错误，可直接修改标题、页码或调整层级（Level）。

![image-20260108122558066](E:\A_doc\Code\PDFCatalogueGenerator\README.assets\image-20260108122558066.png)

4. **生成下载**: 点击 **"Write TOC to PDF"**，处理完成后即可点击**“Download PDF with TOC”**下载带有书签的新 PDF 文件。

打开处理后的PDF文件，可以看到书签栏出现了正确的目录。

![image-20260108122756055](E:\A_doc\Code\PDFCatalogueGenerator\README.assets\image-20260108122756055.png)

## 📂 项目结构

```
PDFCatalogueGenerator/
├── main.py              # Streamlit 主程序，UI 与业务逻辑入口
├── ocr_service.py       # AI 服务模块，负责与 OpenAI API 交互
├── pdf_utils.py         # PDF 处理模块，负责提取图片与写入书签
├── requirements.txt     # 项目依赖列表
└── README.md            # 项目说明文档
```

## ⚠️ 注意事项

*   **API 成本**: 图像识别需要消耗 Token，处理超长目录（数十页）时请留意你的 API 配额。
*   **隐私安全**: 请确保你使用的 API 渠道安全可靠。本项目上传的 PDF 仅在本地临时处理，但被选中的目录页截图会被发送给 服务商的服务器进行识别。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！如果你有更好的 Prompt 策略或功能建议，请随时分享。

## 📄 许可证

[MIT License](LICENSE)
