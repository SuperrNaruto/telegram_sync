#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件检查工具
"""

import json
import os
import sys

def check_config():
    """检查配置文件"""
    config_file = 'config.json'
    
    print("=== 配置文件检查工具 ===\n")
    
    # 检查文件是否存在
    if not os.path.exists(config_file):
        print(f"❌ 配置文件 {config_file} 不存在")
        print("请运行 python quick_setup.py 创建配置文件")
        return False
    
    print(f"✅ 配置文件 {config_file} 存在")
    
    # 检查文件大小
    file_size = os.path.getsize(config_file)
    print(f"📁 文件大小: {file_size} 字节")
    
    # 检查文件编码
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print("✅ UTF-8 编码读取成功")
    except UnicodeDecodeError as e:
        print(f"❌ UTF-8 编码读取失败: {e}")
        return False
    
    # 检查JSON格式
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ JSON 格式正确")
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误: {e}")
        print(f"错误位置: 第 {e.lineno} 行, 第 {e.colno} 列")
        
        # 显示错误附近的内容
        lines = content.split('\n')
        if e.lineno <= len(lines):
            print(f"错误行内容: {lines[e.lineno-1]}")
        return False
    
    # 检查必需字段
    required_fields = ['api_id', 'api_hash', 'phone', 'target_channel', 'source_chats']
    missing_fields = []
    
    for field in required_fields:
        if field not in config:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ 缺少必需字段: {', '.join(missing_fields)}")
        return False
    
    print("✅ 所有必需字段都存在")
    
    # 检查API配置
    if config['api_id'] == "YOUR_API_ID":
        print("⚠️  请填入你的实际 API ID")
    
    if config['api_hash'] == "YOUR_API_HASH":
        print("⚠️  请填入你的实际 API Hash")
    
    if config['phone'] == "YOUR_PHONE_NUMBER":
        print("⚠️  请填入你的实际手机号")
    
    # 显示配置摘要
    print(f"\n📋 配置摘要:")
    print(f"   目标频道: {config['target_channel']}")
    print(f"   源数量: {len(config['source_chats'])}")
    
    for chat_id, name in config['source_chats'].items():
        print(f"   - {name}: {chat_id}")
    
    print(f"   历史同步: {'启用' if config.get('history_sync', {}).get('enabled', False) else '禁用'}")
    
    print("\n✅ 配置文件检查完成!")
    return True

if __name__ == "__main__":
    success = check_config()
    sys.exit(0 if success else 1)