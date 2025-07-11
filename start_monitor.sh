#!/bin/bash

# 路由器WAN口监控脚本启动器
# 使用方法: ./start_monitor.sh [start|stop|status|restart]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/main.py"
PID_FILE="$SCRIPT_DIR/monitor.pid"
LOG_FILE="$SCRIPT_DIR/router_monitor.log"

case "$1" in
    start)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "监控程序已在运行 (PID: $PID)"
                exit 1
            else
                rm -f "$PID_FILE"
            fi
        fi
        
        echo "启动路由器WAN口监控程序..."
        nohup conda run -n spider python "$PYTHON_SCRIPT" > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "监控程序已启动 (PID: $!)"
        echo "日志文件: $LOG_FILE"
        ;;
    
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "停止监控程序 (PID: $PID)..."
                kill $PID
                rm -f "$PID_FILE"
                echo "监控程序已停止"
            else
                echo "监控程序未运行"
                rm -f "$PID_FILE"
            fi
        else
            echo "监控程序未运行"
        fi
        ;;
    
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "监控程序正在运行 (PID: $PID)"
                echo "日志文件: $LOG_FILE"
            else
                echo "监控程序未运行"
                rm -f "$PID_FILE"
            fi
        else
            echo "监控程序未运行"
        fi
        ;;
    
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    
    logs)
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo "日志文件不存在: $LOG_FILE"
        fi
        ;;
    
    *)
        echo "使用方法: $0 {start|stop|status|restart|logs}"
        echo ""
        echo "  start   - 启动监控程序"
        echo "  stop    - 停止监控程序"
        echo "  status  - 查看程序状态"
        echo "  restart - 重启监控程序"
        echo "  logs    - 实时查看日志"
        exit 1
        ;;
esac
