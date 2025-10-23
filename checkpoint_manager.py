#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
断点续传管理器
支持批处理任务的断点保存和恢复功能
"""

import os
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# 配置日志
logger = logging.getLogger(__name__)

# =============================================================================
# 数据结构定义
# =============================================================================

@dataclass
class FileProcessingState:
    """文件处理状态"""
    file_path: str
    file_size: int
    file_hash: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None
    result_data: Optional[Dict] = None

@dataclass
class BatchProcessingCheckpoint:
    """批处理断点数据"""
    checkpoint_id: str
    session_id: str
    create_time: str
    update_time: str
    total_files: int
    completed_files: int
    failed_files: int
    processing_config: Dict[str, Any]
    files_state: List[FileProcessingState]
    current_file_index: int
    output_directory: str
    is_completed: bool = False


# =============================================================================
# 断点管理器
# =============================================================================

class CheckpointManager:
    """断点续传管理器"""
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        """
        初始化断点管理器
        
        Args:
            checkpoint_dir: 断点文件存储目录
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.current_checkpoint: Optional[BatchProcessingCheckpoint] = None
        
        # 清理过期的断点文件
        self._cleanup_old_checkpoints()
    
    # =============================================================================
    # 断点创建和保存
    # =============================================================================
    
    def create_checkpoint(self, 
                         files: List[str],
                         processing_config: Dict[str, Any],
                         output_directory: str,
                         session_id: Optional[str] = None) -> str:
        """
        创建新的断点
        
        Args:
            files: 要处理的文件列表
            processing_config: 处理配置
            output_directory: 输出目录
            session_id: 会话ID
            
        Returns:
            str: 断点ID
        """
        # 生成唯一的断点ID
        checkpoint_id = self._generate_checkpoint_id(files, processing_config)
        
        if not session_id:
            session_id = self._generate_session_id()
        
        # 创建文件状态列表
        files_state = []
        for file_path in files:
            try:
                file_size = os.path.getsize(file_path)
                file_hash = self._calculate_file_hash(file_path)
                
                state = FileProcessingState(
                    file_path=file_path,
                    file_size=file_size,
                    file_hash=file_hash,
                    status='pending'
                )
                files_state.append(state)
                
            except Exception as e:
                logger.warning(f"无法获取文件信息 {file_path}: {e}")
                state = FileProcessingState(
                    file_path=file_path,
                    file_size=0,
                    file_hash="",
                    status='failed',
                    error_message=str(e)
                )
                files_state.append(state)
        
        # 创建断点对象
        checkpoint = BatchProcessingCheckpoint(
            checkpoint_id=checkpoint_id,
            session_id=session_id,
            create_time=datetime.now().isoformat(),
            update_time=datetime.now().isoformat(),
            total_files=len(files),
            completed_files=0,
            failed_files=0,
            processing_config=processing_config,
            files_state=files_state,
            current_file_index=0,
            output_directory=output_directory
        )
        
        self.current_checkpoint = checkpoint
        self._save_checkpoint()
        
        logger.info(f"创建断点: {checkpoint_id}, 文件数: {len(files)}")
        return checkpoint_id
    
    def save_checkpoint(self):
        """保存当前断点"""
        if self.current_checkpoint:
            self.current_checkpoint.update_time = datetime.now().isoformat()
            self._save_checkpoint()
    
    def _save_checkpoint(self):
        """内部保存断点方法"""
        if not self.current_checkpoint:
            return
        
        checkpoint_file = self.checkpoint_dir / f"{self.current_checkpoint.checkpoint_id}.json"
        
        try:
            # 转换为字典格式
            checkpoint_data = asdict(self.current_checkpoint)
            
            # 保存到文件
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"断点已保存: {checkpoint_file}")
            
        except Exception as e:
            logger.error(f"保存断点失败: {e}")
    
    # =============================================================================
    # 断点加载和恢复
    # =============================================================================
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """列出所有可用的断点"""
        checkpoints = []
        
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
                
                # 提取关键信息
                info = {
                    "checkpoint_id": checkpoint_data["checkpoint_id"],
                    "create_time": checkpoint_data["create_time"],
                    "update_time": checkpoint_data["update_time"],
                    "total_files": checkpoint_data["total_files"],
                    "completed_files": checkpoint_data["completed_files"],
                    "failed_files": checkpoint_data["failed_files"],
                    "is_completed": checkpoint_data.get("is_completed", False),
                    "progress": f"{checkpoint_data['completed_files']}/{checkpoint_data['total_files']}"
                }
                
                checkpoints.append(info)
                
            except Exception as e:
                logger.warning(f"读取断点文件失败 {checkpoint_file}: {e}")
        
        # 按更新时间排序
        checkpoints.sort(key=lambda x: x["update_time"], reverse=True)
        return checkpoints
    
    def load_checkpoint(self, checkpoint_id: str) -> bool:
        """
        加载指定的断点
        
        Args:
            checkpoint_id: 断点ID
            
        Returns:
            bool: 是否成功加载
        """
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            logger.error(f"断点文件不存在: {checkpoint_file}")
            return False
        
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            # 重建文件状态对象
            files_state = []
            for file_data in checkpoint_data["files_state"]:
                state = FileProcessingState(**file_data)
                files_state.append(state)
            
            # 重建断点对象
            checkpoint_data["files_state"] = files_state
            self.current_checkpoint = BatchProcessingCheckpoint(**checkpoint_data)
            
            logger.info(f"断点加载成功: {checkpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"加载断点失败 {checkpoint_id}: {e}")
            return False
    
    # =============================================================================
    # 状态更新
    # =============================================================================
    
    def update_file_status(self, 
                          file_path: str, 
                          status: str,
                          result_data: Optional[Dict] = None,
                          error_message: Optional[str] = None):
        """
        更新文件处理状态
        
        Args:
            file_path: 文件路径
            status: 新状态
            result_data: 结果数据
            error_message: 错误信息
        """
        if not self.current_checkpoint:
            return
        
        # 查找文件状态
        for state in self.current_checkpoint.files_state:
            if state.file_path == file_path:
                old_status = state.status
                state.status = status
                
                if status == 'processing':
                    state.start_time = datetime.now().isoformat()
                elif status in ['completed', 'failed']:
                    state.end_time = datetime.now().isoformat()
                    
                    if status == 'completed':
                        state.result_data = result_data
                        # 更新完成计数
                        if old_status != 'completed':
                            self.current_checkpoint.completed_files += 1
                    elif status == 'failed':
                        state.error_message = error_message
                        # 更新失败计数
                        if old_status != 'failed':
                            self.current_checkpoint.failed_files += 1
                
                break
        
        # 检查是否全部完成
        if (self.current_checkpoint.completed_files + self.current_checkpoint.failed_files 
            >= self.current_checkpoint.total_files):
            self.current_checkpoint.is_completed = True
        
        # 自动保存
        self.save_checkpoint()
    
    def get_next_pending_file(self) -> Optional[str]:
        """获取下一个待处理的文件"""
        if not self.current_checkpoint:
            return None
        
        for state in self.current_checkpoint.files_state:
            if state.status == 'pending':
                return state.file_path
        
        return None
    
    def get_processing_progress(self) -> Dict[str, Any]:
        """获取处理进度信息"""
        if not self.current_checkpoint:
            return {}
        
        total = self.current_checkpoint.total_files
        completed = self.current_checkpoint.completed_files
        failed = self.current_checkpoint.failed_files
        pending = total - completed - failed
        
        return {
            "total_files": total,
            "completed_files": completed,
            "failed_files": failed,
            "pending_files": pending,
            "progress_percentage": (completed / total * 100) if total > 0 else 0,
            "is_completed": self.current_checkpoint.is_completed
        }
    
    # =============================================================================
    # 工具方法
    # =============================================================================
    
    def _generate_checkpoint_id(self, files: List[str], config: Dict[str, Any]) -> str:
        """生成唯一的断点ID"""
        # 基于文件列表和配置生成哈希
        content = f"{sorted(files)}{config}".encode('utf-8')
        hash_obj = hashlib.md5(content)
        timestamp = int(time.time())
        return f"checkpoint_{timestamp}_{hash_obj.hexdigest()[:8]}"
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        timestamp = int(time.time())
        return f"session_{timestamp}"
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值（用于验证文件完整性）"""
        try:
            hash_obj = hashlib.md5()
            with open(file_path, 'rb') as f:
                # 只读取文件的前1KB来生成哈希（提高性能）
                chunk = f.read(1024)
                hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception:
            return ""
    
    def _cleanup_old_checkpoints(self, max_age_days: int = 7, auto_clean_completed: bool = True):
        """
        清理过期的断点文件
        
        Args:
            max_age_days: 最大保留天数
            auto_clean_completed: 是否自动清理已完成的checkpoint
        """
        try:
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 3600
            
            for checkpoint_file in self.checkpoint_dir.glob("*.json"):
                try:
                    # 读取checkpoint检查是否完成
                    if auto_clean_completed:
                        with open(checkpoint_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # 自动删除已完成的checkpoint
                            if data.get('is_completed', False):
                                checkpoint_file.unlink()
                                logger.info(f"删除已完成的断点文件: {checkpoint_file.name}")
                                continue
                    
                    # 删除过期的checkpoint
                    file_age = current_time - checkpoint_file.stat().st_mtime
                    if file_age > max_age_seconds:
                        checkpoint_file.unlink()
                        logger.info(f"删除过期断点文件: {checkpoint_file.name}")
                        
                except Exception as e:
                    logger.warning(f"处理checkpoint文件 {checkpoint_file.name} 失败: {e}")
                    
        except Exception as e:
            logger.warning(f"清理断点文件失败: {e}")
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """删除指定的断点文件"""
        try:
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                logger.info(f"删除断点文件: {checkpoint_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除断点文件失败 {checkpoint_id}: {e}")
            return False
    
    def get_checkpoint_info(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """获取断点详细信息"""
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取断点信息失败 {checkpoint_id}: {e}")
            return None


# =============================================================================
# 便捷函数
# =============================================================================

def create_checkpoint_manager(checkpoint_dir: str = "checkpoints") -> CheckpointManager:
    """创建断点管理器实例"""
    return CheckpointManager(checkpoint_dir)


if __name__ == "__main__":
    # 简单测试
    manager = create_checkpoint_manager()
    
    # 模拟创建断点
    test_files = ["test1.pdf", "test2.docx"]
    test_config = {"model": "gpt-4o", "chunk_size": 12000}
    
    checkpoint_id = manager.create_checkpoint(
        files=test_files,
        processing_config=test_config,
        output_directory="test_output"
    )
    
    print(f"创建断点: {checkpoint_id}")
    
    # 列出断点
    checkpoints = manager.list_checkpoints()
    print(f"可用断点: {len(checkpoints)}")
    
    # 更新状态
    manager.update_file_status("test1.pdf", "completed", {"terms": 10})
    
    # 获取进度
    progress = manager.get_processing_progress()
    print(f"处理进度: {progress}")
