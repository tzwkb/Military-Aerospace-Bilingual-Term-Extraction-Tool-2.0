#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件类型检测和文本提取模块
支持多种文件格式的智能检测和文本提取，包括PDF、DOCX、图片OCR等
"""

import os
import logging
import importlib.util
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any, Union

# 配置日志
logger = logging.getLogger(__name__)

# =============================================================================
# 依赖检查和导入
# =============================================================================

class DependencyManager:
    """依赖管理器"""
    
    def __init__(self):
        self.available_modules = {}
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查可选依赖"""
        # PDF处理 - 使用pdfminer.six + PyPDF2备用
        if importlib.util.find_spec('pdfminer'):
            self.available_modules['pdf'] = ['pdfminer.six']
        elif importlib.util.find_spec('PyPDF2'):
            self.available_modules['pdf'] = ['PyPDF2']
        else:
            self.available_modules['pdf'] = []
        
        # DOCX处理
        if importlib.util.find_spec('docx'):
            self.available_modules['docx'] = ['python-docx']
        else:
            self.available_modules['docx'] = []
        
        # 文件类型检测
        if importlib.util.find_spec('magic'):
            self.available_modules['magic'] = ['python-magic']
        else:
            self.available_modules['magic'] = []
        
        # OCR功能 - 使用PaddleOCR
        if importlib.util.find_spec('paddleocr'):
            self.available_modules['ocr'] = ['paddleocr']
        else:
            self.available_modules['ocr'] = []
        
        self._log_dependencies()
    
    def _log_dependencies(self):
        """记录依赖状态"""
        for module, deps in self.available_modules.items():
            if deps:
                logger.info(f"✅ {module.upper()} 支持: {', '.join(deps)}")
            else:
                logger.warning(f"⚠️  {module.upper()} 不可用")
    
    def is_available(self, module: str) -> bool:
        """检查模块是否可用"""
        return bool(self.available_modules.get(module, []))


# 全局依赖管理器
deps = DependencyManager()


# =============================================================================
# 文件类型检测
# =============================================================================

class FileTypeDetector:
    """文件类型检测器"""
    
    # 支持的MIME类型映射
    SUPPORTED_TYPES = {
        'text': ['text/plain', 'text/html', 'text/xml', 'application/xml'],
        'pdf': ['application/pdf'],
        'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        'doc': ['application/msword'],
        'image': ['image/jpeg', 'image/png', 'image/tiff', 'image/bmp', 'image/gif']
    }
    
    @staticmethod
    def detect_file_type(file_path: str) -> Tuple[str, str]:
        """
        检测文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[str, str]: (文件类型, MIME类型)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 首先尝试使用python-magic
        if deps.is_available('magic'):
            try:
                import magic
                mime_type = magic.from_file(file_path, mime=True)
                return FileTypeDetector._categorize_mime_type(mime_type), mime_type
            except Exception as e:
                logger.warning(f"Magic检测失败: {e}")
        
        # 回退到基于扩展名的检测
        return FileTypeDetector._detect_by_extension(file_path)
    
    @staticmethod
    def _detect_by_extension(file_path: str) -> Tuple[str, str]:
        """基于文件扩展名检测类型"""
        ext = Path(file_path).suffix.lower()
        
        # 扩展名映射
        extension_map = {
            '.txt': ('text', 'text/plain'),
            '.md': ('text', 'text/markdown'),
            '.html': ('text', 'text/html'),
            '.xml': ('text', 'application/xml'),
            '.pdf': ('pdf', 'application/pdf'),
            '.docx': ('docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            '.doc': ('doc', 'application/msword'),
            '.jpg': ('image', 'image/jpeg'),
            '.jpeg': ('image', 'image/jpeg'),
            '.png': ('image', 'image/png'),
            '.tiff': ('image', 'image/tiff'),
            '.bmp': ('image', 'image/bmp'),
            '.gif': ('image', 'image/gif'),
        }
        
        return extension_map.get(ext, ('unknown', 'application/octet-stream'))
    
    @staticmethod
    def _categorize_mime_type(mime_type: str) -> str:
        """根据MIME类型分类"""
        for category, mime_list in FileTypeDetector.SUPPORTED_TYPES.items():
            if mime_type in mime_list:
                return category
        return 'unknown'


# =============================================================================
# 文本提取器
# =============================================================================

class TextExtractor:
    """文本提取器基类"""
    
    def extract(self, file_path: str) -> List[str]:
        """提取文本的抽象方法"""
        raise NotImplementedError


class PlainTextExtractor(TextExtractor):
    """纯文本提取器"""
    
    def extract(self, file_path: str) -> List[str]:
        """提取纯文本文件内容"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read().strip()
                    if content:
                        logger.info(f"成功使用 {encoding} 编码读取文件")
                        return [content]
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"读取文件失败: {e}")
                break
        
        raise ValueError(f"无法读取文件 {file_path}，尝试了所有编码")


