#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
断点管理命令行工具
用于查看、管理和清理断点文件
"""

import argparse
import sys
from datetime import datetime
from checkpoint_manager import CheckpointManager

def list_checkpoints(manager: CheckpointManager):
    """列出所有断点"""
    checkpoints = manager.list_checkpoints()
    
    if not checkpoints:
        print("📝 没有找到断点文件")
        return
    
    print(f"📋 找到 {len(checkpoints)} 个断点:")
    print("-" * 80)
    
    for i, cp in enumerate(checkpoints, 1):
        status = "✅ 已完成" if cp.get('is_completed', False) else "🔄 未完成"
        create_time = cp.get('create_time', '')[:19]  # 显示完整时间
        update_time = cp.get('update_time', '')[:19]
        progress = cp.get('progress', '0/0')
        
        print(f"{i}. 断点ID: {cp['checkpoint_id']}")
        print(f"   状态: {status}")
        print(f"   创建时间: {create_time}")
        print(f"   更新时间: {update_time}")
        print(f"   进度: {progress}")
        print()

def show_checkpoint_details(manager: CheckpointManager, checkpoint_id: str):
    """显示断点详细信息"""
    info = manager.get_checkpoint_info(checkpoint_id)
    
    if not info:
        print(f"❌ 未找到断点: {checkpoint_id}")
        return
    
    print(f"📋 断点详细信息: {checkpoint_id}")
    print("=" * 60)
    
    print(f"创建时间: {info.get('create_time', 'N/A')}")
    print(f"更新时间: {info.get('update_time', 'N/A')}")
    print(f"总文件数: {info.get('total_files', 0)}")
    print(f"已完成: {info.get('completed_files', 0)}")
    print(f"失败数: {info.get('failed_files', 0)}")
    print(f"状态: {'已完成' if info.get('is_completed', False) else '进行中'}")
    
    # 显示处理配置
    config = info.get('processing_config', {})
    if config:
        print("\n🔧 处理配置:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    
    # 显示文件状态
    files_state = info.get('files_state', [])
    if files_state:
        print(f"\n📁 文件处理状态 ({len(files_state)} 个文件):")
        
        # 统计各状态数量
        status_counts = {}
        for file_state in files_state:
            status = file_state.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            emoji = {'pending': '⏳', 'processing': '🔄', 'completed': '✅', 'failed': '❌'}.get(status, '❓')
            print(f"  {emoji} {status}: {count} 个")

def delete_checkpoint(manager: CheckpointManager, checkpoint_id: str):
    """删除指定断点"""
    if manager.delete_checkpoint(checkpoint_id):
        print(f"✅ 已删除断点: {checkpoint_id}")
    else:
        print(f"❌ 删除断点失败: {checkpoint_id}")

def cleanup_checkpoints(manager: CheckpointManager, days: int):
    """清理过期断点"""
    print(f"🧹 清理 {days} 天前的断点文件...")
    
    # 这里需要修改CheckpointManager来支持返回清理数量
    manager._cleanup_old_checkpoints(max_age_days=days)
    print("✅ 清理完成")

def interactive_mode(manager: CheckpointManager):
    """交互模式"""
    print("🎮 进入断点管理交互模式")
    print("输入 'help' 查看可用命令")
    
    while True:
        try:
            command = input("\ncheckpoint> ").strip().lower()
            
            if command in ['exit', 'quit', 'q']:
                print("👋 退出断点管理工具")
                break
            elif command == 'help':
                print("可用命令:")
                print("  list       - 列出所有断点")
                print("  show <id>  - 显示断点详情")
                print("  delete <id> - 删除指定断点")
                print("  cleanup <days> - 清理N天前的断点")
                print("  clear      - 清屏")
                print("  exit       - 退出")
            elif command == 'list':
                list_checkpoints(manager)
            elif command.startswith('show '):
                checkpoint_id = command[5:].strip()
                if checkpoint_id:
                    show_checkpoint_details(manager, checkpoint_id)
                else:
                    print("❌ 请提供断点ID")
            elif command.startswith('delete '):
                checkpoint_id = command[7:].strip()
                if checkpoint_id:
                    confirm = input(f"确认删除断点 {checkpoint_id}? (y/N): ")
                    if confirm.lower() == 'y':
                        delete_checkpoint(manager, checkpoint_id)
                else:
                    print("❌ 请提供断点ID")
            elif command.startswith('cleanup '):
                try:
                    days = int(command[8:].strip())
                    cleanup_checkpoints(manager, days)
                except ValueError:
                    print("❌ 请提供有效的天数")
            elif command == 'clear':
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
            elif command:
                print(f"❌ 未知命令: {command}")
                print("输入 'help' 查看可用命令")
                
        except KeyboardInterrupt:
            print("\n👋 退出断点管理工具")
            break
        except Exception as e:
            print(f"❌ 执行命令时出错: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="断点管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python checkpoint_tool.py list                    # 列出所有断点
  python checkpoint_tool.py show <checkpoint_id>    # 显示断点详情
  python checkpoint_tool.py delete <checkpoint_id>  # 删除断点
  python checkpoint_tool.py cleanup --days 7        # 清理7天前的断点
  python checkpoint_tool.py interactive             # 进入交互模式
        """
    )
    
    parser.add_argument("action", 
                       choices=['list', 'show', 'delete', 'cleanup', 'interactive'],
                       help="要执行的操作")
    parser.add_argument("checkpoint_id", nargs='?', help="断点ID（适用于show和delete操作）")
    parser.add_argument("--days", type=int, default=7, help="清理多少天前的断点（默认7天）")
    parser.add_argument("--dir", default="checkpoints", help="断点文件目录（默认: checkpoints）")
    
    args = parser.parse_args()
    
    # 创建断点管理器
    try:
        manager = CheckpointManager(args.dir)
    except Exception as e:
        print(f"❌ 初始化断点管理器失败: {e}")
        sys.exit(1)
    
    # 执行操作
    try:
        if args.action == 'list':
            list_checkpoints(manager)
        
        elif args.action == 'show':
            if not args.checkpoint_id:
                print("❌ 请提供断点ID")
                sys.exit(1)
            show_checkpoint_details(manager, args.checkpoint_id)
        
        elif args.action == 'delete':
            if not args.checkpoint_id:
                print("❌ 请提供断点ID")
                sys.exit(1)
            delete_checkpoint(manager, args.checkpoint_id)
        
        elif args.action == 'cleanup':
            cleanup_checkpoints(manager, args.days)
        
        elif args.action == 'interactive':
            interactive_mode(manager)
    
    except Exception as e:
        print(f"❌ 执行操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
