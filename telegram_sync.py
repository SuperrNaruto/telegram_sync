#!/usr/bin/env python3
"""
Telegram消息同步工具
将源群组/频道的消息同步到目标频道
"""

import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import json
import os
from datetime import datetime, timedelta
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramSyncer:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.client = None
        self.message_mapping = {}  # 用于映射原消息ID到新消息ID
        
    def load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 转换source_chats的键为整数
            if 'source_chats' in config:
                source_chats = {}
                for chat_id, name in config['source_chats'].items():
                    # 清理chat_id，去除空格并转换为整数
                    clean_chat_id = str(chat_id).strip()
                    source_chats[int(clean_chat_id)] = name
                config['source_chats'] = source_chats
                
            return config
        except FileNotFoundError:
            logger.error(f"配置文件 {config_file} 不存在")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            return None
    
    async def initialize_client(self):
        """初始化Telegram客户端"""
        api_id = self.config['api_id']
        api_hash = self.config['api_hash']
        phone = self.config['phone']
        
        self.client = TelegramClient('session', api_id, api_hash)
        await self.client.start(phone=phone)
        logger.info("Telegram客户端初始化成功")
    
    async def sync_single_message(self, message, source_chat_id, target_channel, add_timestamp=False):
        """同步单条消息到目标频道"""
        try:
            # 检查是否是需要同步的源
            if source_chat_id not in self.config['source_chats']:
                return False
            
            source_name = self.config['source_chats'][source_chat_id]
            
            # 应用过滤器
            if not self.should_sync_message(message):
                return False
            
            # 转换目标频道ID为整数（如果是字符串格式）
            if isinstance(target_channel, str) and target_channel.startswith('-'):
                target_id = int(target_channel)
            else:
                target_id = target_channel
            
            # 构建消息内容
            content = ""
            
            if message.text:
                content = message.text
            
            # 处理回复消息
            reply_to_msg_id = None
            if message.reply_to and hasattr(message.reply_to, 'reply_to_msg_id'):
                original_reply_id = message.reply_to.reply_to_msg_id
                # 查找映射的消息ID
                reply_to_msg_id = self.message_mapping.get(original_reply_id)
                if reply_to_msg_id:
                    logger.info(f"找到回复目标: 原消息ID {original_reply_id} -> 新消息ID {reply_to_msg_id}")
                else:
                    logger.warning(f"未找到回复目标消息ID {original_reply_id}，将作为普通消息发送")
            
            # 添加来源和时间信息
            footer = []
            if self.config.get('add_source_info', True):
                footer.append(f"📢 来源: {source_name}")
            if add_timestamp and message.date:
                footer.append(f"🕐 时间: {message.date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if footer:
                content += f"\n\n{' | '.join(footer)}"
            
            # 发送消息 - 优先处理所有类型的文件
            sent_message = None
            
            # 检查是否有任何类型的媒体文件
            has_file = False
            file_to_send = None
            
            # 按优先级检查文件类型
            if message.document:
                file_to_send = message.document
                has_file = True
                logger.info(f"检测到文档: {message.document.mime_type if message.document.mime_type else 'unknown'}")
            elif message.photo:
                file_to_send = message.photo
                has_file = True
                logger.info("检测到图片")
            elif message.video:
                file_to_send = message.video
                has_file = True
                logger.info("检测到视频")
            elif message.audio:
                file_to_send = message.audio
                has_file = True
                logger.info("检测到音频")
            elif message.voice:
                file_to_send = message.voice
                has_file = True
                logger.info("检测到语音")
            elif message.video_note:
                file_to_send = message.video_note
                has_file = True
                logger.info("检测到视频消息")
            elif message.sticker:
                file_to_send = message.sticker
                has_file = True
                logger.info("检测到贴纸")
            elif message.animation:
                file_to_send = message.animation
                has_file = True
                logger.info("检测到动画/GIF")
            elif message.media:
                file_to_send = message.media
                has_file = True
                logger.info(f"检测到其他媒体: {type(message.media)}")
            
            # 发送文件或文本
            if has_file and file_to_send:
                try:
                    sent_message = await self.client.send_file(
                        target_id,
                        file_to_send,
                        caption=content if content else None,
                        reply_to=reply_to_msg_id
                    )
                    logger.info("✅ 文件发送成功")
                except Exception as file_error:
                    logger.error(f"❌ 文件发送失败: {file_error}")
                    # 如果文件发送失败，尝试只发送文本
                    if content:
                        sent_message = await self.client.send_message(
                            target_id,
                            content,
                            reply_to=reply_to_msg_id
                        )
                        logger.info("✅ 文本发送成功（文件发送失败后的备选）")
            elif content:
                # 发送纯文本
                sent_message = await self.client.send_message(
                    target_id,
                    content,
                    reply_to=reply_to_msg_id
                )
                logger.info("✅ 文本消息发送成功")
            else:
                logger.warning("❌ 消息既没有文件也没有文本内容")
                return False
            
            # 保存消息ID映射，用于后续回复
            if sent_message:
                new_msg_id = sent_message.id if hasattr(sent_message, 'id') else sent_message
                self.message_mapping[message.id] = new_msg_id
                logger.info(f"保存消息映射: 原ID {message.id} -> 新ID {new_msg_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"同步消息时出错: {e}")
            return False
    
    def should_sync_message(self, message):
        """检查消息是否应该被同步"""
        # 检查消息是否有内容 - 包括所有文件类型
        has_text = bool(message.text)
        has_media = bool(
            message.media or message.document or message.photo or message.video or
            message.audio or message.voice or message.video_note or 
            message.sticker or message.animation
        )
        
        # 如果既没有文本也没有媒体，跳过
        if not has_text and not has_media:
            return False
            
        filters = self.config.get('filters', {})
        
        # 如果没有设置任何过滤器，同步所有消息
        if not any(filters.values()):
            return True
        
        # 关键词过滤
        if filters.get('keywords') and has_text:
            if not any(keyword.lower() in message.text.lower() for keyword in filters['keywords']):
                return False
        
        # 排除关键词
        if filters.get('exclude_keywords') and has_text:
            if any(keyword.lower() in message.text.lower() for keyword in filters['exclude_keywords']):
                return False
        
        # 媒体类型过滤
        if filters.get('media_only') and not has_media:
            return False
        
        if filters.get('text_only') and has_media:
            return False
        
        return True
    
    async def sync_message(self, event):
        """同步新消息到目标频道"""
        target_channel = self.config['target_channel']
        success = await self.sync_single_message(
            event.message, 
            event.chat_id, 
            target_channel
        )
        if success:
            logger.info(f"新消息已同步到 {target_channel}")
    
    async def sync_history(self, source_chat_id, limit=None, days_back=None):
        """同步历史消息"""
        try:
            target_channel = self.config['target_channel']
            source_name = self.config['source_chats'].get(source_chat_id, str(source_chat_id))
            
            logger.info(f"开始同步 {source_name} 的历史消息...")
            logger.info(f"源ID: {source_chat_id} (类型: {type(source_chat_id)})")
            
            # 确保chat_id是整数
            chat_id = int(source_chat_id)
            
            # 先尝试获取频道/群组信息
            try:
                entity = await self.client.get_entity(chat_id)
                entity_type = "频道" if hasattr(entity, 'broadcast') and entity.broadcast else "群组"
                entity_name = entity.title if hasattr(entity, 'title') else str(entity)
                logger.info(f"成功获取{entity_type}信息: {entity_name}")
            except Exception as entity_error:
                logger.error(f"无法获取频道/群组 {chat_id} 的信息: {entity_error}")
                logger.error("可能的原因:")
                logger.error("1. 频道/群组ID不正确")
                logger.error("2. 你的账号没有访问该频道/群组的权限")
                logger.error("3. 频道/群组不存在或已被删除")
                logger.error("4. 私有频道需要先加入或获得访问权限")
                
                # 尝试其他方法获取实体
                logger.info("尝试其他方法获取频道信息...")
                try:
                    # 尝试通过对话列表查找
                    async for dialog in self.client.iter_dialogs():
                        if dialog.id == chat_id:
                            logger.info(f"在对话列表中找到: {dialog.name}")
                            entity = dialog.entity
                            break
                    else:
                        logger.error("在对话列表中也未找到该频道")
                        return
                except Exception as dialog_error:
                    logger.error(f"通过对话列表查找也失败: {dialog_error}")
                    return
            
            # 计算时间范围
            offset_date = None
            if days_back:
                offset_date = datetime.now() - timedelta(days=days_back)
            
            # 获取历史消息
            messages = []
            async for message in self.client.iter_messages(
                chat_id,
                limit=limit,
                offset_date=offset_date,
                reverse=True  # 按时间顺序同步，确保被回复的消息先处理
            ):
                messages.append(message)
            
            # 确保消息按时间顺序排列（最旧的在前）
            messages.sort(key=lambda x: x.date)
            
            logger.info(f"找到 {len(messages)} 条历史消息")
            
            # 同步消息
            synced_count = 0
            for i, message in enumerate(messages):
                # 添加调试信息 - 检测所有文件类型
                msg_types = []
                if message.text:
                    msg_types.append("文本")
                if message.document:
                    mime_type = message.document.mime_type if message.document.mime_type else 'unknown'
                    file_name = message.document.attributes[0].file_name if message.document.attributes and hasattr(message.document.attributes[0], 'file_name') else 'unnamed'
                    msg_types.append(f"文档({mime_type}:{file_name})")
                if message.photo:
                    msg_types.append("图片")
                if message.video:
                    msg_types.append("视频")
                if message.audio:
                    msg_types.append("音频")
                if message.voice:
                    msg_types.append("语音")
                if message.video_note:
                    msg_types.append("视频消息")
                if message.sticker:
                    msg_types.append("贴纸")
                if message.animation:
                    msg_types.append("动画/GIF")
                if message.media and not any([message.document, message.photo, message.video, message.audio, message.voice, message.video_note, message.sticker, message.animation]):
                    msg_types.append(f"其他媒体({type(message.media).__name__})")
                
                msg_type = "+".join(msg_types) if msg_types else "空消息"
                
                if message.reply_to:
                    reply_id = message.reply_to.reply_to_msg_id if hasattr(message.reply_to, 'reply_to_msg_id') else "unknown"
                    logger.info(f"处理消息 {i+1}: {msg_type} 回复消息 (回复ID: {reply_id})")
                else:
                    logger.info(f"处理消息 {i+1}: {msg_type} 普通消息")
                
                success = await self.sync_single_message(
                    message, 
                    source_chat_id, 
                    target_channel,
                    add_timestamp=True
                )
                
                if success:
                    synced_count += 1
                    logger.info(f"✅ 消息 {i+1} 同步成功")
                else:
                    logger.warning(f"❌ 消息 {i+1} 同步失败")
                
                # 显示进度
                if (i + 1) % 10 == 0:
                    logger.info(f"已处理 {i + 1}/{len(messages)} 条消息，已同步 {synced_count} 条")
                
                # 避免API限制
                await asyncio.sleep(0.5)
            
            logger.info(f"历史消息同步完成: {source_name} - 共同步 {synced_count}/{len(messages)} 条消息")
            
        except Exception as e:
            logger.error(f"同步历史消息时出错: {e}")
            logger.error(f"群组: {source_name} (ID: {source_chat_id})")
    
    async def sync_all_history(self):
        """同步所有源的历史消息"""
        history_config = self.config.get('history_sync', {})
        
        if not history_config.get('enabled', False):
            logger.info("历史消息同步未启用")
            return
        
        limit = history_config.get('limit', 100)
        days_back = history_config.get('days_back', 7)
        
        logger.info(f"开始同步所有源的历史消息 (限制: {limit} 条, 时间范围: {days_back} 天)")
        
        for source_chat_id in self.config['source_chats']:
            await self.sync_history(source_chat_id, limit, days_back)
            # 源之间的延迟
            await asyncio.sleep(2)
    
    async def start_sync(self, sync_history_first=True):
        """开始监听和同步消息"""
        if not self.client:
            await self.initialize_client()
        
        # 首先同步历史消息
        if sync_history_first:
            await self.sync_all_history()
        
        # 注册消息处理器
        @self.client.on(events.NewMessage)
        async def handler(event):
            await self.sync_message(event)
        
        logger.info("开始监听新消息...")
        logger.info(f"监听的源: {list(self.config['source_chats'].values())}")
        logger.info(f"目标频道: {self.config['target_channel']}")
        
        # 保持运行
        await self.client.run_until_disconnected()

async def main():
    syncer = TelegramSyncer()
    if syncer.config:
        await syncer.start_sync()
    else:
        logger.error("无法加载配置，程序退出")

if __name__ == "__main__":
    asyncio.run(main())