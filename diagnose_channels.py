#!/usr/bin/env python3
"""
频道诊断工具
"""

import asyncio
import json
from telethon import TelegramClient

async def diagnose_channels():
    print("=== 频道诊断工具 ===\n")
    
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if config['api_id'] == "YOUR_API_ID":
        print("❌ 请先配置API信息")
        return
    
    # 初始化客户端
    client = TelegramClient('diagnose_session', int(config['api_id']), config['api_hash'])
    await client.start(phone=config['phone'])
    
    print("✅ 客户端连接成功\n")
    
    # 列出所有对话
    print("📋 你的所有对话列表:")
    print("-" * 80)
    
    channels = []
    groups = []
    
    async for dialog in client.iter_dialogs():
        if hasattr(dialog.entity, 'broadcast') and dialog.entity.broadcast:
            channels.append(dialog)
            print(f"📺 频道: {dialog.name} (ID: {dialog.id})")
        elif dialog.is_group:
            groups.append(dialog)
            print(f"👥 群组: {dialog.name} (ID: {dialog.id})")
    
    print(f"\n统计: {len(channels)} 个频道, {len(groups)} 个群组")
    print("-" * 80)
    
    # 检查配置中的频道
    print("\n🔍 检查配置中的频道:")
    for chat_id_str, name in config['source_chats'].items():
        chat_id = int(chat_id_str.strip())
        print(f"\n检查: {name} ({chat_id})")
        
        # 在对话列表中查找
        found_dialog = None
        for dialog in channels + groups:
            if dialog.id == chat_id:
                found_dialog = dialog
                break
        
        if found_dialog:
            entity_type = "频道" if hasattr(found_dialog.entity, 'broadcast') and found_dialog.entity.broadcast else "群组"
            print(f"✅ 在对话列表中找到: {found_dialog.name} ({entity_type})")
            
            # 测试消息读取
            try:
                message_count = 0
                async for message in client.iter_messages(chat_id, limit=3):
                    message_count += 1
                    if message.text:
                        preview = message.text[:50] + "..." if len(message.text) > 50 else message.text
                        print(f"   📝 消息预览: {preview}")
                
                print(f"   ✅ 成功读取 {message_count} 条消息")
                
            except Exception as msg_error:
                print(f"   ❌ 读取消息失败: {msg_error}")
        else:
            print(f"❌ 未在对话列表中找到")
            print("   可能需要:")
            print("   1. 加入该频道")
            print("   2. 检查频道ID是否正确")
            print("   3. 确认频道仍然存在")
    
    # 建议
    print(f"\n💡 建议:")
    print("1. 如果频道不在对话列表中，请先加入频道")
    print("2. 私有频道需要邀请链接或管理员添加")
    print("3. 确认频道ID格式正确 (负数，以-100开头)")
    print("4. 可以使用上面列出的频道ID替换配置文件中的ID")
    
    await client.disconnect()
    print("\n诊断完成!")

if __name__ == "__main__":
    asyncio.run(diagnose_channels())