class PDFExtractor(TextExtractor):
    """PDF文本提取器 - 基于pdfminer.six，支持OCR降级"""
    
    def __init__(self, enable_ocr: bool = True, use_gpu: bool = False):
        """
        初始化PDF提取器
        
        Args:
            enable_ocr: 是否启用OCR降级功能
            use_gpu: 是否使用GPU加速（仅在需要OCR时生效）
        """
        self.enable_ocr = enable_ocr
        self.use_gpu = use_gpu
        self.ocr_extractor = None  # 延迟初始化，只在需要时创建
        logger.debug(f"PDFExtractor初始化: enable_ocr={enable_ocr}, use_gpu={use_gpu}")
    
    def extract(self, file_path: str) -> List[str]:
        """提取PDF文件内容，自动降级到OCR"""
        if not deps.is_available('pdf'):
            raise RuntimeError("PDF处理库不可用，请安装 pdfminer.six")
        
        # 优先使用pdfminer.six（主要方法）
        if 'pdfminer.six' in deps.available_modules['pdf']:
            return self._extract_with_pdfminer(file_path)
        else:
            # 备用方案：PyPDF2
            return self._extract_with_pypdf2(file_path)
    
    def _extract_with_pdfminer(self, file_path: str) -> List[str]:
        """使用pdfminer.six提取PDF文本"""
        try:
            from pdfminer.high_level import extract_text
            from pdfminer.layout import LAParams
            from pathlib import Path
            import re
            
            # 优化的布局参数（学术文档专用）
            laparams = LAParams(
                line_overlap=0.5,
                char_margin=2.0,
                line_margin=0.5,
                word_margin=0.3,  # 确保单词正确分离
                boxes_flow=0.5,
                detect_vertical=True,
                all_texts=True
            )
            
            full_text = extract_text(file_path, laparams=laparams)
            
            # 检查提取的文本质量
            text_stripped = full_text.strip() if full_text else ""
            
            # 如果文本为空、太短，或只有元数据，尝试OCR降级
            is_scanned = False
            if not full_text or not text_stripped:
                is_scanned = True
                reason = "PDF为空"
            elif len(text_stripped) < 200:  # 文本太短，可能只有元数据
                is_scanned = True
                reason = f"提取文本太短（{len(text_stripped)}字符），可能是扫描版"
            elif "[General Information]" in text_stripped and len(text_stripped) < 500:
                is_scanned = True
                reason = "只提取到元数据信息"
            
            if is_scanned:
                logger.warning(f"检测到扫描版PDF: {Path(file_path).name} - {reason}")
                
                # 如果启用了OCR功能，自动降级到OCR
                if self.enable_ocr:
                    logger.info("自动降级到OCR处理...")
                    return self._extract_with_ocr(file_path)
                else:
                    raise ValueError("扫描版PDF需要OCR处理，但OCR功能未启用")
            
            # 智能文本后处理
            full_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', full_text)  # 小写后跟大写
            full_text = re.sub(r'([A-Z]{2,})([A-Z][a-z])', r'\1 \2', full_text)  # 连续大写后跟单词
            full_text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', full_text)  # 数字后跟字母
            full_text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', full_text)  # 字母后跟数字
            full_text = re.sub(r'\s+', ' ', full_text)  # 清理多余空格
            
            # 直接返回处理后的文本，不添加文件名标题
            texts = [full_text.strip()]
            logger.info(f"使用pdfminer.six成功提取: {len(full_text)} 字符")
            return texts
            
        except Exception as e:
            logger.error(f"pdfminer.six提取失败: {e}")
            
            # 检查是否应该降级到OCR
            if "扫描版" in str(e) or "需要OCR" in str(e):
                if self.ocr_extractor:
                    logger.info("pdfminer失败，自动降级到OCR处理...")
                    return self._extract_with_ocr(file_path)
            
            # 简单回退策略
            if 'PyPDF2' in deps.available_modules['pdf']:
                return self._extract_with_pypdf2(file_path)
            raise ValueError(f"PDF文件处理失败: {e}")
    
    def _get_pdf_page_count(self, file_path: str) -> int:
        """获取PDF页数"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return len(reader.pages)
        except Exception as e:
            logger.warning(f"无法获取PDF页数: {e}")
            return 0
    
    def _extract_with_ocr(self, file_path: str) -> List[str]:
        """使用OCR处理扫描版PDF（支持分批处理）"""
        try:
            logger.info(f"使用OCR处理PDF: {Path(file_path).name}")
            logger.warning("注意: 大型扫描版PDF的OCR处理需要较长时间")
            
            # 懒加载：只在需要OCR时才初始化PaddleOCR
            if self.ocr_extractor is None:
                if not self.enable_ocr:
                    raise ValueError("OCR功能未启用")
                
                if not deps.is_available('ocr'):
                    raise ValueError("OCR库不可用，请安装: pip install paddleocr paddlepaddle")
                
                logger.info("🔄 正在初始化PaddleOCR引擎（首次使用需要加载模型）...")
                try:
                    self.ocr_extractor = PaddleOCRExtractor(use_gpu=self.use_gpu)
                    logger.info("✅ PaddleOCR初始化完成")
                except Exception as init_error:
                    logger.error(f"❌ PaddleOCR初始化失败: {init_error}")
                    raise ValueError(f"无法初始化OCR引擎: {init_error}")
            
            # 检查文件大小和页数
            file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
            page_count = self._get_pdf_page_count(file_path)
            
            print(f"\n{'='*70}")
            print(f"📊 PDF文件信息:")
            print(f"   文件名: {Path(file_path).name}")
            print(f"   大小: {file_size_mb:.2f} MB")
            print(f"   页数: {page_count} 页")
            print(f"{'='*70}\n")
            logger.info(f"PDF信息: {file_size_mb:.2f} MB, {page_count}页")
            
            # 分批处理策略（从配置读取）
            try:
                from config import PDF_OCR_CONFIG
                batch_enabled = PDF_OCR_CONFIG.get("enable_batch_processing", True)
                batch_threshold_pages = PDF_OCR_CONFIG.get("batch_threshold_pages", 50)
                batch_threshold_mb = PDF_OCR_CONFIG.get("batch_threshold_mb", 50)
                batch_size = PDF_OCR_CONFIG.get("batch_size", 20)
                max_retries = PDF_OCR_CONFIG.get("max_retries", 3)
                retry_delay = PDF_OCR_CONFIG.get("retry_delay", 2)
                
                print(f"📋 分批处理配置:")
                print(f"   启用分批: {batch_enabled}")
                print(f"   页数阈值: {batch_threshold_pages} 页")
                print(f"   大小阈值: {batch_threshold_mb} MB")
                print(f"   批次大小: {batch_size} 页/批")
                print(f"   最大重试: {max_retries} 次")
            except ImportError:
                # 如果无法导入配置，使用默认值
                batch_enabled = True
                batch_threshold_pages = 50
                batch_threshold_mb = 50
                batch_size = 20
                max_retries = 3
                retry_delay = 2
                print(f"⚠️ 使用默认分批配置")
            
            should_batch = batch_enabled and (
                (page_count > batch_threshold_pages or file_size_mb > batch_threshold_mb) 
                and page_count > 0
            )
            
            if should_batch:
                print(f"\n✅ 将使用分批处理模式（每批{batch_size}页）")
                print(f"💡 提示: 可在config.py的PDF_OCR_CONFIG中调整分批参数\n")
                logger.info(f"📑 检测到大型PDF，将分批处理（每批{batch_size}页）")
                logger.info(f"💡 提示: 可在config.py的PDF_OCR_CONFIG中调整分批参数")
                return self._extract_pdf_in_batches(file_path, page_count, batch_size, max_retries, retry_delay)
            else:
                # 小文件直接处理
                print(f"\n✅ 将使用直接处理模式")
                if file_size_mb > 20 or page_count > 20:
                    print(f"⚠️ PDF较大，处理可能需要较长时间")
                    logger.warning(f"⚠️ PDF较大({file_size_mb:.2f} MB, {page_count}页)，处理可能需要较长时间")
                print()
                
                # 使用OCR提取器处理
                try:
                    result = self.ocr_extractor.extract(file_path)
                    print(f"✅ OCR成功处理PDF\n")
                    logger.info(f"✅ OCR成功处理PDF")
                    return result
                except KeyboardInterrupt:
                    logger.warning("用户中断OCR处理")
                    raise
                except Exception as ocr_error:
                    logger.error(f"OCR直接处理失败: {type(ocr_error).__name__}: {ocr_error}")
                    
                    # 尝试降级到分批处理
                    if page_count > 0:
                        logger.warning(f"⚠️ 直接OCR失败，尝试分批处理作为降级方案...")
                        try:
                            return self._extract_pdf_in_batches(file_path, page_count, batch_size, max_retries, retry_delay)
                        except Exception as batch_error:
                            logger.error(f"分批处理也失败: {batch_error}")
                            raise RuntimeError(f"OCR处理失败（直接处理和分批处理均失败）: {ocr_error}")
                    else:
                        raise
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"OCR处理PDF失败: {e}")
            logger.error(f"错误类型: {type(e).__name__}")
            import traceback
            logger.error(f"详细堆栈:\n{traceback.format_exc()}")
            
            # 如果直接OCR失败，建议用户手动处理
            raise ValueError(
                f"OCR处理大型PDF失败: {e}\n"
                f"建议: 对于大型扫描版PDF（{Path(file_path).name}），"
                f"可以使用专门的PDF转图片工具预处理后再提取术语"
            )
    
    def _extract_pdf_in_batches(self, file_path: str, total_pages: int, batch_size: int, max_retries: int = 3, retry_delay: int = 2) -> List[str]:
        """
        分批OCR处理PDF（避免内存溢出）
        
        Args:
            file_path: PDF文件路径
            total_pages: 总页数
            batch_size: 每批处理的页数
            
        Returns:
            List[str]: 提取的文本列表
        """
        import tempfile
        import shutil
        try:
            import PyPDF2
        except ImportError:
            raise ValueError("分批处理需要PyPDF2库，请安装: pip install PyPDF2")
        
        all_texts = []
        temp_dir = None
        
        # 创建extracted_texts目录（如果不存在）
        output_dir = Path("extracted_texts")
        output_dir.mkdir(exist_ok=True)
        
        # 生成输出文件名（基于原PDF文件名）
        pdf_name = Path(file_path).stem
        batch_output_file = output_dir / f"{pdf_name}_batch_ocr.txt"
        
        # 清理旧的输出文件（如果存在）
        if batch_output_file.exists():
            logger.info(f"🗑️ 删除旧的批次结果文件")
            batch_output_file.unlink()
        
        try:
            # 创建临时目录存放分割的PDF
            temp_dir = tempfile.mkdtemp(prefix="pdf_batch_")
            logger.info(f"📁 临时目录: {temp_dir}")
            logger.info(f"💾 中间结果将实时保存到: {batch_output_file}")
            
            # 计算批次数
            num_batches = (total_pages + batch_size - 1) // batch_size
            print(f"\n{'='*70}")
            print(f"📊 分批处理计划:")
            print(f"   总页数: {total_pages} 页")
            print(f"   批次大小: {batch_size} 页/批")
            print(f"   批次数量: {num_batches} 批")
            print(f"   结果文件: {batch_output_file}")
            print(f"{'='*70}\n")
            logger.info(f"📊 将处理 {num_batches} 个批次，共 {total_pages} 页")
            
            # 打开原始PDF
            with open(file_path, 'rb') as input_pdf:
                pdf_reader = PyPDF2.PdfReader(input_pdf)
                
                # 分批处理
                for batch_idx in range(num_batches):
                    start_page = batch_idx * batch_size
                    end_page = min((batch_idx + 1) * batch_size, total_pages)
                    current_batch_size = end_page - start_page
                    
                    print(f"\n{'='*70}")
                    print(f"📖 批次 {batch_idx + 1}/{num_batches}: 页 {start_page + 1}-{end_page} ({current_batch_size}页)")
                    print(f"{'='*70}")
                    logger.info(f"\n{'='*60}")
                    logger.info(f"📖 批次 {batch_idx + 1}/{num_batches}: 页 {start_page + 1}-{end_page}")
                    logger.info(f"{'='*60}")
                    
                    # 创建临时PDF（只包含当前批次的页面）
                    batch_pdf_path = Path(temp_dir) / f"batch_{batch_idx + 1}.pdf"
                    pdf_writer = PyPDF2.PdfWriter()
                    
                    for page_num in range(start_page, end_page):
                        try:
                            pdf_writer.add_page(pdf_reader.pages[page_num])
                        except Exception as e:
                            logger.warning(f"⚠️ 跳过第{page_num + 1}页: {e}")
                            continue
                    
                    # 保存临时PDF
                    with open(batch_pdf_path, 'wb') as output_pdf:
                        pdf_writer.write(output_pdf)
                    
                    batch_size_mb = batch_pdf_path.stat().st_size / (1024 * 1024)
                    logger.info(f"💾 临时文件: {batch_pdf_path.name} ({batch_size_mb:.2f} MB)")
                    
                    # OCR处理当前批次（带重试机制）
                    batch_success = False
                    for retry_attempt in range(max_retries):
                        try:
                            if retry_attempt > 0:
                                print(f"🔄 重试批次 {batch_idx + 1}/{num_batches} (第 {retry_attempt + 1}/{max_retries} 次尝试)...")
                                logger.info(f"🔄 重试批次 {batch_idx + 1}/{num_batches} (第 {retry_attempt + 1}/{max_retries} 次)")
                                import time
                                import gc
                                # 清理内存
                                gc.collect()
                                time.sleep(retry_delay)  # 重试前等待
                            else:
                                print(f"🔄 正在OCR识别批次 {batch_idx + 1}/{num_batches}...")
                                print(f"   ⚠️ 注意: 高分辨率PDF可能需要较长时间...")
                                logger.info(f"🔄 正在OCR识别批次 {batch_idx + 1}/{num_batches}...")
                            
                            import time
                            start_time = time.time()
                            
                            # 添加超时保护和异常捕获
                            try:
                                batch_result = self.ocr_extractor.extract(str(batch_pdf_path))
                            except KeyboardInterrupt:
                                raise  # 用户中断要传播
                            except Exception as ocr_inner_error:
                                # 捕获OCR内部错误
                                logger.error(f"OCR引擎内部错误: {type(ocr_inner_error).__name__}: {ocr_inner_error}")
                                raise RuntimeError(f"OCR处理失败: {ocr_inner_error}")
                            
                            elapsed = time.time() - start_time
                            if retry_attempt > 0:
                                print(f"✅ 批次 {batch_idx + 1} 重试成功，耗时 {elapsed:.1f}秒")
                                logger.info(f"✅ 批次 {batch_idx + 1} 重试成功 (尝试 {retry_attempt + 1}/{max_retries})，耗时 {elapsed:.1f}秒")
                            else:
                                print(f"✅ 批次 {batch_idx + 1} 完成，耗时 {elapsed:.1f}秒")
                                logger.info(f"✅ 批次 {batch_idx + 1} 完成，耗时 {elapsed:.1f}秒")
                            
                            # 添加批次标记
                            batch_texts = []
                            for text in batch_result:
                                marked_text = f"[批次 {batch_idx + 1}: 页{start_page + 1}-{end_page}]\n{text}"
                                batch_texts.append(marked_text)
                                all_texts.append(marked_text)
                            
                            # 立即保存当前批次结果到文件（追加模式）
                            try:
                                with open(batch_output_file, 'a', encoding='utf-8') as f:
                                    if batch_idx == 0:
                                        # 第一批次添加文件头
                                        f.write(f"{'='*70}\n")
                                        f.write(f"OCR分批处理结果\n")
                                        f.write(f"文件: {Path(file_path).name}\n")
                                        f.write(f"总页数: {total_pages}\n")
                                        f.write(f"批次大小: {batch_size}页/批\n")
                                        f.write(f"{'='*70}\n\n")
                                    
                                    # 写入当前批次内容
                                    f.write(f"\n{'='*70}\n")
                                    f.write(f"批次 {batch_idx + 1}/{num_batches} (页{start_page + 1}-{end_page})\n")
                                    f.write(f"{'='*70}\n\n")
                                    for batch_text in batch_texts:
                                        f.write(batch_text)
                                        f.write("\n\n")
                                    f.flush()  # 确保立即写入磁盘
                                
                                print(f"💾 批次 {batch_idx + 1} 结果已保存")
                                logger.info(f"💾 批次 {batch_idx + 1} 结果已保存")
                                
                            except Exception as save_error:
                                print(f"⚠️ 保存批次 {batch_idx + 1} 结果失败: {save_error}")
                                logger.warning(f"⚠️ 保存批次 {batch_idx + 1} 结果失败: {save_error}")
                            
                            # 删除临时PDF释放空间
                            batch_pdf_path.unlink()
                            
                            # 强制清理内存
                            import gc
                            gc.collect()
                            
                            batch_success = True
                            break  # 成功，跳出重试循环
                            
                        except Exception as e:
                            if retry_attempt < max_retries - 1:
                                print(f"⚠️ 批次 {batch_idx + 1} 处理失败: {e}")
                                print(f"   将在 {retry_delay} 秒后重试...")
                                logger.warning(f"批次 {batch_idx + 1} 处理失败 (尝试 {retry_attempt + 1}/{max_retries}): {e}")
                            else:
                                print(f"❌ 批次 {batch_idx + 1} 处理失败 (已重试 {max_retries} 次): {e}")
                                print(f"⚠️ 将跳过批次 {batch_idx + 1}，继续处理下一批次")
                                logger.error(f"❌ 批次 {batch_idx + 1} 最终失败 (已重试 {max_retries} 次): {e}")
                                logger.warning(f"⚠️ 将跳过批次 {batch_idx + 1}，继续处理下一批次")
                    
                    # 如果重试后仍然失败，继续下一批次
                    if not batch_success:
                        continue
                    
                    # 显示整体进度
                    progress = ((batch_idx + 1) / num_batches) * 100
                    print(f"\n📈 总进度: {progress:.1f}% ({batch_idx + 1}/{num_batches})")
                    print(f"📄 已保存文本: {batch_output_file}\n")
                    logger.info(f"📈 总进度: {progress:.1f}% ({batch_idx + 1}/{num_batches})")
                    logger.info(f"📄 已保存文本: {batch_output_file}")
            
            if not all_texts:
                raise ValueError("所有批次均处理失败，未提取到任何文本")
            
            # 写入完成标记
            try:
                with open(batch_output_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*70}\n")
                    f.write(f"✅ 所有批次处理完成\n")
                    f.write(f"   - 成功批次: {len(all_texts)}\n")
                    f.write(f"   - 总页数: {total_pages}\n")
                    f.write(f"{'='*70}\n")
                    f.flush()
            except Exception as e:
                logger.warning(f"写入完成标记失败: {e}")
            
            print(f"\n{'='*70}")
            print(f"🎉 分批处理完成！")
            print(f"   - 成功处理: {len(all_texts)} 个批次")
            print(f"   - 总页数: {total_pages}")
            print(f"   - 完整结果: {batch_output_file}")
            print(f"{'='*70}\n")
            logger.info(f"\n{'='*60}")
            logger.info(f"🎉 分批处理完成！")
            logger.info(f"   - 成功处理: {len(all_texts)} 个批次")
            logger.info(f"   - 总页数: {total_pages}")
            logger.info(f"   - 完整结果: {batch_output_file}")
            logger.info(f"{'='*60}\n")
            
            # 读取完整文件内容并返回（这样可以确保返回的内容与文件一致）
            try:
                with open(batch_output_file, 'r', encoding='utf-8') as f:
                    complete_text = f.read()
                return [complete_text]
            except Exception as e:
                logger.warning(f"读取完整文件失败: {e}，使用内存中的结果")
                # 降级方案：使用内存中的文本
                combined_text = f"[扫描版PDF - {Path(file_path).name}]\n分批OCR处理结果（共{total_pages}页，{len(all_texts)}批次）\n\n"
                combined_text += "\n\n".join(all_texts)
                return [combined_text]
            
        finally:
            # 清理临时目录
            if temp_dir and Path(temp_dir).exists():
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"🗑️ 已清理临时文件")
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {e}")
    
    def _extract_with_pypdf2(self, file_path: str) -> List[str]:
        """使用PyPDF2提取PDF文本（备用方法）"""
        try:
            import PyPDF2
            
            texts = []
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                for i, page in enumerate(reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            # 简单的文本后处理
                            import re
                            text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
                            text = re.sub(r'([A-Z]{2,})([A-Z][a-z])', r'\1 \2', text)
                            text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
                            text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
                            text = re.sub(r'\s+', ' ', text)
                            texts.append(text.strip())
                    except Exception as e:
                        logger.warning(f"第{i}页提取失败: {e}")
                        continue
            
            if not texts:
                raise ValueError("PDF文件为空或无法提取文本")
            
            logger.info(f"使用PyPDF2成功提取 {len(texts)} 页")
            return texts
            
        except Exception as e:
            logger.error(f"PyPDF2提取失败: {e}")
            raise ValueError(f"PDF文件处理失败: {e}")
    
    def extract_with_custom_params(self, file_path: str, **custom_params) -> List[str]:
        """使用自定义参数提取PDF文本"""
        # 临时更新参数
        original_params = self.layout_params.copy()
        self.layout_params.update(custom_params)
        
        try:
            return self.extract(file_path)
        finally:
            # 恢复原始参数
            self.layout_params = original_params


class DOCXExtractor(TextExtractor):
    """DOCX文档提取器"""
    
    def extract(self, file_path: str) -> List[str]:
        """提取DOCX文件内容"""
        if not deps.is_available('docx'):
            raise RuntimeError("DOCX处理库不可用，请安装 python-docx")
        
        try:
            from docx import Document
            
            doc = Document(file_path)
            paragraphs = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
            
            if not paragraphs:
                raise ValueError("DOCX文件为空或无文本内容")
            
            # 将段落合并为完整文档
            full_text = '\n\n'.join(paragraphs)
            logger.info(f"成功提取DOCX文档，共 {len(paragraphs)} 个段落")
            
            return [f"[DOCX文档]\n{full_text}"]
            
        except Exception as e:
            logger.error(f"DOCX提取失败: {e}")
            raise ValueError(f"DOCX文件处理失败: {e}")


class ImageExtractorWrapper(TextExtractor):
    """图片OCR提取器包装类 - 懒加载模式"""
    
    def __init__(self, use_gpu: bool = False):
        """
        初始化图片提取器包装器
        
        Args:
            use_gpu: 是否使用GPU加速
        """
        self.use_gpu = use_gpu
        self.ocr_extractor = None  # 延迟初始化
    
    def extract(self, file_path: str) -> List[str]:
        """提取图片文本（懒加载OCR）"""
        # 只在首次使用时初始化PaddleOCR
        if self.ocr_extractor is None:
            logger.info("🔄 正在初始化PaddleOCR引擎（首次使用需要加载模型）...")
            self.ocr_extractor = PaddleOCRExtractor(use_gpu=self.use_gpu)
            logger.info("✅ PaddleOCR初始化完成")
        
        return self.ocr_extractor.extract(file_path)


class PaddleOCRExtractor(TextExtractor):
    """PaddleOCR文本提取器 - PP-OCRv5"""
    
    def __init__(self, use_gpu: bool = False):
        """
        初始化PaddleOCR提取器
        
        Args:
            use_gpu: 是否使用GPU加速
        """
        if not deps.is_available('ocr') or 'paddleocr' not in deps.available_modules['ocr']:
            raise RuntimeError("PaddleOCR不可用，请安装 paddleocr")
        
        try:
            from paddleocr import PaddleOCR
            import os
            
            # 设置环境变量以减少警告和优化内存
            os.environ.setdefault('FLAGS_allocator_strategy', 'auto_growth')
            
            # 初始化PaddleOCR（使用3.x正确API）
            print("🔧 初始化PaddleOCR引擎（v3.x）...")
            # 禁用一些功能以提高稳定性和速度
            self.ocr = PaddleOCR(
                use_doc_orientation_classify=False,  # 禁用文档方向分类
                use_doc_unwarping=False,             # 禁用文档矫正（减少内存）
                use_textline_orientation=False       # 禁用文本行方向检测
            )
            print("✅ PaddleOCR引擎初始化完成")
            logger.info(f"PaddleOCR初始化成功（v3.x API）")
            
        except Exception as e:
            logger.error(f"PaddleOCR初始化失败: {e}")
            logger.error("请确保已正确安装PaddleOCR: pip install paddleocr paddlepaddle")
            raise RuntimeError(f"PaddleOCR初始化失败: {e}")
    
    def extract(self, file_path: str) -> List[str]:
        """从图片或PDF提取文本"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            # 检查是否是PDF文件
            if file_ext == '.pdf':
                logger.info("检测到PDF文件，PaddleOCR将逐页处理")
                return self._extract_from_pdf(file_path)
            else:
                # 图片文件
                return self._extract_from_image(file_path)
            
        except Exception as e:
            logger.error(f"PaddleOCR提取失败: {e}")
            raise ValueError(f"OCR处理失败: {e}")
    
    def _extract_from_image(self, file_path: str) -> List[str]:
        """从图片提取文本"""
        # 执行OCR识别（PaddleOCR 3.x API）
        result = self.ocr.predict(input=file_path)
        
        # PaddleOCR 3.x 返回的是可迭代的结果对象
        if not result:
            raise ValueError("图片中未检测到文本")
        
        # 从result中提取文本（按照3.x API）
        texts = []
        try:
            # result是可迭代对象，每个res有text属性
            for res in result:
                if hasattr(res, 'text'):
                    texts.append(res.text)
                else:
                    logger.warning(f"结果对象没有text属性: {type(res)}")
            
            if texts:
                full_text = '\n'.join(texts)
            else:
                # 降级方案：尝试直接转换
                full_text = str(result)
                
        except Exception as e:
            logger.error(f"解析OCR结果失败: {e}, 结果类型: {type(result)}")
            raise ValueError(f"OCR结果解析失败: {e}")
        
        if not full_text or not full_text.strip():
            raise ValueError("图片中未检测到有效文本")
        
        logger.info(f"PaddleOCR成功提取文本，长度: {len(full_text)} 字符")
        return [f"[图片OCR - {Path(file_path).name}]\n{full_text.strip()}"]
    
    def _extract_from_pdf(self, file_path: str) -> List[str]:
        """从PDF文件提取文本（逐页OCR）"""
        try:
            import time
            logger.info(f"开始OCR处理PDF: {Path(file_path).name}")
            logger.info("这可能需要较长时间，请耐心等待...")
            
            start_time = time.time()
            
            # PaddleOCR 3.x支持直接处理PDF
            logger.info("正在调用PaddleOCR引擎...")
            try:
                result = self.ocr.predict(input=file_path)
                logger.info(f"PaddleOCR处理完成，耗时: {time.time() - start_time:.2f}秒")
            except KeyboardInterrupt:
                logger.warning("用户中断OCR处理")
                raise
            except Exception as ocr_error:
                logger.error(f"PaddleOCR处理时出错: {type(ocr_error).__name__}: {ocr_error}")
                raise RuntimeError(f"PaddleOCR处理失败: {ocr_error}")
            
            if not result:
                raise ValueError("PDF中未检测到文本")
            
            # 从result中提取文本（PaddleOCR 3.x API）
            try:
                logger.info(f"正在解析OCR结果，类型: {type(result)}")
                
                # result是可迭代对象（每页一个结果）
                all_texts = []
                for page_idx, res in enumerate(result):
                    logger.info(f"处理第{page_idx + 1}页...")
                    if hasattr(res, 'text'):
                        all_texts.append(f"[第{page_idx + 1}页]\n{res.text}")
                    else:
                        logger.warning(f"第{page_idx + 1}页结果对象没有text属性: {type(res)}")
                
                if not all_texts:
                    raise ValueError("PDF所有页面均未检测到文本")
                
                full_text = '\n\n'.join(all_texts)
                logger.info(f"成功提取{len(all_texts)}页文本")
                
            except Exception as e:
                logger.error(f"解析PDF OCR结果失败: {e}, 结果类型: {type(result)}")
                raise ValueError(f"PDF OCR结果解析失败: {e}")
            
            if not full_text or not full_text.strip():
                raise ValueError("PDF中未检测到有效文本")
            
            total_time = time.time() - start_time
            logger.info(f"PaddleOCR成功处理PDF，提取{len(full_text)}字符，总耗时: {total_time:.2f}秒")
            return [f"[扫描版PDF - {Path(file_path).name}]\n{full_text}"]
            
        except Exception as e:
            logger.error(f"PaddleOCR处理PDF失败: {e}")
            logger.error(f"错误详情: {type(e).__name__}: {str(e)}")
            logger.error(f"建议: 对于大型扫描版PDF，可以先用专门工具转换为文本文件")
            raise


