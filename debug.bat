@echo off
echo 滋兰科技医学临床科研专病数据平台 - 调试模式

REM 激活虚拟环境
if exist venv\Scripts\activate.bat (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo 虚拟环境不存在，请先运行install.bat
    pause > nul
    exit /b 1
)

REM 设置调试环境变量
echo 设置调试环境变量...
set FLASK_ENV=development
set FLASK_DEBUG=1
set FLASK_APP=app.py
set PYTHONDONTWRITEBYTECODE=1
set FLASK_RUN_PORT=6000
set FLASK_RUN_HOST=127.0.0.1

REM 检查端口是否被占用
echo 检查端口是否被占用...
netstat -ano | findstr :6000 > nul
if %ERRORLEVEL% EQU 0 (
    echo 警告: 端口6000已被占用，尝试使用备用端口7000...
    set FLASK_RUN_PORT=7000
)

echo 启动应用（调试模式）...
echo 使用端口: %FLASK_RUN_PORT%
python app.py

if %ERRORLEVEL% NEQ 0 (
    echo 应用启动失败! 错误代码: %ERRORLEVEL%
    echo 尝试通过flask命令启动...
    flask run --host=0.0.0.0 --port=%FLASK_RUN_PORT% --debug
)

pause 