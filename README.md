# TP-LINK 路由器 WAN 口监控与飞书通知系统

> 本程序为校园网内动态分配 IP 导致 WAN 口状态频繁变化而编写的监控脚本，旨在自动获取和记录路由器的 WAN 口状态信息，并在 IP 变化时发送飞书通知。

## 🆕 v2.0 更新说明

- 📦 **模块化重构**: 采用面向对象设计，将功能分离为独立模块
- 🏠 **Hosts文件管理**: 自动维护hosts文件，绑定域名到WAN口IP
- 🔧 **Git集成**: 当IP变化时自动提交并推送hosts文件到远程仓库
- 📊 **更好的数据管理**: 独立的配置管理器和数据管理器
- 🧪 **完整测试**: 提供综合测试套件验证所有功能

## 功能特性

### 核心功能
1. **定时监控**: 每分钟自动获取一次 WAN 口状态信息
2. **智能身份验证**: 自动检测登录 token 失效并重新登录
3. **IP 变化检测**: 实时监控 WAN 口 IP 地址变化
4. **飞书通知**: IP 变化时自动发送通知到飞书群
5. **启动通知**: 程序启动时发送当前 IP 状态
6. **数据持久化**: 将 WAN 口状态信息保存到历史文件中
7. **完整日志**: 详细的运行日志记录
8. **后台运行**: 支持后台运行和进程管理

### 🆕 新增功能
9. **Hosts文件管理**: 自动维护hosts文件，绑定域名到当前WAN口IP
10. **Git版本控制**: IP变化时自动提交hosts文件并推送到远程仓库
11. **模块化架构**: 清晰的项目结构，便于维护和扩展
12. **配置管理**: 统一的配置管理系统，支持配置验证
13. **综合测试**: 完整的测试套件确保功能正常

## 环境要求

- Python 3.8+
- requests 库
- Git（如果需要Git功能）
- 推荐使用 conda 环境管理（spider 环境）

## 项目结构

```
tplink-host-spider/
├── src/                          # 源代码目录
│   ├── main.py                   # 🆕 模块化主程序
│   ├── core/                     # 核心功能模块
│   │   ├── router_monitor.py     # 路由器监控核心逻辑
│   │   └── monitor_service.py    # 监控服务整合
│   ├── utils/                    # 工具模块
│   │   ├── config_manager.py     # 配置管理
│   │   └── data_manager.py       # 数据管理
│   ├── notifiers/                # 通知模块
│   │   └── feishu_notifier.py    # 飞书通知
│   └── managers/                 # 管理模块
│       └── hosts_manager.py      # hosts文件和Git管理
├── tests/                        # 测试文件
│   ├── test_integration.py       # 综合测试
│   ├── test_hosts.py            # hosts功能测试
│   ├── test_monitor.py          # 监控功能测试
│   └── demo_hosts.py            # hosts功能演示
├── scripts/                      # 脚本文件
│   └── start_monitor.sh         # 启动脚本
├── data/                         # 数据文件
│   └── wan_status_data.json     # WAN状态历史数据
├── logs/                         # 日志文件
│   └── router_monitor.log       # 运行日志
├── hosts                         # 🆕 动态hosts文件
├── router_config.json            # 主配置文件
├── router_config.json.example    # 配置示例
└── requirements.txt              # Python依赖
```

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

### 模块说明

#### 核心模块 (src/core/)
- `router_monitor.py`: 路由器登录、获取WAN状态等核心功能
- `monitor_service.py`: 整合所有功能的主服务类

#### 工具模块 (src/utils/)
- `config_manager.py`: 配置文件的加载、保存、验证
- `data_manager.py`: WAN状态数据的存储和历史管理

#### 通知模块 (src/notifiers/)
- `feishu_notifier.py`: 飞书机器人通知功能

#### 管理模块 (src/managers/)
- `hosts_manager.py`: hosts文件管理和Git版本控制

