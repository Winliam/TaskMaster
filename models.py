from app import db
from flask_login import UserMixin
from datetime import datetime
import re
import pypinyin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50),
                             unique=True,
                             nullable=False,
                             default="")
    student_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    teacher_name = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(100), nullable=False)
    total_classes = db.Column(db.Integer, default=0)
    completed_classes = db.Column(db.Integer, default=0)
    remaining_classes = db.Column(db.Integer, default=0)
    class_price = db.Column(db.Float, default=0.0)
    salary_price = db.Column(db.Float, default=0.0)  # 新增工资单价字段
    total_price = db.Column(db.Float, default=0.0)
    paid_amount = db.Column(db.Float, default=0.0)
    used_amount = db.Column(db.Float, default=0.0)
    remaining_amount = db.Column(db.Float, default=0.0)  # 已缴费用 - 已销费用
    payable_amount = db.Column(db.Float, default=0.0)  # 订单总价 - 已缴费用
    payable_salary = db.Column(db.Float, default=0.0)
    paid_salary = db.Column(db.Float, default=0.0)
    remaining_salary = db.Column(db.Float, default=0.0)
    order_note = db.Column(db.Text, nullable=True)
    teacher_note = db.Column(db.Text, nullable=True)
    student_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    class_records = db.relationship('ClassRecord', backref='order', lazy=True)
    payment_records = db.relationship('PaymentRecord',
                                      backref='order',
                                      lazy=True)
    salary_records = db.relationship('SalaryRecord',
                                     backref='order',
                                     lazy=True)

    @staticmethod
    def generate_order_number(student_name, subject):
        """生成订单号：日期-学生简称-科目简称-递增序号
        格式：YYMMDD-XXX-YYY-NNNN，例如：250329-YYX-MATH-0001
        """
        now = datetime.now()
        date_part = now.strftime("%y%m%d")

        # 学生简称：取英文名或中文拼音首字母
        if re.search(r'[\u4e00-\u9fa5]', student_name):  # 包含中文字符
            # 获取中文拼音首字母
            first_letters = pypinyin.lazy_pinyin(student_name,
                                                 style=pypinyin.FIRST_LETTER)
            student_part = ''.join(first_letters)
        else:
            # 英文名取首字母或首几个字母
            student_part = ''.join([c for c in student_name if c.isalpha()])

        student_part = student_part[:3].upper()

        # 科目简称：科目名称前4个字母，大写
        if re.search(r'[\u4e00-\u9fa5]', subject):  # 包含中文字符
            # 获取中文拼音首字母
            first_letters = pypinyin.lazy_pinyin(subject,
                                                 style=pypinyin.FIRST_LETTER)
            subject_part = ''.join(first_letters)
        else:
            # 英文科目取首字母或首几个字母
            subject_part = ''.join([c for c in subject if c.isalpha()])

        subject_part = subject_part[:4].upper()

        # 设置一个基础序号
        base_num = 1

        # 查找今天已有的该学生该科目的订单
        today_start = datetime.combine(now.date(), datetime.min.time())
        existing_orders = Order.query.filter(
            Order.created_at >= today_start,
            # Order.student_name == student_name,
            # Order.subject == subject
        ).all()

        # 如果已有订单，则序号递增
        if existing_orders:
            base_num += len(existing_orders)

        # 格式化为四位数字
        number_part = f"{base_num:04d}"

        return f"{date_part}-{student_part}-{subject_part}-{number_part}"


class ClassRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(100), nullable=False)
    teacher_name = db.Column(db.String(100), nullable=False)
    class_content = db.Column(db.Text, nullable=True)
    class_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    location = db.Column(db.String(100), nullable=False)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)


class PaymentRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(100), nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    payment_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    payment_method = db.Column(db.String(100), nullable=True)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)


class SalaryRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    teacher_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(100), nullable=False)
    salary_amount = db.Column(db.Float, nullable=False)
    payment_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
