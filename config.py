#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI GPT批处理术语抽取配置文件
包含API配置、模型参数、处理配置和提示词设置
"""

import os
from typing import List, Dict, Any

# =============================================================================
# API 配置
# =============================================================================

# OpenAI API配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")  # 支持自定义API端点

# 模型配置
DEFAULT_MODEL = "gpt-4o"

# =============================================================================
# 模型API参数兼容性配置
# =============================================================================

MODEL_API_PARAMS = {
    # 使用max_completion_tokens的新版本模型
    "new_models": ["gpt-5", "2025", "gpt-4o-2024-08-06"],
    # 使用max_tokens的传统模型
    "legacy_models": ["gpt-4", "gpt-3.5", "gpt-4-turbo"]
}

def get_token_param_name(model: str) -> str:
    """
    根据模型名称返回正确的token参数名
    
    Args:
        model: 模型名称
        
    Returns:
        str: 'max_completion_tokens' 或 'max_tokens'
    """
    model_lower = model.lower()
    
    # 检查是否是新版本模型
    for new_model in MODEL_API_PARAMS["new_models"]:
        if new_model.lower() in model_lower:
            return "max_completion_tokens"
    
    # 默认使用传统参数
    return "max_tokens"

# =============================================================================
# 批处理参数配置
# =============================================================================

BATCH_CONFIG = {
    "temperature": 0,  # 完全确定性输出，用于建立绝对基线
    "max_output_tokens": 128000,  # 通用的最大输出token数（会根据模型自动转换为正确的参数名）
    "check_interval": 5,  # 状态检查间隔（秒）
    "max_wait_time": 3600,  # 最大等待时间（秒）
    "requests_per_minute": 30,  # 每分钟请求限制（降低）
    "max_concurrent": 10,  # 最大并发请求数（降低以提高稳定性）
}

# =============================================================================
# PDF OCR处理配置
# =============================================================================

PDF_OCR_CONFIG = {
    "batch_threshold_pages": 10,  # 超过多少页时启用分批处理（降低阈值以避免内存问题）
    "batch_threshold_mb": 10,     # 超过多少MB时启用分批处理（降低阈值）
    "batch_size": 10,              # 每批处理的页数（降低到3页以提高稳定性，避免内存溢出）
    "enable_batch_processing": True,  # 是否启用分批处理功能
    "max_retries": 3,             # 单个批次失败时的最大重试次数
    "retry_delay": 2,             # 重试之间的延迟（秒）
}

# =============================================================================
# 提示词配置
# =============================================================================

# 术语提取模式
EXTRACTION_MODE = {
    "bilingual": True,  # True=双语模式, False=单语模式（可在运行时修改）
}

# 系统提示词
SYSTEM_PROMPT = """You are a senior navigation and motion control terminology extraction specialist with extensive expertise in aerospace guidance, inertial navigation, control systems, and robotics. Your mission is to extract precise technical terminology from navigation and control systems documentation, building comprehensive bilingual/multilingual terminology databases with maximum accuracy."""

def get_user_prompt(text: str, bilingual: bool = True) -> str:
    """
    生成用户提示词模板（支持单语/双语模式）
    
    Args:
        text: 占位符，实际使用时会被替换为真实文本
        bilingual: True=双语模式, False=单语模式
        
    Returns:
        str: 格式化的用户提示词模板
    """
    if bilingual:
        # 双语模式 - 导航与运动控制专用
        return f"""Extract comprehensive bilingual terminology from navigation and motion control systems documentation to build a professional terminology database. Focus on navigation, guidance, control systems, inertial sensors, and aerospace engineering terminology.

BILINGUAL EXTRACTION STANDARDS:

CRITICAL: Each term must include BOTH English and Chinese versions:
- If the source text is in English/Russian: provide the original term + accurate Chinese translation
- If the source text is in Chinese: provide the Chinese term + English translation
- For acronyms: include full expansion (e.g., "INS, Inertial Navigation System" + "惯性导航系统")
- For Russian terms (if present): transliterate and provide English/Chinese equivalents
- For proper nouns/model names: transliterate if no standard translation exists

Standardize similar terms (merge variants into the most precise or official form)
Extract domain-specific technical terms related to navigation, control, aerospace, and robotics
Avoid overly generic terms unless they have specific technical significance in navigation/control
Prioritize standard terminology used in IEEE, AIAA, and international aerospace standards

