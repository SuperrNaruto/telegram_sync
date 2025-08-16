#!/usr/bin/env python3
"""
历史消息同步工具 - 单独运行历史消息同步
"""

import asyncio
import json
from telegram_sync import TelegramSyncer
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    print("=== Telegram历史消息同步工具 ===\n")
    
    # 加载配置
    syncer = TelegramSyncer()
    if not syncer.config:
        logger.error("无法加载配置文件")
        return
    
    await syncer.initialize_client()
    
    print("可用的同步源:")
    for chat_id, name in syncer.config['source_chats'].items():
        print(f"  {name} (ID: {chat_id})")
    
    print(f"\n目标频道: {syncer.config['target_channel']}")
    
    # 选择同步选项
    print("\n同步选项:")
    print("1. 同步所有源的历史消息")
    print("2. 同步指定源的历史消息")
    print("3. 自定义同步参数")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        # 同步所有源
        await syncer.sync_all_history()
        
    elif choice == "2":
        # 选择特定源
        print("\n请选择要同步的源:")
        sources = list(syncer.config['source_chats'].items())
        for i, (chat_id, name) in enumerate(sources, 1):
            print(f"{i}. {name}")
        
        try:
            source_idx = int(input("输入序号: ")) - 1
            if 0 <= source_idx < len(sources):
                chat_id, name = sources[source_idx]
                
                # 获取同步参数
                limit = input("消息数量限制 (默认100): ").strip()
                limit = int(limit) if limit else 100
                
                days_back = input("同步几天内的消息 (默认7): ").strip()
                days_back = int(days_back) if days_back else 7
                
                await syncer.sync_history(chat_id, limit, days_back)
            else:
                print("无效的选择")
        except ValueError:
            print("输入无效")
            
    elif choice == "3":
        # 自定义参数
        try:
            limit = input("消息数量限制 (默认100): ").strip()
            limit = int(limit) if limit else 100
            
            days_back = input("同步几天内的消息 (默认7): ").strip()
            days_back = int(days_back) if days_back else 7
            
            # 更新配置
            syncer.config['history_sync'] = {
                'enabled': True,
                'limit': limit,
                'days_back': days_back
            }
            
            await syncer.sync_all_history()
            
        except ValueError:
            print("输入无效")
    
    else:
        print("无效的选择")
    
    await syncer.client.disconnect()
    print("\n历史消息同步完成!")

if __name__ == "__main__":
    asyncio.run(main())