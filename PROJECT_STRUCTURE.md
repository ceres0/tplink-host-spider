# 项目结构说明

## 目录结构

```
tplink-host-spider/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── core/                     # 核心功能模块
│   │   ├── __init__.py
│   │   ├── router_monitor.py     # 路由器监控核心逻辑
│   │   └── monitor_service.py    # 监控服务整合
│   ├── utils/                    # 工具模块
│   │   ├── __init__.py
│   │   ├── config_manager.py     # 配置管理
│   │   └── data_manager.py       # 数据管理
│   ├── notifiers/                # 通知模块
│   │   ├── __init__.py
│   │   └── feishu_notifier.py    # 飞书通知
│   └── managers/                 # 管理模块
│       ├── __init__.py
│       └── hosts_manager.py      # hosts文件和Git管理
├── tests/                        # 测试文件
│   ├── test_integration.py       # 综合测试
│   ├── test_hosts.py            # hosts功能测试
│   ├── test_monitor.py          # 监控功能测试
│   └── demo_hosts.py            # hosts功能演示
├── scripts/                      # 脚本文件
│   └── start_monitor.sh         # 启动脚本
├── config/                       # 配置文件（已移动到根目录）
│   ├── router_config.json       # 主配置文件
│   └── router_config.json.example # 配置示例
├── data/                         # 数据文件
│   └── wan_status_data.json     # WAN状态历史数据
├── logs/                         # 日志文件
│   └── router_monitor.log       # 运行日志
├── main.py                       # 原始主程序（保留作为备份）
├── main_new.py                   # 新的模块化主程序
├── router_monitor.py             # 原始路由器监控（保留作为备份）
├── feishu_notifier.py           # 原始飞书通知（保留作为备份）
├── hosts                         # 动态hosts文件
├── requirements.txt              # Python依赖
├── environment.yml               # Conda环境配置
└── README.md                     # 项目说明
```

## 模块说明

### 核心模块 (src/core/)
- `router_monitor.py`: 路由器登录、获取WAN状态等核心功能
- `monitor_service.py`: 整合所有功能的主服务类

### 工具模块 (src/utils/)
- `config_manager.py`: 配置文件的加载、保存、验证
- `data_manager.py`: WAN状态数据的存储和历史管理

### 通知模块 (src/notifiers/)
- `feishu_notifier.py`: 飞书机器人通知功能

### 管理模块 (src/managers/)
- `hosts_manager.py`: hosts文件管理和Git版本控制

## 使用方法

### 直接运行
```bash
python main_new.py
```

### 后台运行
```bash
./scripts/start_monitor.sh start
```

### 功能测试
```bash
python tests/test_integration.py
```

## 配置文件

配置文件位于根目录的 `router_config.json`，包含以下配置项：

- 路由器连接配置
- 飞书通知配置  
- hosts文件管理配置
- Git版本控制配置

详细配置说明请参考 `router_config.json.example`。