### 数据文件
- `data/wan_status_data.json`: WAN 口状态历史数据（自动生成）
- `logs/router_monitor.log`: 运行日志（自动生成）
- `hosts`: 🆕 动态维护的hosts文件（自动生成）

## 使用方法

### 1. 配置设置

在 `router_config.json` 中配置以下参数：

```json
{
  "host": "192.168.1.1",
  "password": "your-router-password",
  "encrypt_password": "",
  "stok": "",
  "last_login_time": "",
  "feishu_webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-url",
  "feishu_secret": "your-feishu-secret-key",
  
  // 🆕 Hosts文件管理配置
  "domains": [
    "example.com",
    "www.example.com", 
    "api.example.com",
    "app.example.com",
    "home.mydomain.com"
  ],
  
  // 🆕 Git集成配置
  "git_enabled": true,
  "git_name": "Router Monitor",
  "git_email": "router@monitor.local",
  "git_remote": "origin",
  "git_branch": "main"
}
```

### 2. 飞书配置步骤

1. 在飞书中创建自定义机器人
2. 获取 webhook URL 和密钥
3. 将真实的 webhook URL 和密钥填入配置文件
4. `feishu_notifier.py` 中已实现飞书的签名算法

### 3. Git仓库配置（🆕 可选）

如果您想使用Git功能，需要先初始化仓库并设置远程地址：

```bash
# 初始化Git仓库（如果还没有）
git init

# 添加远程仓库
git remote add origin https://github.com/your-username/your-repo.git

# 设置Git用户信息（或在配置文件中设置）
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 4. 测试运行

```bash
# 激活conda环境
conda activate spider

# 🆕 运行综合功能测试
python tests/test_integration.py

# 🆕 测试hosts管理功能
python tests/test_hosts.py

# 运行监控功能测试（只运行3次）
python tests/test_monitor.py

# 🆕 运行主程序（模块化版本）
python src/main.py
```

### 5. 后台运行（推荐）

```bash
# 启动监控
./scripts/start_monitor.sh start

# 查看状态
./scripts/start_monitor.sh status

# 停止监控
./scripts/start_monitor.sh stop

# 重启监控
./scripts/start_monitor.sh restart

