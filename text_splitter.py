#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文本切片模块
将长文本按照段落、语义边界和token限制切分为适合AI处理的片段
支持多种分割策略和重叠处理
"""

import re
import logging
from typing import List, Dict, Union
from dataclasses import dataclass

# 配置日志
logger = logging.getLogger(__name__)

# =============================================================================
# 依赖检查
# =============================================================================

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
    logger.info("✅ tiktoken 可用")
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("⚠️  tiktoken 不可用，将使用字符估算")


# =============================================================================
# 数据结构
# =============================================================================

@dataclass
class TextChunk:
    """文本块数据结构"""
    content: str
    start_pos: int
    end_pos: int
    tokens: int
    chunk_id: int
    metadata: Dict[str, Union[str, int]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SplitResult:
    """分割结果数据结构"""
    chunks: List[TextChunk]
    total_chunks: int
    total_tokens: int
    original_length: int
    overlap_info: Dict[str, int]


# =============================================================================
# Token计算器
# =============================================================================

class TokenCounter:
    """Token计算器"""
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        """
        初始化Token计算器
        
        Args:
            encoding_name: tiktoken编码名称
        """
        self.encoding_name = encoding_name
        self.encoding = None
        self._init_encoding()
    
    def _init_encoding(self):
        """初始化编码器"""
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.get_encoding(self.encoding_name)
                logger.debug(f"使用tiktoken编码器: {self.encoding_name}")
            except Exception as e:
                logger.warning(f"tiktoken初始化失败: {e}")
                self.encoding = None
        
        if not self.encoding:
            logger.info("使用字符估算模式 (1 token ≈ 4 字符)")
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的token数量
        
        Args:
            text: 输入文本
            
        Returns:
            int: token数量
        """
        if not text:
            return 0
        
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception:
                pass
        
        # 回退到字符估算：中文约2字符=1token，英文约4字符=1token
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        other_chars = len(text) - chinese_chars
        return int(chinese_chars * 0.5 + other_chars * 0.25)
    
    def estimate_tokens(self, char_count: int) -> int:
        """
        根据字符数估算token数
        
        Args:
            char_count: 字符数
            
        Returns:
            int: 估算的token数
        """
        return max(1, int(char_count * 0.3))  # 保守估算


# =============================================================================
# 文本分割器
# =============================================================================

