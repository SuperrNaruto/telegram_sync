#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速配置脚本 - 避免编码问题
"""

import json
import sys

def create_config():
    """创建配置文件"""
    print("=== Telegram消息同步工具快速配置 ===\n")
    
    # 基本配置
    config = {
        "api_id": "",
        "api_hash": "",
        "phone": "",
        "target_channel": "",
        "source_chats": {},
        "add_source_info": True,
        "history_sync": {
            "enabled": True,
            "limit": 100,
            "days_back": 7
        },
        "filters": {
            "keywords": [],
            "exclude_keywords": [],
            "media_only": False,
            "text_only": False
        }
    }
    
    print("请按提示输入配置信息:")
    print("(如果遇到输入问题，请直接编辑生成的config.json文件)")
    print()
    
    try:
        # API配置
        config["api_id"] = input("API ID: ").strip()
        config["api_hash"] = input("API Hash: ").strip()
        config["phone"] = input("手机号 (如 +8613800138000): ").strip()
        
        # 目标频道
        config["target_channel"] = input("目标频道 (如 @mychannel 或 -1002557556585): ").strip()
        
        # 源配置
        print("\n源群组/频道配置:")
        print("请输入源ID和名称，格式: ID,名称")
        print("例如: -1002406053912,源群组1")
        print("多个源请分行输入，输入空行结束:")
        
        while True:
            source_line = input("源 (ID,名称): ").strip()
            if not source_line:
                break
            
            try:
                source_id, source_name = source_line.split(',', 1)
                config["source_chats"][int(source_id.strip())] = source_name.strip()
                print(f"已添加: {source_name.strip()} ({source_id.strip()})")
            except ValueError:
                print("格式错误，请使用: ID,名称")
        
        # 历史同步配置
        print("\n历史消息同步配置:")
        history_enabled = input("启用历史消息同步? (y/n, 默认y): ").strip().lower()
        config["history_sync"]["enabled"] = history_enabled != 'n'
        
        if config["history_sync"]["enabled"]:
            limit = input("消息数量限制 (默认100): ").strip()
            if limit:
                config["history_sync"]["limit"] = int(limit)
            
            days = input("同步天数 (默认7): ").strip()
            if days:
                config["history_sync"]["days_back"] = int(days)
        
    except KeyboardInterrupt:
        print("\n配置已取消")
        return
    except Exception as e:
        print(f"\n输入错误: {e}")
        print("请直接编辑config.json文件")
    
    # 保存配置
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n配置已保存到 config.json")
    print("\n使用方法:")
    print("1. python telegram_sync.py - 完整同步")
    print("2. python history_sync.py - 仅历史同步")
    
    # 显示配置摘要
    print(f"\n配置摘要:")
    print(f"- 目标频道: {config['target_channel']}")
    print(f"- 源数量: {len(config['source_chats'])}")
    print(f"- 历史同步: {'启用' if config['history_sync']['enabled'] else '禁用'}")

def create_config_from_args():
    """从命令行参数创建配置"""
    if len(sys.argv) < 5:
        print("用法: python quick_setup.py <api_id> <api_hash> <phone> <target_channel> [source_ids...]")
        print("例如: python quick_setup.py 12345 abcdef +8613800138000 @mychannel -1001234567890 -1001234567891")
        return
    
    api_id = sys.argv[1]
    api_hash = sys.argv[2]
    phone = sys.argv[3]
    target_channel = sys.argv[4]
    source_ids = sys.argv[5:] if len(sys.argv) > 5 else []
    
    config = {
        "api_id": int(api_id),
        "api_hash": api_hash,
        "phone": phone,
        "target_channel": target_channel,
        "source_chats": {},
        "add_source_info": True,
        "history_sync": {
            "enabled": True,
            "limit": 100,
            "days_back": 7
        },
        "filters": {
            "keywords": [],
            "exclude_keywords": [],
            "media_only": False,
            "text_only": False
        }
    }
    
    # 添加源
    for i, source_id in enumerate(source_ids):
        config["source_chats"][int(source_id)] = f"源{i+1}"
    
    # 保存配置
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("配置已创建成功!")
    print(f"目标频道: {target_channel}")
    print(f"源数量: {len(source_ids)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_config_from_args()
    else:
        create_config()