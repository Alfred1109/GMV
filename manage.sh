#!/bin/bash

# GeniusMed Vault医学科研专病库平台管理脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
APP_NAME="GeniusMed Vault"
FLASK_APP="app.py"
VENV_PATH="./venv"
PID_FILE="app.pid"
LOG_FILE="flask.log"
PORT=80
HOST="0.0.0.0"
DEBUG_MODE=true

# 检查虚拟环境
check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        echo -e "${RED}错误: 找不到虚拟环境 ($VENV_PATH)${NC}"
        echo -e "请先运行 ${YELLOW}python -m venv venv${NC} 创建虚拟环境"
        exit 1
    fi
}

# 激活虚拟环境
activate_venv() {
    check_venv
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows环境
        source "$VENV_PATH/Scripts/activate"
    else
        # Linux/Mac环境
        source "$VENV_PATH/bin/activate"
    fi
}

# 启动应用
start() {
    echo -e "${BLUE}正在启动 $APP_NAME...${NC}"
    
    # 检查应用是否已在运行
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}警告: $APP_NAME 已在运行 (PID: $PID)${NC}"
            echo -e "使用 ${GREEN}./manage.sh restart${NC} 重启应用"
            return 1
        else
            # PID文件存在但进程不存在，清理PID文件
            rm "$PID_FILE"
        fi
    fi
    
    # 激活虚拟环境并启动应用
    activate_venv
    
    if [ "$DEBUG_MODE" = true ]; then
        # 调试模式
        echo -e "${YELLOW}以调试模式启动...${NC}"
        nohup python "$FLASK_APP" > "$LOG_FILE" 2>&1 &
    else
        # 生产模式
        echo -e "${GREEN}以生产模式启动...${NC}"
        nohup python "$FLASK_APP" --no-debugger --no-reload > "$LOG_FILE" 2>&1 &
    fi
    
    # 保存PID
    echo $! > "$PID_FILE"
    echo -e "${GREEN}$APP_NAME 已启动 (PID: $(cat "$PID_FILE"))${NC}"
    echo -e "可以通过 ${BLUE}http://localhost:$PORT${NC} 访问应用"
    echo -e "日志保存在: ${YELLOW}$LOG_FILE${NC}"
}

# 停止应用
stop() {
    echo -e "${BLUE}正在停止 $APP_NAME...${NC}"
    
    # 检查PID文件
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}警告: 找不到PID文件，应用可能未运行${NC}"
        return 1
    fi
    
    # 获取PID并终止进程
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        kill "$PID"
        sleep 2
        
        # 检查进程是否已终止
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}进程未响应，尝试强制终止...${NC}"
            kill -9 "$PID"
            sleep 1
        fi
        
        # 最终检查
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${RED}无法终止进程 (PID: $PID)${NC}"
            return 1
        else
            echo -e "${GREEN}$APP_NAME 已停止${NC}"
        fi
    else
        echo -e "${YELLOW}进程 (PID: $PID) 已不存在${NC}"
    fi
    
    # 删除PID文件
    rm "$PID_FILE"
}

# 重启应用
restart() {
    echo -e "${BLUE}正在重启 $APP_NAME...${NC}"
    stop
    sleep 2
    start
}

# 查看状态
status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}$APP_NAME 正在运行 (PID: $PID)${NC}"
            echo -e "可以通过 ${BLUE}http://localhost:$PORT${NC} 访问应用"
            return 0
        else
            echo -e "${YELLOW}$APP_NAME 已停止，但PID文件仍然存在${NC}"
            return 1
        fi
    else
        echo -e "${RED}$APP_NAME 未运行${NC}"
        return 1
    fi
}

# 查看日志
logs() {
    if [ -f "$LOG_FILE" ]; then
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            # Windows
            tail -n 50 "$LOG_FILE"
        else
            # Linux/Mac
            tail -n 50 -f "$LOG_FILE"
        fi
    else
        echo -e "${YELLOW}日志文件不存在: $LOG_FILE${NC}"
    fi
}

# 运行单元测试
run_tests() {
    echo -e "${BLUE}运行单元测试...${NC}"
    activate_venv
    python -m pytest tests/ -v
}

# 运行API测试
test_api() {
    echo -e "${BLUE}运行API测试...${NC}"
    activate_venv
    python test_api.py
}

# 运行回归分析API测试
test_regression() {
    echo -e "${BLUE}运行回归分析API测试...${NC}"
    activate_venv
    python test_regression_api.py
}

# 初始化或重置数据库
reset_db() {
    echo -e "${YELLOW}警告: 此操作将重置数据库，所有数据将丢失!${NC}"
    read -p "确定要继续吗? (y/n): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        echo -e "${BLUE}重置数据库...${NC}"
        activate_venv
        python reset_db.py
        echo -e "${GREEN}数据库已重置${NC}"
    else
        echo -e "${BLUE}操作已取消${NC}"
    fi
}

# 迁移数据库
migrate_db() {
    echo -e "${BLUE}执行数据库迁移...${NC}"
    activate_venv
    python db_migrate.py
    echo -e "${GREEN}数据库迁移完成${NC}"
}

# 显示帮助信息
help() {
    echo -e "${BLUE}$APP_NAME 管理脚本${NC}"
    echo -e "用法: ./manage.sh [命令]"
    echo
    echo -e "可用命令:"
    echo -e "  ${GREEN}start${NC}      启动应用"
    echo -e "  ${GREEN}stop${NC}       停止应用"
    echo -e "  ${GREEN}restart${NC}    重启应用"
    echo -e "  ${GREEN}status${NC}     查看应用状态"
    echo -e "  ${GREEN}logs${NC}       查看应用日志"
    echo -e "  ${GREEN}test${NC}       运行单元测试"
    echo -e "  ${GREEN}api_test${NC}   运行API测试"
    echo -e "  ${GREEN}reg_test${NC}   运行回归分析API测试"
    echo -e "  ${GREEN}reset_db${NC}   重置数据库"
    echo -e "  ${GREEN}migrate${NC}    执行数据库迁移"
    echo -e "  ${GREEN}help${NC}       显示此帮助信息"
}

# 主函数
main() {
    # 检查命令行参数
    if [ $# -eq 0 ]; then
        help
        exit 1
    fi
    
    # 根据命令执行相应操作
    case "$1" in
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        status)
            status
            ;;
        logs)
            logs
            ;;
        test)
            run_tests
            ;;
        api_test)
            test_api
            ;;
        reg_test)
            test_regression
            ;;
        reset_db)
            reset_db
            ;;
        migrate)
            migrate_db
            ;;
        help)
            help
            ;;
        *)
            echo -e "${RED}错误: 未知命令 '$1'${NC}"
            help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 