OUTPUT FORMAT - Strict JSON structure with BILINGUAL fields:
{{{{
  "terms": [
    {{{{
      "eng_term": "English term with full expansion for acronyms (include Russian if present)",
      "zh_term": "中文术语及缩写的完整展开"
    }}}}
  ]
}}}}

QUALITY VALIDATION CHECKLIST:
✓ EVERY term has BOTH eng_term and zh_term fields (mandatory)
✓ English terms follow standard navigation/control terminology conventions
✓ Chinese translations use commonly accepted aerospace/control engineering terms
✓ Abbreviations include full expanded form in both languages
✓ No duplicate terms (merge similar entries - prefer precise/official forms)
✓ Terms are relevant to navigation, guidance, control, or motion systems

TEXT TO PROCESS:
{text}"""
    else:
        # 单语模式 - 导航与运动控制专用
        return f"""Extract comprehensive navigation and motion control terminology from the provided text to build a professional terminology database. Focus on navigation systems, guidance, control theory, and aerospace engineering terms.

PROFESSIONAL EXTRACTION STANDARDS:

For acronyms: 
Include both abbreviated and expanded forms when available (e.g., "惯性测量单元 (IMU, Inertial Measurement Unit)" or "卡尔曼滤波 (Kalman Filter)")

Standardize similar terms (merge variants into the most precise or official form)
Extract domain-specific technical terms related to navigation, control, aerospace, and robotics
Avoid overly generic terms unless they have specific technical significance in navigation/control
Prioritize standard terminology used in IEEE, AIAA, and international aerospace standards
For Chinese texts, provide Chinese terms; for English/Russian texts, provide the original term

OUTPUT FORMAT - Strict JSON structure:
{{{{
  "terms": [
    {{{{
      "term": "Exact term as extracted from text (with full expansion for acronyms)"
    }}}}
  ]
}}}}

QUALITY VALIDATION CHECKLIST:
✓ Each term is relevant to navigation, guidance, control, or motion systems
✓ No duplicate terms (merge similar entries - prefer precise/official forms)
✓ Abbreviations include full expanded form when possible
✓ Terms accurately reflect the content and domain of the source text
✓ Terms follow standard navigation/control engineering conventions

