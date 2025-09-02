#!/bin/zsh

# 路由器WAN口监控脚本启动器
# 使用方法: ./start_monitor.sh [start|stop|status|restart]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$PROJECT_DIR/src/main.py"
PID_FILE="$PROJECT_DIR/monitor.pid"
LOG_FILE="$PROJECT_DIR/logs/router_monitor.log"

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
        # 使用setsid创建新的进程组，便于后续管理
        nohup setsid conda run -n spider python "$PYTHON_SCRIPT" > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "监控程序已启动 (PID: $!)"
        echo "日志文件: $LOG_FILE"
        ;;
    
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "停止监控程序 (PID: $PID)..."
                # 杀死进程组，确保所有相关进程都被停止
                kill -TERM -$PID 2>/dev/null || kill $PID
                
                # 等待进程完全停止
                for i in {1..10}; do
                    if ! ps -p $PID > /dev/null 2>&1; then
                        break
                    fi
                    sleep 0.5
                done
                
                # 如果进程仍然存在，强制杀死
                if ps -p $PID > /dev/null 2>&1; then
                    echo "强制停止进程..."
                    kill -KILL -$PID 2>/dev/null || kill -KILL $PID
                    sleep 1
                fi
                
                rm -f "$PID_FILE"
            else
                echo "PID文件中的进程已不存在，清理PID文件..."
                rm -f "$PID_FILE"
            fi
        fi
        
        # 无论是否有PID文件，都尝试清理相关的Python进程
        PYTHON_PIDS=$(pgrep -f "python.*$PROJECT_DIR/src/main.py" 2>/dev/null)
        if [ -n "$PYTHON_PIDS" ]; then
            echo "清理相关的Python进程: $PYTHON_PIDS"
            pkill -TERM -f "python.*$PROJECT_DIR/src/main.py" 2>/dev/null
            sleep 2
            # 如果还有进程存在，强制杀死
            REMAINING_PIDS=$(pgrep -f "python.*$PROJECT_DIR/src/main.py" 2>/dev/null)
            if [ -n "$REMAINING_PIDS" ]; then
                echo "强制停止剩余进程: $REMAINING_PIDS"
                pkill -KILL -f "python.*$PROJECT_DIR/src/main.py" 2>/dev/null
            fi
        fi
        
        # 最终检查
        FINAL_CHECK=$(pgrep -f "python.*$PROJECT_DIR/src/main.py" 2>/dev/null)
        if [ -z "$FINAL_CHECK" ]; then
            echo "监控程序已停止"
        else
            echo "警告: 可能仍有进程在运行: $FINAL_CHECK"
        fi
        ;;
    
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "监控程序正在运行 (PID: $PID)"
                echo "日志文件: $LOG_FILE"
                
                # 显示相关的python进程
                PYTHON_PIDS=$(pgrep -f "python.*$PROJECT_DIR/src/main.py" 2>/dev/null)
                if [ -n "$PYTHON_PIDS" ]; then
                    echo "Python进程 PIDs: $PYTHON_PIDS"
                fi
            else
                echo "监控程序未运行 (PID文件存在但进程不存在)"
                # 检查是否有遗留的python进程
                PYTHON_PIDS=$(pgrep -f "python.*$PROJECT_DIR/src/main.py" 2>/dev/null)
                if [ -n "$PYTHON_PIDS" ]; then
                    echo "发现遗留的Python进程: $PYTHON_PIDS"
                    echo "建议运行: $0 stop 来清理"
                fi
                rm -f "$PID_FILE"
            fi
        else
            # 检查是否有没有记录的python进程在运行
            PYTHON_PIDS=$(pgrep -f "python.*$PROJECT_DIR/src/main.py" 2>/dev/null)
            if [ -n "$PYTHON_PIDS" ]; then
                echo "监控程序可能在运行 (无PID文件，但发现相关进程: $PYTHON_PIDS)"
                echo "建议运行: $0 stop 来清理，然后重新启动"
            else
                echo "监控程序未运行"
            fi
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
