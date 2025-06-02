chcp 65001
@echo off
echo -----------------------------------
echo  GeniusMedVault医学临床科研专病数据平台 (版权所有)
echo -----------------------------------
echo 正在启动系统...

:: 检查是否安装了Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python安装，请安装Python 3.7或更高版本并重试。
    pause
    exit /b 1
)

:: 检查是否有venv目录，如果没有则创建虚拟环境
if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
    echo 正在安装依赖...
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

:: 获取本机IP地址
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 地址" /c:"IPv4 Address"') do (
    set IP=%%a
    goto :break
)
:break
set IP=%IP:~1%

:: 启动Flask应用
echo 启动完成! 正在打开浏览器...
echo 其他设备可通过访问 http://%IP%:5000/login 连接到系统
start http://localhost:5000/login
flask run --host=0.0.0.0

pause 