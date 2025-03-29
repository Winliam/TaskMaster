import logging
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

# 设置日志
logging.basicConfig(level=logging.INFO)

def create_default_admin():
    with app.app_context():
        # 检查是否已存在admin用户
        if User.query.filter_by(username='admin').first() is None:
            # 创建admin用户
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin')
            )
            db.session.add(admin_user)
            db.session.commit()
            logging.info("Default admin user created")
        else:
            logging.info("Admin user already exists")

if __name__ == "__main__":
    create_default_admin()