class TextSplitter:
    """智能文本分割器"""
    
    def __init__(self, 
                 max_tokens: int = 3000,
                 overlap_tokens: int = 200,
                 encoding_name: str = "cl100k_base"):
        """
        初始化文本分割器
        
        Args:
            max_tokens: 每个片段的最大token数
            overlap_tokens: 片段间重叠的token数
            encoding_name: token编码方式
        """
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.token_counter = TokenCounter(encoding_name)
        
        # 分割策略配置
        self.split_patterns = self._init_split_patterns()
        
        logger.info(f"文本分割器初始化: max_tokens={max_tokens}, overlap={overlap_tokens}")
    
    def _init_split_patterns(self) -> List[Dict[str, Union[str, int]]]:
        """初始化分割模式"""
        return [
            {"pattern": r'\n\s*\n\s*\n+', "priority": 1, "name": "多空行"},
            {"pattern": r'\n\s*\n', "priority": 2, "name": "双换行"},
            {"pattern": r'[。！？；]\s*\n', "priority": 3, "name": "句末换行"},
            {"pattern": r'[。！？；]\s+', "priority": 4, "name": "句末空格"},
            {"pattern": r'[，、]\s*\n', "priority": 5, "name": "逗号换行"},
            {"pattern": r'\n', "priority": 6, "name": "单换行"},
            {"pattern": r'[，、]\s+', "priority": 7, "name": "逗号空格"},
            {"pattern": r'\s+', "priority": 8, "name": "空格"},
        ]
    
    # =============================================================================
    # 主要分割方法
    # =============================================================================
    
    def split_text(self, text: str) -> List[str]:
        """
        分割文本为字符串列表（向后兼容）
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 分割后的文本片段
        """
        result = self.split_text_advanced(text)
        return [chunk.content for chunk in result.chunks]
    
    def split_text_advanced(self, text: str) -> SplitResult:
        """
        高级文本分割，返回详细结果
        
        Args:
            text: 输入文本
            
        Returns:
            SplitResult: 分割结果
        """
        if not text or not text.strip():
            return SplitResult(
                chunks=[],
                total_chunks=0,
                total_tokens=0,
                original_length=0,
                overlap_info={}
            )
        
        # 预处理文本
        processed_text = self._preprocess_text(text)
        
        # 检查是否需要分割
        total_tokens = self.token_counter.count_tokens(processed_text)
        if total_tokens <= self.max_tokens:
            return self._create_single_chunk_result(processed_text, total_tokens)
        
        # 执行分割
        chunks = self._split_by_patterns(processed_text)
        
        # 后处理：合并小块、添加重叠
        chunks = self._post_process_chunks(chunks)
        
        return self._create_split_result(chunks, len(text))
    
    def split_text_with_metadata(self, text: str, source_file: str = "") -> List[str]:
        """
        带元数据的文本分割
        
        Args:
            text: 输入文本
            source_file: 来源文件名
            
        Returns:
            List[str]: 带标签的文本片段
        """
        result = self.split_text_advanced(text)
        
        labeled_chunks = []
        for i, chunk in enumerate(result.chunks, 1):
            if result.total_chunks > 1:
                # 计算token数用于显示
                token_count = self.token_counter.count_tokens(chunk.content)
                label = f"[文件: {source_file} - 片段 {i}/{result.total_chunks} ({token_count} tokens)]"
                labeled_content = f"{label}\n{chunk.content}"
            else:
                labeled_content = f"[文件: {source_file}]\n{chunk.content}"
            
            labeled_chunks.append(labeled_content)
        
        return labeled_chunks
    
    # =============================================================================
    # 特定分割策略
    # =============================================================================
    
    def split_by_paragraphs(self, text: str) -> List[str]:
        """
        按段落分割文本
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 段落列表
        """
        if not text:
            return []
        
        # 按双换行分割段落
        paragraphs = re.split(r'\n\s*\n', text.strip())
        
        # 过滤空段落并清理
        clean_paragraphs = []
        for para in paragraphs:
            clean_para = para.strip()
            if clean_para:
                clean_paragraphs.append(clean_para)
        
        # 如果段落太少，按单换行再分割
        if len(clean_paragraphs) < 2:
            paragraphs = text.split('\n')
            clean_paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return clean_paragraphs
    
    def split_by_sentences(self, text: str) -> List[str]:
        """
        按句子分割文本
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 句子列表
        """
        if not text:
            return []
        
        # 中英文句子分割模式
        sentence_pattern = r'[。！？；.!?;]\s*'
        sentences = re.split(sentence_pattern, text)
        
        # 清理并过滤空句子
        clean_sentences = []
        for sentence in sentences:
            clean_sentence = sentence.strip()
            if clean_sentence:
                clean_sentences.append(clean_sentence)
        
        return clean_sentences
    
    def split_by_length(self, text: str, max_length: int = None) -> List[str]:
        """
        按长度分割文本
        
        Args:
            text: 输入文本
            max_length: 最大长度（字符数），默认使用token估算
            
        Returns:
            List[str]: 分割后的文本块
        """
        if not text:
            return []
        
        if max_length is None:
            max_length = int(self.max_tokens * 3.5)  # 保守的字符估算
        
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_length
            
            if end >= len(text):
                # 最后一块
                chunks.append(text[start:])
                break
        
            # 尝试在合适的位置切断
            cut_pos = self._find_best_cut_position(text, start, end)
            chunks.append(text[start:cut_pos])
            
            # 计算下一个起始位置（考虑重叠）
            overlap_length = int(max_length * 0.1)  # 10%重叠
            start = max(cut_pos - overlap_length, cut_pos)
        
        return chunks
    
    # =============================================================================
    # 内部处理方法
    # =============================================================================
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 统一换行符
        text = re.sub(r'\r\n|\r', '\n', text)
        
        # 清理多余的空白字符
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # 多个空行变为双空行
        text = re.sub(r'[ \t]+', ' ', text)  # 多个空格变为单个空格
        
        # 清理首尾空白
        text = text.strip()
        
        return text
    
    def _split_by_patterns(self, text: str) -> List[TextChunk]:
        """使用模式分割文本"""
        chunks = []
        current_pos = 0
        chunk_id = 0
        
        while current_pos < len(text):
            # 计算当前块的结束位置
            end_pos = self._find_chunk_end(text, current_pos)
            
            if end_pos > current_pos:
                chunk_content = text[current_pos:end_pos].strip()
                if chunk_content:
                    token_count = self.token_counter.count_tokens(chunk_content)
                    
                    chunk = TextChunk(
                        content=chunk_content,
                        start_pos=current_pos,
                        end_pos=end_pos,
                        tokens=token_count,
                        chunk_id=chunk_id
                    )
                    chunks.append(chunk)
                    chunk_id += 1
            
            current_pos = end_pos
        
        return chunks
    
    def _find_chunk_end(self, text: str, start_pos: int) -> int:
        """找到块的最佳结束位置"""
        max_end = min(start_pos + int(self.max_tokens * 4), len(text))
        
        # 如果剩余文本很短，直接返回结尾
        if max_end >= len(text):
            return len(text)
        
        # 在最大范围内寻找最佳切分点
        best_pos = max_end
        
        for pattern_info in self.split_patterns:
            pattern = pattern_info["pattern"]
            matches = list(re.finditer(pattern, text[start_pos:max_end]))
            
            if matches:
                # 选择最接近目标长度的匹配
                target_pos = int(self.max_tokens * 3)  # 目标字符位置
                best_match = min(matches, 
                               key=lambda m: abs(m.end() - target_pos))
                
                candidate_pos = start_pos + best_match.end()
                
                # 验证token数量
                chunk_text = text[start_pos:candidate_pos]
                if self.token_counter.count_tokens(chunk_text) <= self.max_tokens:
                    best_pos = candidate_pos
                    break
        
        return best_pos
    
    def _find_best_cut_position(self, text: str, start: int, max_end: int) -> int:
        """找到最佳切分位置"""
        if max_end >= len(text):
            return len(text)
        
        # 在最后20%的范围内寻找合适的切分点
        search_start = max_end - int((max_end - start) * 0.2)
        search_text = text[search_start:max_end]
        
        for pattern_info in self.split_patterns[:4]:  # 只使用前4个高优先级模式
            pattern = pattern_info["pattern"]
            matches = list(re.finditer(pattern, search_text))
            
            if matches:
                # 选择最后一个匹配
                last_match = matches[-1]
                return search_start + last_match.end()
        
        # 如果找不到合适的切分点，就在最大位置切分
        return max_end
    
    def _post_process_chunks(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """后处理文本块"""
        if not chunks:
            return chunks
        
        # 合并过小的块
        processed_chunks = self._merge_small_chunks(chunks)
        
        # 添加重叠内容
        if self.overlap_tokens > 0:
            processed_chunks = self._add_overlap(processed_chunks)
        
        return processed_chunks
    
    def _merge_small_chunks(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """合并过小的文本块"""
        if len(chunks) <= 1:
            return chunks
        
        min_tokens = max(100, self.max_tokens // 4)  # 最小块大小
        merged_chunks = []
        i = 0
        
        while i < len(chunks):
            current_chunk = chunks[i]
            
            # 如果当前块太小，尝试与下一块合并
            if (current_chunk.tokens < min_tokens and 
                i + 1 < len(chunks) and
                current_chunk.tokens + chunks[i + 1].tokens <= self.max_tokens):
                
                next_chunk = chunks[i + 1]
                merged_content = current_chunk.content + "\n\n" + next_chunk.content
                merged_tokens = self.token_counter.count_tokens(merged_content)
                
                merged_chunk = TextChunk(
                    content=merged_content,
                    start_pos=current_chunk.start_pos,
                    end_pos=next_chunk.end_pos,
                    tokens=merged_tokens,
                    chunk_id=current_chunk.chunk_id,
                    metadata={"merged": True}
                )
                
                merged_chunks.append(merged_chunk)
                i += 2  # 跳过下一个块
            else:
                merged_chunks.append(current_chunk)
                i += 1
        
        return merged_chunks
    
    def _add_overlap(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """为文本块添加重叠内容"""
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            content = chunk.content
            
            # 添加前一个块的结尾作为重叠
            if i > 0:
                prev_chunk = chunks[i - 1]
                overlap_text = self._extract_overlap_text(prev_chunk.content, True)
                if overlap_text:
                    content = overlap_text + "\n...\n" + content
            
            # 添加下一个块的开头作为重叠
            if i < len(chunks) - 1:
                next_chunk = chunks[i + 1]
                overlap_text = self._extract_overlap_text(next_chunk.content, False)
                if overlap_text:
                    content = content + "\n...\n" + overlap_text
            
            # 重新计算token数
            new_tokens = self.token_counter.count_tokens(content)
            
            overlapped_chunk = TextChunk(
                content=content,
                start_pos=chunk.start_pos,
                end_pos=chunk.end_pos,
                tokens=new_tokens,
                chunk_id=chunk.chunk_id,
                metadata={**(chunk.metadata or {}), "has_overlap": True}
            )
            
            overlapped_chunks.append(overlapped_chunk)
        
        return overlapped_chunks
    
    def _extract_overlap_text(self, text: str, from_end: bool) -> str:
        """提取重叠文本"""
        target_tokens = min(self.overlap_tokens, self.max_tokens // 4)
        
        if from_end:
            # 从文本结尾提取
            words = text.split()
            overlap_words = []
            current_tokens = 0
            
            for word in reversed(words):
                word_tokens = self.token_counter.count_tokens(word)
                if current_tokens + word_tokens > target_tokens:
                    break
                overlap_words.insert(0, word)
                current_tokens += word_tokens
            
            return ' '.join(overlap_words)
        else:
            # 从文本开头提取
            words = text.split()
            overlap_words = []
            current_tokens = 0
            
            for word in words:
                word_tokens = self.token_counter.count_tokens(word)
                if current_tokens + word_tokens > target_tokens:
                    break
                overlap_words.append(word)
                current_tokens += word_tokens
            
            return ' '.join(overlap_words)
    
    def _create_single_chunk_result(self, text: str, tokens: int) -> SplitResult:
        """创建单块结果"""
        chunk = TextChunk(
            content=text,
            start_pos=0,
            end_pos=len(text),
            tokens=tokens,
            chunk_id=0
        )
        
        return SplitResult(
            chunks=[chunk],
            total_chunks=1,
            total_tokens=tokens,
            original_length=len(text),
            overlap_info={}
        )
    
    def _create_split_result(self, chunks: List[TextChunk], original_length: int) -> SplitResult:
        """创建分割结果"""
        total_tokens = sum(chunk.tokens for chunk in chunks)
        
        overlap_info = {
            "enabled": self.overlap_tokens > 0,
            "target_tokens": self.overlap_tokens,
            "chunks_with_overlap": len([c for c in chunks if c.metadata and c.metadata.get("has_overlap")])
        }
        
        return SplitResult(
            chunks=chunks,
            total_chunks=len(chunks),
            total_tokens=total_tokens,
            original_length=original_length,
            overlap_info=overlap_info
        )
    
    # =============================================================================
    # 工具方法
    # =============================================================================
    
    def get_stats(self, text: str) -> Dict[str, Union[int, float]]:
        """获取文本统计信息"""
        if not text:
            return {"chars": 0, "tokens": 0, "estimated_chunks": 0}
        
        chars = len(text)
        tokens = self.token_counter.count_tokens(text)
        estimated_chunks = max(1, (tokens + self.max_tokens - 1) // self.max_tokens)
        
        return {
            "chars": chars,
            "tokens": tokens,
            "estimated_chunks": estimated_chunks,
            "avg_tokens_per_chunk": tokens / estimated_chunks if estimated_chunks > 0 else 0
        }


# =============================================================================
# 便捷函数
# =============================================================================

def create_text_splitter(max_tokens: int = 3000, overlap_tokens: int = 200) -> TextSplitter:
    """
    创建文本分割器实例
    
    Args:
        max_tokens: 最大token数
        overlap_tokens: 重叠token数
        
    Returns:
        TextSplitter: 分割器实例
    """
    return TextSplitter(max_tokens=max_tokens, overlap_tokens=overlap_tokens)


def split_text_simple(text: str, max_tokens: int = 3000) -> List[str]:
    """
    简单文本分割函数
    
    Args:
        text: 输入文本
        max_tokens: 最大token数
        
    Returns:
        List[str]: 分割后的文本列表
    """
    splitter = create_text_splitter(max_tokens=max_tokens)
    return splitter.split_text(text)


if __name__ == "__main__":
    # 简单测试
    splitter = create_text_splitter()
    
    test_text = "这是一个测试文本。" * 100
    stats = splitter.get_stats(test_text)
    
    print("文本分割器测试:")
    print(f"字符数: {stats['chars']}")
    print(f"Token数: {stats['tokens']}")
    print(f"预估块数: {stats['estimated_chunks']}")
    
    chunks = splitter.split_text(test_text)
    print(f"实际块数: {len(chunks)}")