TEXT TO PROCESS:
{text}"""


# =============================================================================
# 输出格式配置
# =============================================================================

OUTPUT_FORMATS = {
    "json": {
        "extension": ".json",
        "description": "JSON格式，保留完整结构信息"
    },
    "csv": {
        "extension": ".csv", 
        "description": "CSV格式，便于Excel处理"
    },
    "excel": {
        "extension": ".xlsx",
        "description": "Excel格式，带样式和统计信息"
    },
    "tbx": {
        "extension": ".tbx",
        "description": "TBX格式，术语管理标准XML格式"
    },
    "txt": {
        "extension": ".txt",
        "description": "纯文本格式，便于阅读"
    }
}

# =============================================================================
# 文件处理配置
# =============================================================================

# 支持的输入文件格式
SUPPORTED_INPUT_FORMATS = [".txt", ".json", ".csv", ".md"]

# 智能文本分割配置
TEXT_SPLITTING = {
    "default_chunk_size": 12000,  # 默认块大小（字符）- 约3K tokens，为输出预留空间
    "default_overlap_size": 800,  # 默认重叠大小（字符）
    "min_chunk_size": 1000,  # 最小块大小（字符）
    "max_chunk_size": 400000,  # 最大块大小（字符）- 约100K tokens，预留28K给输出和提示词
    "min_overlap_size": 100,  # 最小重叠大小（字符）
    "max_overlap_ratio": 0.1,  # 最大重叠比例
    "enable_whole_document_mode": True,  # 启用整文档模式选项
    "whole_document_threshold": 300000,  # 小于此字符数时可选择整文档处理（约75K tokens）
}

# =============================================================================
# 术语处理配置
# =============================================================================

TERM_PROCESSING = {
    "enable_deduplication": True,  # 启用术语去重
    "case_sensitive_matching": False,  # 术语匹配是否区分大小写
    "max_merged_contexts": 3,  # 最多合并的上下文数量
    "max_merged_definitions": 3,  # 最多合并的定义数量
    "min_context_length": 20,  # 最小上下文长度（过滤太短的上下文）
    "min_definition_length": 10,  # 最小定义长度
    
    # 术语质量控制
    "quality_controls": {
        "min_term_length": 2,  # 最小术语长度
        "max_term_length": 100,  # 最大术语长度
        "exclude_generic_words": [  # 排除的通用词汇
            "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"
        ],
        "required_categories": [  # 必须的分类列表（严格单一分类）
            "Aircraft & Platforms", "Weapons & Munitions", "Avionics & Electronics",
            "Flight Systems & Controls", "Weapons Integration", "Guidance & Navigation",
            "Safety & Security", "Testing & Operations", "Personnel & Organization",
            "Technical Components"
        ],
        "professional_indicators": [  # 专业术语指示词
            "system", "unit", "component", "device", "equipment", "platform", "weapon",
            "missile", "aircraft", "radar", "sensor", "navigation", "guidance", "control"
        ],
        "deduplication_rules": {  # 去重规则
            "merge_similar_terms": True,  # 合并相似术语
            "prefer_full_forms": True,  # 优先完整形式
            "standardize_abbreviations": True  # 标准化缩写
        }
    }
}

# =============================================================================
# 文件处理参数
# =============================================================================

FILE_PROCESSING = {
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "encoding": "utf-8",
    "supported_pdf_extractors": ["pdfplumber", "pymupdf", "pdfminer"],
    "supported_doc_extractors": ["python-docx", "docx2txt"],
    "fallback_encoding": ["gbk", "gb2312", "latin1"],
}

# =============================================================================
# 日志配置
# =============================================================================

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_rotation": {
        "max_bytes": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5
    }
}

# =============================================================================
# 验证和工具函数
# =============================================================================

def validate_config() -> bool:
    """
    验证配置有效性
    
    Returns:
        bool: 配置是否有效
    """
    # 检查API密钥
    if OPENAI_API_KEY == "your-openai-api-key-here":
        print("警告: 请设置正确的OpenAI API密钥")
        return False
    
    # 检查模型配置
    if not DEFAULT_MODEL:
        print("错误: 未设置默认模型")
        return False
    
    # 检查批处理配置
    required_batch_keys = ["temperature", "max_output_tokens", "max_concurrent"]
    for key in required_batch_keys:
        if key not in BATCH_CONFIG:
            print(f"错误: 批处理配置缺少必要参数: {key}")
            return False
    
    # 检查文本分割配置
    if TEXT_SPLITTING["default_chunk_size"] > TEXT_SPLITTING["max_chunk_size"]:
        print("错误: 默认块大小不能大于最大块大小")
        return False
    
    return True
def get_model_info(model: str) -> Dict[str, Any]:
    """
    获取模型信息
    
    Args:
        model: 模型名称
        
    Returns:
        Dict: 模型信息字典
    """
    return {
        "name": model,
        "token_param": get_token_param_name(model),
        "is_new_model": any(new_model.lower() in model.lower() 
                           for new_model in MODEL_API_PARAMS["new_models"]),
        "max_context": 128000 if "gpt-4" in model.lower() else 4096,
    }

def get_supported_formats() -> List[str]:
    """
    获取支持的文件格式列表
    
    Returns:
        List[str]: 支持的文件扩展名列表
    """
    return SUPPORTED_INPUT_FORMATS + [".pdf", ".docx", ".doc"]

def get_processing_stats() -> Dict[str, Any]:
    """
    获取处理统计信息
    
    Returns:
        Dict: 统计信息字典
    """
    return {
        "supported_formats": len(get_supported_formats()),
        "default_chunk_size": TEXT_SPLITTING["default_chunk_size"],
        "max_concurrent": BATCH_CONFIG["max_concurrent"],
        "quality_controls_enabled": len(TERM_PROCESSING["quality_controls"]),
    }

# =============================================================================
# 配置验证和初始化
# =============================================================================

if __name__ == "__main__":
    # 配置验证
    if validate_config():
        print("✅ 配置验证通过")
        print(f"默认模型: {DEFAULT_MODEL}")
        print(f"Token参数: {get_token_param_name(DEFAULT_MODEL)}")
        
        # 显示配置摘要
        stats = get_processing_stats()
        print(f"支持格式: {stats['supported_formats']} 种")
        print(f"默认块大小: {stats['default_chunk_size']:,} 字符")
        print(f"最大并发: {stats['max_concurrent']}")
    else:
        print("❌ 配置验证失败")
        exit(1)
