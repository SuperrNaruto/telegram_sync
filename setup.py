#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置脚本 - 帮助获取必要的配置信息
"""

import json
import asyncio
import sys
import locale
from telethon import TelegramClient

# 设置编码
if sys.platform.startswith('linux'):
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')

async def get_chat_info():
    """获取群组/频道信息"""
    print("=== Telegram消息同步工具设置 ===\n")
    
    # 获取API凭据
    api_id = input("请输入你的API ID: ")
    api_hash = input("请输入你的API Hash: ")
    phone = input("请输入你的手机号 (包含国家代码，如+86): ")
    
    # 创建客户端
    client = TelegramClient('setup_session', int(api_id), api_hash)
    await client.start(phone=phone)
    
    print("\n正在获取你的对话列表...")
    
    # 获取对话列表
    dialogs = await client.get_dialogs()
    
    print("\n可用的群组和频道:")
    print("-" * 50)
    
    channels = []
    groups = []
    
    for dialog in dialogs:
        if dialog.is_channel:
            channels.append(dialog)
            print(f"频道: {dialog.name} (ID: {dialog.id})")
        elif dialog.is_group:
            groups.append(dialog)
            print(f"群组: {dialog.name} (ID: {dialog.id})")
    
    print("\n" + "=" * 50)
    
    # 选择目标频道
    print("\n请选择目标频道 (消息将同步到这里):")
    target_channel = input("输入目标频道的用户名 (如 @mychannel) 或 ID: ")
    
    # 选择源群组/频道
    print("\n请选择要同步的源 (可以多个，用逗号分隔):")
    try:
        source_input = input("输入源的用户名或ID: ")
    except UnicodeDecodeError:
        print("输入编码错误，请重新输入:")
        source_input = sys.stdin.buffer.read().decode('utf-8').strip()
    
    # 历史消息同步设置
    print("\n历史消息同步设置:")
    sync_history = input("是否启用历史消息同步? (y/n, 默认y): ").strip().lower()
    sync_history = sync_history != 'n'
    
    history_limit = 100
    history_days = 7
    
    if sync_history:
        limit_input = input("历史消息数量限制 (默认100): ").strip()
        if limit_input:
            try:
                history_limit = int(limit_input)
            except ValueError:
                pass
        
        days_input = input("同步几天内的历史消息 (默认7): ").strip()
        if days_input:
            try:
                history_days = int(days_input)
            except ValueError:
                pass
    
    # 构建配置
    config = {
        "api_id": int(api_id),
        "api_hash": api_hash,
        "phone": phone,
        "target_channel": target_channel,
        "source_chats": {},
        "add_source_info": True,
        "history_sync": {
            "enabled": sync_history,
            "limit": history_limit,
            "days_back": history_days
        },
        "filters": {
            "keywords": [],
            "exclude_keywords": [],
            "media_only": False,
            "text_only": False
        }
    }
    
    # 处理源列表
    sources = [s.strip() for s in source_input.split(',')]
    for source in sources:
        try:
            if source.startswith('@'):
                entity = await client.get_entity(source)
                config["source_chats"][entity.id] = entity.title or entity.first_name
            else:
                entity = await client.get_entity(int(source))
                config["source_chats"][int(source)] = entity.title or entity.first_name
        except Exception as e:
            print(f"无法获取 {source} 的信息: {e}")
    
    # 保存配置
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n配置已保存到 config.json")
    print("\n使用方法:")
    print("1. python telegram_sync.py - 同步历史消息后开始实时监听")
    print("2. python history_sync.py - 只同步历史消息")
    
    if sync_history:
        print(f"\n历史消息同步设置:")
        print(f"- 数量限制: {history_limit} 条")
        print(f"- 时间范围: {history_days} 天内")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(get_chat_info())