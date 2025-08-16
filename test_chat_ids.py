#!/usr/bin/env python3
"""
测试chat ID处理
"""

import json
from telegram_sync import TelegramSyncer

def test_chat_ids():
    print("=== Chat ID 处理测试 ===\n")
    
    # 加载配置
    syncer = TelegramSyncer()
    if not syncer.config:
        print("❌ 无法加载配置")
        return
    
    print("✅ 配置加载成功")
    print(f"目标频道: {syncer.config['target_channel']}")
    print(f"源群组数量: {len(syncer.config['source_chats'])}")
    
    print("\n📋 源群组列表:")
    for chat_id, name in syncer.config['source_chats'].items():
        print(f"  {name}: {chat_id} (类型: {type(chat_id)})")
        
        # 检查chat_id格式
        if isinstance(chat_id, int):
            print(f"    ✅ 整数格式正确")
        else:
            print(f"    ❌ 不是整数格式: {type(chat_id)}")
    
    print("\n🔍 原始配置文件内容:")
    with open('config.json', 'r', encoding='utf-8') as f:
        raw_config = json.load(f)
    
    for chat_id, name in raw_config['source_chats'].items():
        print(f"  原始: '{chat_id}' -> 处理后: {syncer.config['source_chats'].get(int(chat_id.strip()), 'NOT_FOUND')}")

if __name__ == "__main__":
    test_chat_ids()