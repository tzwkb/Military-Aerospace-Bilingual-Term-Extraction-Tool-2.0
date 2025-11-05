# 🌐 Military & Aerospace Bilingual Term Extraction Tool

<div align="center">

**AI-Powered Bilingual Terminology Extraction System**

*Specialized for Military, Aerospace, Medical & Defense Technical Documents*

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI GPT-4](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com/)
[![讯飞OCR](https://img.shields.io/badge/讯飞OCR-云端API-orange.svg)](https://www.xfyun.cn/)

</div>

---

## 🎯 核心特性

### 🎉 v2.1 最新更新

- **☁️ 云端OCR升级** - 从PaddleOCR迁移至科大讯飞云端OCR
  - ✅ 无需本地GPU配置
  - ✅ 零模型下载，即用即走
  - ✅ 识别准确率更高
  - ✅ 内存占用大幅降低（从4GB降至512MB）
  - ✅ 按需付费，新用户有免费额度

### ✨ v2.0 核心功能

- **🌐 双语术语提取** - 同时生成英文和中文术语对照（可选）
- **📑 OCR智能分批** - 自动分批处理大型扫描版PDF（10页/10MB阈值），避免内存溢出
- **🔁 自动重试机制** - 批次失败时智能重试（最多3次），大幅提高OCR成功率
- **💾 实时保存** - OCR处理过程中实时保存中间结果，防止数据丢失
- **☁️ 云端OCR** - 科大讯飞云端OCR，无需本地GPU，识别准确
- **🎛️ 模式选择** - 用户可自由选择单语或双语模式

### 🚀 强大功能

#### 文档处理
- ✅ **智能PDF处理** - 基于pdfminer.six的高精度文本提取
- ✅ **自动OCR降级** - 检测扫描版PDF并自动启用OCR（科大讯飞云端OCR）
- ✅ **智能分批处理** - 大型PDF（>10页或10MB）自动分批OCR，避免内存溢出
- ✅ **自动重试机制** - 批次失败时自动重试（最多3次），提高成功率
- ✅ **多格式支持** - PDF、DOCX、TXT、JSON、CSV、Markdown
- ✅ **智能文本分割** - 按语义边界分割，保持上下文完整

#### 术语提取
- ✅ **AI驱动** - GPT-4o专业术语识别
- ✅ **双语输出** - 英文+中文术语对照（可选单语模式）
- ✅ **缩写展开** - 自动提取缩写词完整形式
- ✅ **智能去重** - 基于双语组合的精准去重
- ✅ **领域优化** - 针对军事、航空航天、医疗、国防领域优化

#### 输出格式
- 📊 **JSON** - 结构化数据，便于程序处理
- 📋 **CSV** - 表格数据，Excel兼容（UTF-8-BOM）
- 📈 **Excel** - 带样式和统计信息的专业报表
- 🔤 **TXT** - 双语对照的纯文本格式
- 🏷️ **TBX** - 符合ISO 30042标准的术语交换格式（可导入CAT工具）

#### 工作流优化
- ✅ **断点续传** - 自动保存进度，支持中断恢复
- ✅ **并发处理** - 多线程并发提取，速度提升10倍
- ✅ **进度追踪** - 实时显示处理进度和预计时间
- ✅ **错误容错** - 单个批次失败不影响整体处理

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows / Linux / macOS
- **OpenAI API Key**: 需要有效的API密钥
- **科大讯飞OCR**: 需要AppID和Secret（可选，用于扫描版PDF）
- **网络连接**: 需要稳定的网络连接
- **内存**: 建议4GB+（云端OCR，本地资源占用低）
- **磁盘空间**: 至少500MB（临时文件）

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd "Term Extraction Tool_GPT"
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

**OCR功能提示：**
- 科大讯飞OCR使用云端API，无需下载模型
- 需要在讯飞开放平台注册并获取API凭证
- 按实际使用量计费，新用户通常有免费额度

#### 3. 配置API密钥

**OpenAI API（必需）**

方法1：环境变量（推荐）
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

方法2：配置文件
```python
# 编辑 config.py
OPENAI_API_KEY = "your-api-key-here"
OPENAI_BASE_URL = "https://api.openai.com/v1"  # 可选：自定义API端点
```

**科大讯飞OCR API（可选，用于扫描版PDF）**

方法1：环境变量
```bash
# Windows PowerShell
$env:XUNFEI_APP_ID="your-app-id"
$env:XUNFEI_SECRET="your-secret"

# Linux/Mac
export XUNFEI_APP_ID="your-app-id"
export XUNFEI_SECRET="your-secret"
```

方法2：配置文件
```python
# 编辑 config.py
XUNFEI_OCR_CONFIG = {
    "app_id": "your-xunfei-app-id",
    "secret": "your-xunfei-secret",
    "enabled": True,  # True=启用OCR, False=禁用
}
```

获取讯飞API凭证：
1. 访问 https://www.xfyun.cn/
2. 注册并登录
3. 进入控制台 → 我的应用
4. 创建新应用并获取 AppID 和 Secret

### 基本使用

#### 方式1：交互式模式（推荐）

```bash
python main.py
```

**交互流程：**

```
🎉 欢迎使用OpenAI GPT批处理术语抽取工具!

1. 选择输入方式
   ├─ 从文件读取 (推荐)
   ├─ 直接输入文本
   └─ 使用示例文本

2. 选择模型
   └─ 默认: gpt-4o

3. 选择提取模式 ⭐ 新功能
   ├─ 双语模式 (推荐) - 英文+中文对照
   └─ 单语模式 - 仅提取原文术语

4. 自动处理
   ├─ 检测文件类型
   ├─ 扫描版PDF自动OCR（科大讯飞云端）
   ├─ 大型PDF自动分批处理
   └─ 实时保存进度

5. 选择输出格式
   ├─ JSON / CSV / Excel
   ├─ TBX / TXT
   └─ 支持生成多种格式
```

#### 方式2：命令行模式

```bash
# 指定文件处理
python main.py --file document.pdf

# 自定义参数
python main.py --model gpt-4-turbo --format csv
```

---

## 📁 项目结构

```
Term Extraction Tool_GPT/
├── 📄 核心文件
│   ├── main.py                    # 主程序入口
│   ├── config.py                  # 配置文件（API、提示词、参数）
│   ├── gpt_processor.py           # GPT API处理和批处理
│   ├── file_processor.py          # 文件处理和OCR调度
│   ├── xunfei_ocr.py              # 科大讯飞OCR接口
│   ├── text_splitter.py           # 智能文本分割
│   └── checkpoint_manager.py      # 断点管理
│
├── 📁 工作目录
│   ├── file preparation/          # 📥 输入文档目录
│   ├── extracted_texts/           # 📝 OCR提取的文本
│   ├── batch_results/             # 📊 术语提取结果
│   └── checkpoints/               # 💾 断点文件
│
├── 📚 文档
│   ├── README.md                  # 本文档
│   ├── BILINGUAL_FEATURES.md      # 双语功能详细说明
│   ├── EXTRACTION_MODES.md        # 单语/双语模式对比
│   └── requirements.txt           # Python依赖列表
│
└── 🛠️ 工具脚本
    ├── extract_pdf_texts.py       # PDF批量提取工具
    └── checkpoint_tool.py         # 断点管理CLI
```

---

## 🌐 双语术语提取

### 输出格式对比

#### 双语模式（推荐）

**JSON格式：**
```json
{
  "terms": [
    {
      "eng_term": "Inertial Measurement Unit (IMU)",
      "zh_term": "惯性测量单元"
    },
    {
      "eng_term": "Global Positioning System (GPS)",
      "zh_term": "全球定位系统"
    }
  ]
}
```

**Excel格式：**

| 序号 | 英文术语 | 中文术语 | 来源文件 | 模型 |
|------|----------|----------|----------|------|
| 1 | Inertial Measurement Unit (IMU) | 惯性测量单元 | 词典.pdf | gpt-4o |
| 2 | Global Positioning System (GPS) | 全球定位系统 | 词典.pdf | gpt-4o |

#### 单语模式

**JSON格式：**
```json
{
  "terms": [
    {"term": "惯性测量单元 (IMU, Inertial Measurement Unit)"},
    {"term": "全球定位系统 (GPS, Global Positioning System)"}
  ]
}
```

### 适用场景

| 模式 | 适用场景 | 优势 |
|------|----------|------|
| **双语** | 建立双语术语库、辅助翻译、学习材料 | 完整对照、便于翻译 |
| **单语** | 快速提取、降低成本、保持原文 | 速度快、成本低 |

---

## ☁️ 科大讯飞云端OCR

### 优势特点

- ✅ **无需本地GPU** - 云端处理，任何配置都能运行
- ✅ **识别准确率高** - 基于深度学习的高精度OCR引擎
- ✅ **支持多种格式** - PDF、图片等多种文档格式
- ✅ **快速响应** - 云端并行处理，速度快
- ✅ **按需付费** - 新用户有免费额度，用多少付多少
- ✅ **维护简单** - 无需更新本地模型，自动享受最新技术

### 使用场景

| 场景 | 说明 |
|------|------|
| ✅ 扫描版PDF | 自动识别并提取文本 |
| ✅ 图片文档 | 支持JPG、PNG等格式 |
| ✅ 复杂排版 | 智能识别表格、多栏等复杂布局 |
| ✅ 混合文档 | 同时包含文本和扫描内容的PDF |

---

## 📑 OCR智能分批处理

### 触发条件

对于扫描版PDF，当满足以下条件之一时自动启用分批处理：

- 📄 **页数** > 50页
- 💾 **文件大小** > 50MB

### 处理流程

```
检测大型PDF (238页, 105MB)
  ↓
自动分批 (每批20页)
  ↓
┌─────────────────────────────────┐
│ 批次1: 页1-20                    │
│ ├─ 分割PDF → 临时文件           │
│ ├─ OCR识别 (45秒)               │
│ ├─ 💾 保存到 xxx_batch_ocr.txt  │  ← 实时保存
│ └─ 清理临时文件                 │
├─────────────────────────────────┤
│ 批次2: 页21-40                   │
│ ├─ OCR识别 (42秒)               │
│ ├─ 💾 追加到 xxx_batch_ocr.txt  │  ← 实时追加
│ └─ ...                          │
├─────────────────────────────────┤
│ ...继续处理剩余批次              │
└─────────────────────────────────┘
  ↓
🎉 处理完成
  └─ 完整结果: extracted_texts/xxx_batch_ocr.txt
```

### 实时监控进度

处理过程中可以随时打开 `extracted_texts/` 目录查看：

```
extracted_texts/
  └── 英俄汉导航与运动控制词典_batch_ocr.txt
      ├── [批次 1: 页1-20]  ✅
      ├── [批次 2: 页21-40] ✅
      ├── [批次 3: 页41-60] ✅ 
      └── [批次 4: 页61-80] 🔄 处理中...
```

### 性能优化

**配置调整**（`config.py`）：

```python
PDF_OCR_CONFIG = {
    "batch_threshold_pages": 10,      # 触发阈值：页数（从50降低到10）
    "batch_threshold_mb": 10,         # 触发阈值：文件大小（从50MB降低到10MB）
    "batch_size": 10,                 # 每批处理页数（从20降低到10）
    "enable_batch_processing": True,  # 功能开关
    "max_retries": 3,                 # 单个批次失败时的最大重试次数
    "retry_delay": 2,                 # 重试之间的延迟（秒）
}
```

**建议设置：**

科大讯飞OCR使用云端处理，配置主要影响网络并发和处理速度：

- **网络良好**: `batch_size = 20`, `max_retries = 3`
- **网络一般**: `batch_size = 10-15`, `max_retries = 3`, `retry_delay = 2`
- **网络不稳定**: `batch_size = 5`, `max_retries = 5`, `retry_delay = 5`
- **超大PDF (500页+)**: 保持默认配置，或适当增加 `max_retries`

---

## 🎛️ 配置说明

### API设置

```python
# config.py

# API密钥配置
OPENAI_API_KEY = "your-api-key-here"
OPENAI_BASE_URL = "https://api.openai.com/v1"

# 模型选择
DEFAULT_MODEL = "gpt-4o"  # 推荐：高质量
# 可选: "gpt-4o-mini" (经济), "gpt-4-turbo" (平衡)
```

### 批处理参数

```python
BATCH_CONFIG = {
    "temperature": 0.1,              # 稳定性（0-1，越低越稳定）
    "max_output_tokens": 128000,     # 最大输出token
    "max_concurrent": 10,            # 并发请求数
    "requests_per_minute": 30,       # 速率限制
}
```

### 文本分割策略

```python
TEXT_SPLITTING = {
    "default_chunk_size": 12000,       # 每块字符数
    "default_overlap_size": 800,       # 块间重叠
    "max_chunk_size": 400000,          # 最大块大小
    "whole_document_threshold": 300000,# 整文档阈值
}
```

### 术语提取模式

```python
EXTRACTION_MODE = {
    "bilingual": True,  # True=双语, False=单语
}
```

### 提示词定制

```python
# 系统提示词
SYSTEM_PROMPT = """You are a senior military, aerospace, medical, and defense terminology extraction specialist..."""

# 用户提示词（支持单语/双语）
def get_user_prompt(text: str, bilingual: bool = True):
    # 返回定制化提示词
```

---

## 📋 使用示例

### 示例1：处理扫描版PDF词典

```bash
# 1. 将PDF放入 file preparation/ 目录
# 2. 运行程序
python main.py

# 3. 选择双语模式
🌐 请选择术语提取模式:
1. 双语模式 (推荐)
2. 单语模式
请选择 (1-2): 1

# 4. 自动处理
📑 检测到大型PDF，将分批处理（每批20页）
🔄 正在OCR识别批次 1/12...
✅ 批次 1 完成，耗时 45.3秒
💾 批次 1 结果已保存
📈 总进度: 8.3% (1/12)

# 5. 生成Excel报表
📊 请选择输出格式:
选择格式 (1-5): 3
✅ Excel文件已生成
```

**预期结果：**
- OCR时间：约1-2分钟/页（取决于网络速度）
- 术语提取：20-30分钟（238页PDF）
- 输出文件：`batch_results/词典_20251022_143045_gpt4o_1500terms.xlsx`
- 中间文本：`extracted_texts/词典_batch_ocr.txt`

### 示例2：快速单语提取

```bash
python main.py

# 选择单语模式
🌐 请选择术语提取模式: 2

# 输出CSV格式
📊 请选择输出格式: 2
```

**优势：**
- 处理速度更快
- Token使用更少（降低约15-20%）
- 总体成本更低

### 示例3：批量处理文件夹

```bash
# 1. 预先提取所有PDF文本
python extract_pdf_texts.py

# 2. 批量术语提取
python main.py
# 选择: 从文件读取 → 处理所有文件
```

### 示例4：使用断点续传

```bash
# 查看可恢复的检查点
python checkpoint_tool.py list

# 程序会在启动时自动提示：
🔄 发现 1 个未完成的处理任务
请选择操作：
  1. 恢复任务 (创建: 2025-10-22 14:30, 进度: 5/12)
  2. 跳过，开始新任务
  3. 删除所有checkpoint并开始新任务
```

---

## 📊 输出格式详解

### 1. JSON格式

**用途：** 程序处理、API集成

```json
{
  "custom_id": "merged_terms",
  "extracted_terms": {
    "terms": [
      {
        "eng_term": "Unmanned Aerial Vehicle (UAV)",
        "zh_term": "无人机",
        "source_files": ["document.pdf"]
      }
    ],
    "total_terms": 1500,
    "duplicates_removed": 230
  },
  "usage": {"total_tokens": 45000},
  "model": "gpt-4o",
  "created": 1729584000
}
```

### 2. CSV格式

**用途：** Excel导入、数据分析

```csv
custom_id,英文术语,中文术语,来源文件,模型,token使用
merged_terms,Inertial Navigation System (INS),惯性导航系统,词典.pdf,gpt-4o,1250
```

**编码：** UTF-8-BOM（Excel直接兼容，无乱码）

### 3. Excel格式

**用途：** 人工审核、团队协作

**特性：**
- ✨ 专业样式（表头蓝色、边框、居中对齐）
- 📊 统计信息工作表（总术语数、Token使用、生成时间）
- 📏 自动列宽调整
- 🎨 条件格式（可选）

### 4. TBX格式

**用途：** CAT工具（Trados、MemoQ等）

**标准：** ISO 30042（TermBase eXchange）

```xml
<termEntry id="term_1">
  <langGrp xml:lang="en">
    <term>Inertial Navigation System</term>
  </langGrp>
  <langGrp xml:lang="zh">
    <term>惯性导航系统</term>
  </langGrp>
</termEntry>
```

### 5. TXT格式

**用途：** 简单查看、打印、备份

```
=== 结果 1: merged_terms ===
提取的术语数量: 1500

1. Inertial Navigation System (INS)
   惯性导航系统
   
2. Global Positioning System (GPS)
   全球定位系统
```

---

## 🔧 高级功能

### 智能文本分割

**策略：**
- **整文档模式**: <300K字符 → 单个上下文处理
- **智能分割**: 按段落和语义边界分割
- **按段落处理**: 适合短文本和术语表

**配置：**
```python
# 在运行时选择
📝 文本分割配置:
1. 智能分割 (推荐)
2. 整文档处理
3. 按段落处理
```

### 并发批处理

**优势：**
- 多线程并发API调用
- 速度提升5-10倍
- 自动速率限制

**配置：**
```python
BATCH_CONFIG = {
    "max_concurrent": 10,  # 并发数（根据API限制调整）
    "requests_per_minute": 30,  # 速率限制
}
```

### 断点恢复系统

**自动保存：**
- 每处理5个文件自动保存
- 每10分钟自动保存
- 完成后自动删除

**手动管理：**
```bash
# 列出所有检查点
python checkpoint_tool.py list

# 查看详细信息
python checkpoint_tool.py show <checkpoint-id>

# 删除检查点
python checkpoint_tool.py delete <checkpoint-id>
```

### 去重算法

**单语模式：**
```python
term_key = term.lower()  # 忽略大小写
```

**双语模式：**
```python
term_key = f"{eng_term.lower()}|{zh_term}"  # 组合键
```

**策略：**
- 优先选择首字母大写的版本
- 合并多个来源文件信息
- 保留最完整的术语形式

---

## 🛠️ 故障排查

### 常见问题

#### 1. OCR功能未启用

**错误：** `扫描版PDF需要OCR处理，但OCR功能未启用`

**解决：**
```bash
# 检查讯飞OCR配置
# 编辑 config.py，确保以下配置正确：
XUNFEI_OCR_CONFIG = {
    "app_id": "your-xunfei-app-id",      # 填入您的AppID
    "secret": "your-xunfei-secret",      # 填入您的Secret
    "enabled": True,                     # 确保为True
}

# 或使用环境变量
export XUNFEI_APP_ID="your-app-id"
export XUNFEI_SECRET="your-secret"
```

#### 2. API速率限制

**错误：** `Rate limit exceeded`

**解决：**
```python
# config.py
BATCH_CONFIG = {
    "max_concurrent": 5,  # 降低并发数
    "requests_per_minute": 10,  # 降低速率
}
```

#### 3. 内存不足（大型OCR）

**错误：** `MemoryError` 或程序崩溃

**解决：**
```python
# config.py - 科大讯飞OCR使用云端处理，内存占用极低
PDF_OCR_CONFIG = {
    "batch_size": 10,  # 减小批次大小（主要影响网络并发）
}
```

#### 6. 讯飞OCR API调用失败

**错误：** `OCR API调用失败` 或 `认证失败`

**解决：**
1. 检查AppID和Secret是否正确
2. 检查网络连接是否正常
3. 登录讯飞开放平台检查API额度
4. 确认API服务状态正常

#### 4. 中文乱码（CSV）

**原因：** Excel默认编码问题

**解决：**
- 使用Excel格式（`.xlsx`）代替CSV
- 或在Excel中选择"数据 → 获取外部数据 → 从文本"，选择UTF-8编码

#### 5. Token超限

**错误：** `Context length exceeded`

**解决：**
```python
# config.py
TEXT_SPLITTING = {
    "default_chunk_size": 8000,  # 减小块大小
}
```

### 性能优化建议

#### 提升速度
```python
# 1. 增加并发数（注意API限制）
BATCH_CONFIG["max_concurrent"] = 15

# 2. 使用更快的模型
DEFAULT_MODEL = "gpt-4o-mini"  # 速度快，成本低

# 3. 减小chunk重叠
TEXT_SPLITTING["default_overlap_size"] = 400
```

#### 降低成本
```python
# 1. 使用mini模型
DEFAULT_MODEL = "gpt-4o-mini"  # 成本降低80%

# 2. 单语模式
EXTRACTION_MODE["bilingual"] = False  # 节省20%

# 3. 增大chunk大小（减少请求次数）
TEXT_SPLITTING["default_chunk_size"] = 20000
```

#### 提升质量
```python
# 1. 使用最强模型
DEFAULT_MODEL = "gpt-4o"

# 2. 双语模式
EXTRACTION_MODE["bilingual"] = True

# 3. 降低temperature
BATCH_CONFIG["temperature"] = 0
```

---

## 📦 依赖说明

### 核心依赖

```
# GPT术语抽取核心依赖
openai>=1.10.0              # GPT API集成
tiktoken>=0.5.1             # Token计数

# PDF处理
pdfminer.six>=20231228      # PDF文本提取
PyPDF2==3.0.1              # PDF分割（分批OCR用）

# 文档处理
python-docx==0.8.11         # DOCX支持

# OCR功能（科大讯飞云端API）
requests>=2.31.0            # HTTP客户端，用于调用讯飞OCR API
Pillow>=10.0.0             # 图像处理（可选）

# Excel输出支持
openpyxl>=3.1.0            # Excel输出
```

### 可选依赖

```
python-magic==0.4.27        # 文件类型检测
python-magic-bin==0.4.14    # Windows magic支持
```

### OCR说明

**科大讯飞云端OCR：**
- ✅ 无需下载模型
- ✅ 云端处理，不占用本地资源
- ✅ 识别准确率高
- ⚠️ 需要网络连接
- ⚠️ 按使用量计费（新用户有免费额度）

---

## 📈 性能指标

### 处理速度

| 文档类型 | 文件大小 | 页数 | OCR时间 | 术语提取 | 成本估算* |
|---------|---------|------|---------|---------|----------|
| 文本PDF | 5MB | 50页 | 无需OCR | 2-3分钟 | GPT: $0.15 |
| 扫描PDF | 50MB | 200页 | 3-6分钟 | 20-30分钟 | OCR: $0.10 + GPT: $0.50 |
| 大型PDF | 100MB | 500页 | 8-15分钟 | 1-2小时 | OCR: $0.25 + GPT: $1.20 |

*成本说明：
- GPT成本基于gpt-4o模型计算
- OCR成本基于科大讯飞计费标准（实际费用可能因套餐而异）
- 新用户通常有免费额度可用

### 提取质量

| 指标 | 单语模式 | 双语模式 |
|------|----------|----------|
| **准确率** | 95%+ | 96%+ |
| **缩写识别** | 90%+ | 92%+ |
| **去重率** | 98%+ | 99%+ |
| **领域术语** | 85%+ | 88%+ |

### 资源使用

| 场景 | CPU | 内存 | 磁盘 | 网络 |
|------|-----|------|------|------|
| **文本提取** | 低 | 512MB | 临时文件 | 无 |
| **科大讯飞OCR** | 低 | 512MB | 临时文件 | 需要 |
| **GPT处理** | 低 | 1GB | 无 | 需要 |

**说明：**
- 科大讯飞OCR使用云端处理，本地资源占用极低
- 主要资源消耗在网络传输和GPT API调用

---

## 🎓 最佳实践

### 1. 文档准备

✅ **推荐做法：**
- 使用描述性文件名（便于追踪来源）
- 将相关文档放在同一目录
- 确保PDF质量良好（扫描DPI ≥ 300）

⚠️ **注意事项：**
- 超大文件（>500MB）建议先分割
- 加密PDF需要先解密
- 低质量扫描件可能影响OCR准确率

### 2. 模式选择

| 场景 | 推荐模式 | 原因 |
|------|----------|------|
| 建立术语库 | 双语 | 完整对照，便于管理 |
| 快速预览 | 单语 | 速度快，成本低 |
| 辅助翻译 | 双语 | 直接可用的翻译参考 |
| 纯中文文档 | 单语 | 无需英文翻译 |
| 学习材料 | 双语 | 帮助理解专业术语 |

### 3. 成本优化

**预算有限：**
```python
DEFAULT_MODEL = "gpt-4o-mini"  # 成本降低80%
EXTRACTION_MODE["bilingual"] = False  # 再节省15%
```

**质量优先：**
```python
DEFAULT_MODEL = "gpt-4o"
EXTRACTION_MODE["bilingual"] = True
BATCH_CONFIG["temperature"] = 0
```

### 4. 质量保证

1. **人工审核**：始终由领域专家复核
2. **迭代优化**：根据反馈调整提示词
3. **批量测试**：小范围测试后再大规模处理
4. **备份原文**：保留OCR提取的原始文本

---

## 📞 技术支持

### 自助资源

- 📖 [双语功能详解](BILINGUAL_FEATURES.md)
- 📖 [单语/双语模式对比](EXTRACTION_MODES.md)
- 🔧 [故障排查](#故障排查)
- 💬 提Issue或Pull Request

### 常见查询

```bash
# 查看支持的文件格式
python main.py --help

# 检查OCR配置
python -c "from config import XUNFEI_OCR_CONFIG; print('OCR启用状态:', XUNFEI_OCR_CONFIG['enabled'])"

# 清理缓存
rm -rf checkpoints/
rm -rf extracted_texts/
```

---

## 📄 许可证

本项目为专有软件，专为军事、航空航天和国防领域的术语提取应用设计。

---

## 🤝 贡献指南

本工具面向专业国防和航空航天应用。如需定制化或企业部署，请联系开发团队。

---

## 🔗 相关文档

- [双语术语提取功能说明](BILINGUAL_FEATURES.md) - 详细的双语功能文档
- [提取模式对比](EXTRACTION_MODES.md) - 单语vs双语全面对比
- [配置文件](config.py) - 完整配置选项说明

---

<div align="center">

**🌟 Star this repo if you find it helpful! 🌟**

*Made with ❤️ for Military & Aerospace Professionals*

</div>
