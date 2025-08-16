#!/usr/bin/env python3
"""
简单配置测试
"""

import json

def test_config():
    print("=== 配置文件测试 ===\n")
    
    # 读取原始配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("原始配置中的source_chats:")
    for chat_id, name in config['source_chats'].items():
        print(f"  '{chat_id}' ({type(chat_id).__name__}) -> {name}")
    
    # 模拟程序处理
    source_chats = {}
    for chat_id, name in config['source_chats'].items():
        clean_chat_id = str(chat_id).strip()
        int_chat_id = int(clean_chat_id)
        source_chats[int_chat_id] = name
        print(f"  处理: '{chat_id}' -> {int_chat_id} ({type(int_chat_id).__name__})")
    
    print(f"\n处理后的source_chats:")
    for chat_id, name in source_chats.items():
        print(f"  {chat_id} ({type(chat_id).__name__}) -> {name}")

if __name__ == "__main__":
    test_config()