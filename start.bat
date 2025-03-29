@echo off
echo 正在启动精致培优教务管理系统...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python安装，请安装Python 3.7或更高版本。
    pause
    exit /b 1
)

REM 设置环境变量
set SESSION_SECRET=very-secure-session-key
set DATABASE_URL=sqlite:///education_management.db

REM 检查是否已安装必要的包
echo 正在检查依赖项...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装必要的依赖项...
    pip install flask flask-sqlalchemy flask-login flask-wtf email_validator
)

REM 启动应用
echo 启动应用服务器...
start "" python main.py

REM 等待服务器启动
timeout /t 2 >nul

REM 打开浏览器
echo 正在打开浏览器...
start "" http://localhost:5000

echo.
echo 系统已启动！请在浏览器中使用系统。
echo 初始登录信息: 用户名=admin，密码=admin
echo.
echo 按任意键关闭此窗口将会终止应用服务器...
pause >nul
taskkill /f /im python.exe >nul 2>&1
