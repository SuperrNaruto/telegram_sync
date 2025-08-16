#!/usr/bin/env python3
"""
测试群组访问权限
"""

import asyncio
import json
from telethon import TelegramClient

async def test_access():
    print("=== 群组访问权限测试 ===\n")
    
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if config['api_id'] == "YOUR_API_ID":
        print("❌ 请先配置API信息")
        return
    
    # 初始化客户端
    client = TelegramClient('test_session', int(config['api_id']), config['api_hash'])
    await client.start(phone=config['phone'])
    
    print("✅ 客户端连接成功\n")
    
    # 测试目标频道
    print(f"🎯 测试目标频道: {config['target_channel']}")
    try:
        target_entity = await client.get_entity(config['target_channel'])
        print(f"✅ 目标频道访问成功: {target_entity.title}")
        
        # 测试发送权限
        try:
            await client.send_message(config['target_channel'], "🧪 访问测试消息 (可以删除)")
            print("✅ 目标频道发送权限正常")
        except Exception as send_error:
            print(f"❌ 目标频道发送失败: {send_error}")
            
    except Exception as e:
        print(f"❌ 目标频道访问失败: {e}")
    
    print()
    
    # 测试源群组
    for chat_id_str, name in config['source_chats'].items():
        chat_id = int(chat_id_str.strip())
        print(f"📡 测试源群组: {name} ({chat_id})")
        
        try:
            entity = await client.get_entity(chat_id)
            print(f"✅ 群组访问成功: {entity.title}")
            
            # 获取最近几条消息测试
            message_count = 0
            async for message in client.iter_messages(chat_id, limit=5):
                message_count += 1
            
            print(f"✅ 可以读取消息，测试获取了 {message_count} 条")
            
        except Exception as e:
            print(f"❌ 群组访问失败: {e}")
            print("   可能原因:")
            print("   - 群组ID不正确")
            print("   - 你不是群组成员")
            print("   - 群组设置了访问限制")
        
        print()
    
    await client.disconnect()
    print("测试完成!")

if __name__ == "__main__":
    asyncio.run(test_access())