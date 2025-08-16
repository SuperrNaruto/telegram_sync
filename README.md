# Telegram消息同步工具

这个工具可以将Telegram群组或频道的消息实时同步到你的目标频道。

## 功能特性

- **历史消息同步**: 同步源群组/频道的已有消息
- **实时消息同步**: 监听并同步新消息
- **多源支持**: 支持多个源群组/频道
- **时间戳标记**: 历史消息自动添加原始时间
- **消息过滤**: 支持关键词和媒体类型过滤
- **进度显示**: 历史同步时显示详细进度
- **API限制处理**: 自动处理Telegram API限制

## 安装步骤

### 1. 获取Telegram API凭据

1. 访问 https://my.telegram.org/apps
2. 登录你的Telegram账号
3. 创建新应用，获取 `api_id` 和 `api_hash`

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置工具

运行设置脚本来配置你的同步设置:

```bash
python setup.py
```

这个脚本会:
- 要求你输入API凭据
- 显示你的群组和频道列表
- 帮你选择源和目标
- 自动生成配置文件

### 4. 配置工具

**方法1: 交互式配置 (推荐)**:
```bash
python setup.py
```

**方法2: 快速配置 (避免编码问题)**:
```bash
python quick_setup.py
```

**方法3: 命令行配置**:
```bash
python quick_setup.py <api_id> <api_hash> <phone> <target_channel> [source_ids...]
```

**方法4: 手动编辑**:
直接编辑 `config.json` 文件，填入你的API信息。

### 5. 开始同步

**完整同步 (推荐)**:
```bash
python telegram_sync.py
```
这会先同步历史消息，然后开始实时监听新消息。

**仅同步历史消息**:
```bash
python history_sync.py
```
这个工具提供交互式界面，让你选择同步哪些源和参数。

**仅实时监听** (跳过历史消息):
修改 `config.json` 中的 `history_sync.enabled` 为 `false`，然后运行主程序。

## 配置说明

`config.json` 文件包含以下配置:

```json
{
  "api_id": "你的API ID",
  "api_hash": "你的API Hash",
  "phone": "你的手机号",
  "target_channel": "@目标频道用户名",
  "source_chats": {
    -1001234567890: "源群组名称"
  },
  "add_source_info": true,
  "history_sync": {
    "enabled": true,
    "limit": 100,
    "days_back": 7
  },
  "filters": {
    "keywords": ["关键词过滤"],
    "exclude_keywords": ["排除关键词"],
    "media_only": false,
    "text_only": false
  }
}
```

## 高级功能

### 历史消息同步

配置 `history_sync` 部分:

- `enabled`: 是否启用历史消息同步
- `limit`: 每个源最多同步多少条消息 (默认100)
- `days_back`: 同步多少天内的消息 (默认7天)

历史消息会按时间顺序同步，并自动添加原始时间戳。

### 消息过滤

你可以在配置文件中设置过滤条件:

- `keywords`: 只同步包含这些关键词的消息
- `exclude_keywords`: 排除包含这些关键词的消息
- `media_only`: 只同步媒体消息
- `text_only`: 只同步文本消息

### 批量历史同步

使用 `history_sync.py` 可以:

1. 同步所有源的历史消息
2. 选择特定源进行同步
3. 自定义同步参数 (消息数量、时间范围)

### 获取群组/频道ID

如果你不知道群组或频道的ID，可以:

1. 将机器人添加到群组
2. 发送消息 `/id` (如果有相关机器人)
3. 或者使用我们的设置脚本自动获取

## 注意事项

1. 确保你的账号有权限访问源群组/频道
2. 确保你是目标频道的管理员
3. 首次运行需要验证手机号码
4. 保持程序运行以实现实时同步

## 故障排除

### 常见问题

1. **编码错误**: 在Linux环境下如果遇到UTF-8编码问题，使用 `quick_setup.py` 或手动编辑配置文件
2. **权限错误**: 确保你有访问源和目标的权限
3. **API限制**: Telegram有API调用频率限制，程序会自动处理
4. **会话过期**: 删除 `.session` 文件重新登录

### 环境变量设置 (Linux)

如果遇到编码问题，可以设置环境变量:
```bash
export PYTHONIOENCODING=utf-8
export LC_ALL=C.UTF-8
```

### 配置文件示例

如果配置工具出现问题，可以手动创建 `config.json`:
```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here",
  "phone": "+8613800138000",
  "target_channel": "-1002557556585",
  "source_chats": {
    -1002406053912: "源群组1",
    -1002426727534: "源群组2",
    -1001768155075: "源群组3"
  },
  "add_source_info": true,
  "history_sync": {
    "enabled": true,
    "limit": 100,
    "days_back": 7
  },
  "filters": {
    "keywords": [],
    "exclude_keywords": [],
    "media_only": false,
    "text_only": false
  }
}
```

### 日志

程序会输出详细的日志信息，帮助你诊断问题。

## 免责声明

请遵守Telegram的服务条款和相关法律法规。此工具仅供学习和合法用途使用。