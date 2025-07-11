# TP-LINK 路由器 WAN 口监控程序

> 本程序为校园网内动态分配 IP 导致 WAN 口状态频繁变化而编写的监控脚本，旨在自动获取和记录路由器的 WAN 口状态信息。

## 功能特性

1. **定时监控**: 每分钟自动获取一次 WAN 口状态信息
2. **智能身份验证**: 自动检测登录 token 失效并重新登录
3. **配置文件管理**: 自动保存密码、加密密码和 stok 到配置文件
4. **数据持久化**: 将 WAN 口状态信息保存到历史文件中
5. **完整日志**: 详细的运行日志记录
6. **后台运行**: 支持后台运行和进程管理

## 环境要求

- Python 3.8+
- requests 库
- 推荐使用 conda 环境管理

## 安装步骤

### 1. 创建 conda 环境（可选）

```bash
conda create -n spider python=3.8
conda activate spider
# or
conda env create -f environment.yml
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 文件说明

- `main.py`: 主程序文件
- `test_monitor.py`: 测试版本（运行 3 次后自动停止）
- `start_monitor.sh`: 后台启动管理脚本
- `environment.yml`: conda 环境配置文件
- `requirements.txt`: Python 依赖列表
- `router_config.json`: 配置文件（路由器本地 IP、密码等）
- `wan_status_data.json`: WAN 口状态历史数据（生成）
- `router_monitor.log`: 运行日志（生成）

## 使用方法

### 1. 测试运行

```bash
# 激活conda环境
conda activate spider

# 运行测试版本（只运行3次）
python test_monitor.py

# 直接运行主程序（会持续运行）
python main.py
```

### 2. 后台运行（推荐）

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

## 配置文件结构

`router_config.json` 文件包含以下信息：

```json
{
  "host": "路由器 IP 地址",
  "password": "原始密码",
  "encrypt_password": "加密后的密码",
  "stok": "当前有效的登录token",
  "last_login_time": "最后登录时间"
}
```

## 数据文件结构

`wan_status_data.json` 文件包含历史 WAN 口状态数据：

```json
[
    {
        "timestamp": "2025-07-11T10:30:00.123456",
        "data": {
            "network": {
                "wan_status": {
                    "proto": "dhcp",
                    "ipaddr": "192.168.1.100",
                    ...
                }
            }
        }
    }
]
```

## 注意事项

1. 程序会自动保留最近 10 条 WAN 口状态记录
2. 如果登录 token 失效，程序会自动重新登录
3. 所有操作都有详细的日志记录
4. 程序支持 Ctrl+C 优雅退出

## 故障排除

1. 如果程序无法连接路由器，请检查网络连接和路由器 IP 地址
2. 如果登录失败，请检查密码是否正确
3. 查看日志文件了解详细错误信息
