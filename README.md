# TP-LINK 路由器 WAN 口监控与飞书通知系统

> 本程序为校园网内动态分配 IP 导致 WAN 口状态频繁变化而编写的监控脚本，旨在自动获取和记录路由器的 WAN 口状态信息，并在 IP 变化时发送飞书通知。

## 功能特性

1. **定时监控**: 每分钟自动获取一次 WAN 口状态信息
2. **智能身份验证**: 自动检测登录 token 失效并重新登录
3. **IP 变化检测**: 实时监控 WAN 口 IP 地址变化
4. **飞书通知**: IP 变化时自动发送通知到飞书群
5. **启动通知**: 程序启动时发送当前 IP 状态
6. **配置文件管理**: 自动保存密码、加密密码和 stok 到配置文件
7. **数据持久化**: 将 WAN 口状态信息保存到历史文件中
8. **完整日志**: 详细的运行日志记录
9. **后台运行**: 支持后台运行和进程管理
10. **模块化设计**: 功能模块化，便于维护和扩展

## 环境要求

- Python 3.8+
- requests 库
- 推荐使用 conda 环境管理（spider 环境）

## 安装步骤

### 1. 使用 conda 环境

```bash
# 激活现有的 spider 环境
conda activate spider

# 或创建新的环境
conda create -n spider python=3.8
conda activate spider
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 文件结构

### 核心文件

- `main.py`: 主程序入口，负责协调路由器监控和飞书通知
- `router_monitor.py`: 路由器信息获取模块，包含登录、获取 WAN 状态等功能
- `feishu_notifier.py`: 飞书推送模块，负责消息格式化和推送
- `test_monitor.py`: 测试版本（运行 3 次后自动停止）

### 配置和数据文件

- `router_config.json`: 配置文件（路由器和飞书相关配置）
- `wan_status_data.json`: WAN 口状态历史数据（生成）
- `router_monitor.log`: 运行日志（生成）
- `router_monitor_test.log`: 测试日志（生成）

### 环境和脚本文件

- `start_monitor.sh`: 后台启动管理脚本
- `environment.yml`: conda 环境配置文件
- `requirements.txt`: Python 依赖列表

## 使用方法

### 1. 配置设置

在 `router_config.json` 中配置以下参数：

```json
{
  "host": "192.168.1.1", // 路由器IP地址
  "password": "your-router-password", // 路由器管理密码
  "encrypt_password": "", // 加密后的密码（自动生成）
  "stok": "", // 登录令牌（自动获取）
  "last_login_time": "", // 最后登录时间（自动记录）
  "feishu_webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-url", // 飞书机器人webhook地址
  "feishu_secret": "your-feishu-secret-key" // 飞书机器人密钥
}
```

### 2. 飞书配置步骤

1. 在飞书中创建自定义机器人
2. 获取 webhook URL 和密钥
3. 将真实的 webhook URL 和密钥填入配置文件
4. `feishu_notifier.py` 中已实现飞书的签名算法

### 3. 测试运行

```bash
# 激活conda环境
conda activate spider

# 运行测试版本（只运行3次，包含飞书通知测试）
python3 test_monitor.py

# 直接运行主程序（会持续运行）
python3 main.py
```

### 4. 后台运行（推荐）

```bash
# 启动监控
./start_monitor.sh start

# 查看状态
./start_monitor.sh status

# 停止监控
./start_monitor.sh stop

# 重启监控
./start_monitor.sh restart

# 查看实时日志
./start_monitor.sh logs
```

## 飞书消息格式

### IP 变化通知

```
路由器WAN口IP地址发生变化
旧IP: 192.168.1.100
新IP: 192.168.1.101
时间: 2025-07-11 17:59:37
```

### 启动通知

```
路由器监控程序已启动
当前WAN口IP: 192.168.1.100
时间: 2025-07-11 17:59:37
```

## 配置文件结构

`router_config.json` 文件包含路由器和飞书配置信息：

```json
{
  "host": "路由器 IP 地址",
  "password": "路由器管理密码",
  "encrypt_password": "加密后的密码（自动生成）",
  "stok": "当前有效的登录token（自动获取）",
  "last_login_time": "最后登录时间（自动记录）",
  "feishu_webhook_url": "飞书机器人webhook地址",
  "feishu_secret": "飞书机器人密钥"
}
```

## 数据文件结构

`wan_status_data.json` 文件包含历史 WAN 口状态数据：

```json
[
    {
        "timestamp": "2025-07-11T17:59:37.178456",
        "data": {
            "network": {
                "wan_status": {
                    "proto": "dhcp",
                    "ipaddr": "10.96.46.145",
                    "netmask": "255.255.252.0",
                    "gateway": "10.96.44.1",
                    "up": true,
                    ...
                }
            }
        }
    }
]
```

## 测试结果

程序已通过测试，测试结果显示：

1. ✅ **路由器连接**: 成功连接到路由器并获取 WAN 状态
2. ✅ **身份验证**: 自动处理 stok 过期和重新登录
3. ✅ **IP 提取**: 正确提取当前 WAN 口 IP 地址（如：10.96.46.145）
4. ✅ **数据保存**: 成功保存 WAN 状态历史数据
5. ✅ **飞书集成**: 飞书通知器初始化成功（需配置真实 webhook）
6. ✅ **模块化**: 所有模块导入和调用正常

## 注意事项

### 路由器相关

1. 程序会自动保留最近 10 条 WAN 口状态记录
2. 如果登录 token 失效，程序会自动重新登录
3. 所有操作都有详细的日志记录
4. 程序支持 Ctrl+C 优雅退出

### 飞书通知相关

1. 请确保将配置文件中的 `feishu_webhook_url` 和 `feishu_secret` 替换为真实值
2. 签名算法已在 `feishu_notifier.py` 中正确实现
3. 监控间隔为 60 秒，可根据需要在代码中调整
4. 日志会同时输出到控制台和 `router_monitor.log` 文件
5. 如果飞书配置为默认值，程序将跳过通知功能但正常监控

## 故障排除

### 网络连接问题

1. 如果程序无法连接路由器，请检查网络连接和路由器 IP 地址
2. 如果登录失败，请检查密码是否正确
3. 查看日志文件了解详细错误信息

### 飞书通知问题

1. 检查飞书机器人配置是否正确
2. 确认 webhook URL 和密钥是否有效
3. 查看日志中的飞书通知相关错误信息

### 环境问题

1. 确保使用 spider conda 环境
2. 确认 requests 库已正确安装
3. 检查 Python 版本是否为 3.8+
