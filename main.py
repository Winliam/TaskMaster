import logging
from app import app
from create_admin import create_default_admin

# 设置日志
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # 创建管理员账户
    create_default_admin()
    # 运行应用
    app.run(host="0.0.0.0", port=5000, debug=True)
