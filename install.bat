@echo off
echo 滋兰科技医学临床科研专病数据平台 - 安装脚本

REM 检查Python是否已安装
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python未安装，请先安装Python 3.8或更高版本
    echo 可以从 https://www.python.org/downloads/ 下载
    echo 按任意键退出...
    pause > nul
    exit /b 1
)

echo Python已安装，继续安装过程...

REM 创建虚拟环境
if exist venv (
    echo 虚拟环境已存在，是否重新创建? (Y/N)
    set /p recreate=
    if /i "%recreate%"=="Y" (
        echo 删除现有虚拟环境...
        rmdir /s /q venv
        echo 创建新的虚拟环境...
        python -m venv venv
    )
) else (
    echo 创建虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖...
pip install -r requirements.txt

REM 创建必要的目录
if not exist uploads (
    mkdir uploads
    echo 创建uploads目录成功
)
if not exist static (
    mkdir static
    mkdir static\css
    mkdir static\js
    mkdir static\images
    echo 创建static目录成功
)

REM 创建默认的.env文件
echo 是否创建默认的.env文件? (Y/N)
set /p createenv=
if /i "%createenv%"=="Y" (
    echo SECRET_KEY=zl-geniusmedvault-secret-key > .env
    echo DATABASE_URI=sqlite:///zl_geniusmedvault.db >> .env
    echo UPLOAD_FOLDER=uploads >> .env
    echo 创建默认.env文件成功
)

echo ======================================
echo 安装完成!
echo 可以通过运行run.bat启动应用
echo ======================================

echo 按任意键退出...
pause > nul 