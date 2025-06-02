#!/bin/bash

# GeniusMedVault医学临床科研专病数据平台管理脚本
# 用于启动、停止和重启服务

# 定义颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 显示标题
show_title() {
    echo "-----------------------------------"
    echo " GeniusMedVault医学临床科研专病数据平台 (版权所有)"
    echo "-----------------------------------"
}

# 检查Python是否安装
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "未检测到Python安装，请安装Python 3.7或更高版本并重试。"
        exit 1
    fi
}

# 检查并激活虚拟环境
setup_venv() {
    # 检查python命令
    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        if command -v python &> /dev/null; then
            PYTHON_CMD="python"
        else
            log_error "未检测到Python安装，请安装Python 3.7或更高版本并重试。"
            exit 1
        fi
    fi
    
    log_info "使用Python命令: $PYTHON_CMD"
    
    # 检查虚拟环境路径
    VENV_ACTIVATE="venv/bin/activate"
    if [ -f "venv/Scripts/activate" ]; then
        VENV_ACTIVATE="venv/Scripts/activate"
    fi
    
    if [ ! -d "venv" ]; then
        log_info "正在创建虚拟环境..."
        $PYTHON_CMD -m venv venv
        log_info "正在安装依赖..."
        
        if [ -f "$VENV_ACTIVATE" ]; then
            source "$VENV_ACTIVATE"
            pip install -r requirements.txt
        else
            log_error "无法找到虚拟环境激活脚本: $VENV_ACTIVATE"
            log_info "尝试直接使用pip安装依赖..."
            $PYTHON_CMD -m pip install -r requirements.txt
        fi
    else
        if [ -f "$VENV_ACTIVATE" ]; then
            log_info "激活虚拟环境: $VENV_ACTIVATE"
            source "$VENV_ACTIVATE"
        else
            log_error "无法找到虚拟环境激活脚本: $VENV_ACTIVATE"
            log_info "尝试直接使用系统Python..."
        fi
    fi
}

# 获取Flask进程PID
get_flask_pid() {
    pgrep -f "flask run --host=0.0.0.0 --port=80" || pgrep -f "python3 -m flask run --host=0.0.0.0 --port=80"
}

# 启动应用
start_app() {
    show_title
    log_info "正在启动系统..."
    
    # 检查是否已经在运行
    if [ -n "$(get_flask_pid)" ]; then
        log_warn "系统已经在运行中!"
        return
    fi
    
    check_python
    setup_venv
    
    # 获取本机IP地址
    IP=$(hostname -I | awk '{print $1}')
    
    log_info "启动Flask应用..."
    # 启动Flask应用在后台
    FLASK_CMD="flask"
    if ! command -v flask &> /dev/null; then
        FLASK_CMD="$PYTHON_CMD -m flask"
    fi
    
    # 获取由pyenv管理的Python可执行文件的真实路径
    # 首先检查pyenv是否安装和配置
    PYTHON_EXECUTABLE_PATH=""
    if command -v pyenv &> /dev/null; then
        # 尝试获取pyenv实际使用的python路径
        REAL_PYENV_PYTHON_PATH=$(pyenv which $PYTHON_CMD 2>/dev/null)
        if [ -n "$REAL_PYENV_PYTHON_PATH" ] && [ -f "$REAL_PYENV_PYTHON_PATH" ]; then
            PYTHON_EXECUTABLE_PATH=$REAL_PYENV_PYTHON_PATH
            log_info "检测到 pyenv 管理的 Python 路径: $PYTHON_EXECUTABLE_PATH"
        else
            log_warn "pyenv 命令存在，但无法获取到 $PYTHON_CMD 的真实路径。将回退到使用 which。"
            PYTHON_EXECUTABLE_PATH=$(which $PYTHON_CMD)
        fi
    else
        log_info "未检测到 pyenv。将使用 which $PYTHON_CMD 来确定 Python 路径。"
        PYTHON_EXECUTABLE_PATH=$(which $PYTHON_CMD)
    fi

    if [ -z "$PYTHON_EXECUTABLE_PATH" ] || [ ! -e "$PYTHON_EXECUTABLE_PATH" ]; then
        log_error "无法确定 Python 可执行文件的有效路径或符号链接。setcap步骤将跳过。"
    else
        # 解析符号链接获取真实路径
        REAL_PYTHON_TARGET_PATH=$(readlink -f "$PYTHON_EXECUTABLE_PATH")
        if [ -z "$REAL_PYTHON_TARGET_PATH" ] || [ ! -f "$REAL_PYTHON_TARGET_PATH" ]; then
            log_error "无法解析Python可执行文件的真实路径: $PYTHON_EXECUTABLE_PATH. setcap步骤将跳过。"
        else
            log_info "Python可执行文件的真实路径为: $REAL_PYTHON_TARGET_PATH"
            # 检查是否已经有 cap_net_bind_service 权限
            if ! getcap "$REAL_PYTHON_TARGET_PATH" | grep -q "cap_net_bind_service+ep"; then
                log_info "为 $REAL_PYTHON_TARGET_PATH 设置 cap_net_bind_service 权限..."
                sudo setcap cap_net_bind_service=+ep "$REAL_PYTHON_TARGET_PATH"
                if [ $? -ne 0 ]; then
                    log_error "设置 setcap 失败。请检查是否有sudo权限或setcap是否正确安装。"
                    log_error "应用可能无法在80端口启动。尝试使用 sudo bash manage.sh start"
                else
                    log_info "setcap权限设置成功。"
                fi 
            else
                log_info "$REAL_PYTHON_TARGET_PATH 已有 cap_net_bind_service 权限。"
            fi
        fi
    fi
    
    nohup $FLASK_CMD run --host=0.0.0.0 --port=80 > flask.log 2>&1 &
    
    log_info "启动完成!"
    log_info "本地访问地址: http://localhost:80/login"
    log_info "其他设备可通过访问 http://$IP:80/login 连接到系统"
    log_info "服务已在后台启动，日志保存在 flask.log"
}

# 停止应用
stop_app() {
    show_title
    log_info "正在停止系统..."
    
    PID=$(get_flask_pid)
    
    if [ -z "$PID" ]; then
        log_warn "系统未在运行!"
        return
    fi
    
    kill $PID
    log_info "系统已停止运行。"
}

# 重启应用
restart_app() {
    show_title
    log_info "正在重启系统..."
    
    stop_app
    sleep 2
    start_app
}

# 显示使用说明
show_usage() {
    echo "使用方法: $0 {start|stop|restart|status}"
    echo "  start   - 启动服务"
    echo "  stop    - 停止服务"
    echo "  restart - 重启服务"
    echo "  status  - 显示服务状态"
}

# 显示状态
show_status() {
    show_title
    
    PID=$(get_flask_pid)
    
    if [ -z "$PID" ]; then
        log_info "系统状态: 未运行"
    else
        log_info "系统状态: 运行中 (PID: $PID)"
        log_info "运行时间: $(ps -o etime= -p $PID)"
    fi
}

# 主函数
main() {
    case "$1" in
        start)
            start_app
            ;;
        stop)
            stop_app
            ;;
        restart)
            restart_app
            ;;
        status)
            show_status
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 