# =============================================================================
# 主文件处理器
# =============================================================================

class FileProcessor:
    """统一文件处理器"""
    
    def __init__(self, use_gpu: bool = False):
        """
        初始化文件处理器
        
        Args:
            use_gpu: 是否使用GPU加速OCR（PaddleOCR支持）
        """
        self.use_gpu = use_gpu
        self.extractors = self._init_extractors()
    
    def _init_extractors(self) -> Dict[str, TextExtractor]:
        """初始化提取器"""
        extractors = {
            'text': PlainTextExtractor(),
        }
        
        # PDF提取器（支持懒加载OCR）
        if deps.is_available('pdf'):
            enable_ocr = deps.is_available('ocr')
            logger.info(f"📄 初始化PDF提取器: OCR={'启用' if enable_ocr else '禁用'}, GPU={'启用' if self.use_gpu else '禁用'}")
            extractors['pdf'] = PDFExtractor(enable_ocr=enable_ocr, use_gpu=self.use_gpu)
            if enable_ocr:
                logger.info("✅ PDF提取器已启用OCR降级功能（懒加载模式）")
            else:
                logger.warning("⚠️  PDF提取器OCR功能未启用（PaddleOCR未安装）")
        
        # 图片OCR提取器（懒加载，只在直接处理图片时初始化）
        # 这里不立即初始化，而是在ImageExtractorWrapper中懒加载
        if deps.is_available('ocr'):
            extractors['image'] = ImageExtractorWrapper(use_gpu=self.use_gpu)
        
        if deps.is_available('docx'):
            extractors['docx'] = DOCXExtractor()
            extractors['doc'] = DOCXExtractor()  # 使用相同的提取器
        
        return extractors
    
    def process_file(self, file_path: str) -> Tuple[str, List[str]]:
        """
        处理文件并提取文本
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[str, List[str]]: (文件类型, 提取的文本列表)
        """
        try:
            # 检测文件类型
            file_type, mime_type = FileTypeDetector.detect_file_type(file_path)
            logger.info(f"检测到文件类型: {file_type} ({mime_type})")
            
            # 获取对应的提取器
            extractor = self.extractors.get(file_type)
            if not extractor:
                raise ValueError(f"不支持的文件类型: {file_type}")
            
            # 提取文本
            texts = extractor.extract(file_path)
            
            # 验证结果
            if not texts or not any(text.strip() for text in texts):
                raise ValueError("文件中未提取到有效文本")
            
            logger.info(f"成功处理文件 {Path(file_path).name}: {len(texts)} 个文本块")
            return file_type, texts
            
        except Exception as e:
            logger.error(f"文件处理失败 {file_path}: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式列表"""
        formats = ['txt', 'md', 'html', 'xml']  # 基础文本格式
        
        if 'pdf' in self.extractors:
            formats.append('pdf')
        
        if 'docx' in self.extractors:
            formats.extend(['docx', 'doc'])
        
        if 'image' in self.extractors:
            formats.extend(['jpg', 'jpeg', 'png', 'tiff', 'bmp', 'gif'])
        
        return formats
    
    def get_processor_info(self) -> Dict[str, Any]:
        """获取处理器信息"""
        return {
            "supported_formats": self.get_supported_formats(),
            "available_extractors": list(self.extractors.keys()),
            "dependencies": deps.available_modules,
            "ocr_enabled": 'image' in self.extractors,
        }
    
    # =============================================================================
    # 便捷方法（保持向后兼容）
    # =============================================================================
    
    def extract_text_file(self, file_path: str) -> List[str]:
        """提取文本文件（向后兼容）"""
        file_type, texts = self.process_file(file_path)
        return texts
    
    def extract_pdf_text(self, file_path: str) -> List[str]:
        """提取PDF文本（向后兼容）"""
        if 'pdf' not in self.extractors:
            raise RuntimeError("PDF处理器不可用")
        return self.extractors['pdf'].extract(file_path)
    
    def extract_docx_text(self, file_path: str) -> List[str]:
        """提取DOCX文本（向后兼容）"""
        if 'docx' not in self.extractors:
            raise RuntimeError("DOCX处理器不可用")
        return self.extractors['docx'].extract(file_path)
    
    def extract_image_text(self, file_path: str) -> List[str]:
        """提取图片文本（向后兼容）"""
        if 'image' not in self.extractors:
            raise RuntimeError("OCR处理器不可用")
        return self.extractors['image'].extract(file_path)


# =============================================================================
# 工具函数
# =============================================================================

def create_file_processor(tesseract_path: Optional[str] = None) -> FileProcessor:
    """
    创建文件处理器实例
    
    Args:
        tesseract_path: Tesseract路径
        
    Returns:
        FileProcessor: 文件处理器实例
    """
    return FileProcessor(tesseract_path)


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        Dict: 文件信息
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    file_type, mime_type = FileTypeDetector.detect_file_type(file_path)
    
    return {
        "name": path.name,
        "size": path.stat().st_size,
        "extension": path.suffix,
        "type": file_type,
        "mime_type": mime_type,
        "is_supported": file_type in ['text', 'pdf', 'docx', 'doc', 'image'],
    }


if __name__ == "__main__":
    # 简单测试
    processor = create_file_processor()
    info = processor.get_processor_info()
    
    print("文件处理器信息:")
    print(f"支持格式: {info['supported_formats']}")
    print(f"可用提取器: {info['available_extractors']}")
    print(f"OCR功能: {'启用' if info['ocr_enabled'] else '禁用'}")