# 查看实时日志
./scripts/start_monitor.sh logs
```

## 🆕 新功能说明

### Hosts文件管理

程序会自动维护一个`hosts`文件，当WAN口IP变化时：

1. 自动更新hosts文件中配置的域名对应的IP地址
2. 保留文件中的注释和时间戳信息
3. 只有IP真正变化时才更新文件
4. 支持自定义域名列表配置

### Git版本控制

当启用Git功能时，程序会：

1. 检测IP变化后自动提交hosts文件更新
2. 推送更改到配置的远程仓库
3. 使用有意义的提交信息，包含新的IP地址
4. 支持自定义远程仓库和分支配置

### 模块化架构

新的架构提供以下优势：

1. **清晰的职责分离**: 每个模块只负责特定功能
2. **更好的可维护性**: 易于修改和扩展功能
3. **完整的错误处理**: 统一的异常处理机制
4. **全面的测试覆盖**: 每个模块都有对应测试

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

`router_config.json` 文件包含以下配置项：

```json
{
  // 路由器连接配置
  "host": "路由器 IP 地址",
  "password": "路由器管理密码",
  "encrypt_password": "加密后的密码（自动生成）",
  "stok": "当前有效的登录token（自动获取）",
  "last_login_time": "最后登录时间（自动记录）",
  
  // 飞书通知配置
  "feishu_webhook_url": "飞书机器人webhook地址",
  "feishu_secret": "飞书机器人密钥",
  
  // 🆕 Hosts文件管理配置
  "domains": ["需要绑定的域名列表"],
  
  // 🆕 Git版本控制配置
  "git_enabled": "是否启用Git功能",
  "git_name": "Git用户名",
  "git_email": "Git用户邮箱", 
  "git_remote": "Git远程仓库名",
  "git_branch": "Git分支名"
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

### v2.0 模块化系统测试 ✅

程序已通过全面的模块化测试：

1. ✅ **配置管理器**: 配置加载、保存、验证功能正常
2. ✅ **数据管理器**: WAN状态数据存储和历史管理正常
3. ✅ **路由器监控器**: 路由器连接和状态获取功能正常
4. ✅ **飞书通知器**: 通知系统初始化和消息格式化正常
5. ✅ **Hosts管理器**: 文件创建、更新、读取功能正常
6. ✅ **Git管理器**: 仓库检测和版本控制功能正常
7. ✅ **集成测试**: 所有模块整合运行正常

### 功能验证 ✅

- ✅ **路由器连接**: 成功连接到路由器并获取 WAN 状态
- ✅ **身份验证**: 自动处理 stok 过期和重新登录
- ✅ **IP 提取**: 正确提取当前 WAN 口 IP 地址
- ✅ **数据保存**: 成功保存 WAN 状态历史数据
- ✅ **飞书集成**: 飞书通知器初始化成功
- ✅ **Hosts管理**: 自动维护hosts文件绑定域名到IP
- ✅ **Git集成**: 自动提交和推送hosts文件更改
- ✅ **模块化**: 所有模块导入和调用正常

## 注意事项

### 路由器相关

1. 程序会自动保留最近 10 条 WAN 口状态记录
2. 如果登录 token 失效，程序会自动重新登录
3. 所有操作都有详细的日志记录，位于 `logs/` 目录
4. 程序支持 Ctrl+C 优雅退出

### 飞书通知相关

1. 请确保将配置文件中的 `feishu_webhook_url` 和 `feishu_secret` 替换为真实值
2. 签名算法已在 `src/notifiers/feishu_notifier.py` 中正确实现
3. 监控间隔为 60 秒，可根据需要在代码中调整
4. 如果飞书配置为默认值，程序将跳过通知功能但正常监控

### 🆕 Hosts文件相关

1. hosts文件会自动创建在项目根目录
2. 每次IP变化时会添加时间戳注释
3. 只有IP真正变化时才会更新文件
4. 可以在配置文件中自定义域名列表

### 🆕 Git功能相关

1. Git功能是可选的，可通过配置开启或关闭
2. 首次使用需要初始化Git仓库并设置远程地址
3. 每次IP变化会自动生成有意义的提交信息
4. 推送失败不会影响其他功能的正常运行

## 故障排除

### 网络连接问题

1. 如果程序无法连接路由器，请检查网络连接和路由器 IP 地址
2. 如果登录失败，请检查密码是否正确
3. 查看 `logs/router_monitor.log` 了解详细错误信息

### 飞书通知问题

1. 检查飞书机器人配置是否正确
2. 确认 webhook URL 和密钥是否有效
3. 查看日志中的飞书通知相关错误信息

### 🆕 Hosts文件问题

1. 确保项目目录有写入权限
2. 检查域名配置是否正确
3. 查看日志中的hosts管理相关信息

### 🆕 Git功能问题

1. 确保已安装Git并配置用户信息
2. 检查远程仓库地址是否正确
3. 确认有推送权限到目标仓库
4. Git操作失败不会影响其他功能

### 环境问题

1. 确保使用 spider conda 环境
2. 确认 requests 库已正确安装
3. 检查 Python 版本是否为 3.8+
4. 🆕 运行 `python tests/test_integration.py` 进行全面功能测试

---

## 更新日志

### v2.0.0 (2025-07-29)
- 🔄 **重大重构**: 采用模块化架构设计
- 🏠 **新增**: Hosts文件自动管理功能
- 🔧 **新增**: Git版本控制集成
- 📊 **改进**: 统一的配置和数据管理
- 🧪 **新增**: 完整的测试套件
- 📖 **更新**: 全面的文档和使用说明

### v1.0.0 (2025-07-11)
- 🚀 **首次发布**: 基础WAN口监控和飞书通知功能
