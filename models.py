from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    teacher_name = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(100), nullable=False)
    total_classes = db.Column(db.Integer, default=0)
    completed_classes = db.Column(db.Integer, default=0)
    remaining_classes = db.Column(db.Integer, default=0)
    class_price = db.Column(db.Float, default=0.0)
    total_price = db.Column(db.Float, default=0.0)
    paid_amount = db.Column(db.Float, default=0.0)
    used_amount = db.Column(db.Float, default=0.0)
    remaining_amount = db.Column(db.Float, default=0.0)
    payable_salary = db.Column(db.Float, default=0.0)
    paid_salary = db.Column(db.Float, default=0.0)
    remaining_salary = db.Column(db.Float, default=0.0)
    order_note = db.Column(db.Text, nullable=True)
    teacher_note = db.Column(db.Text, nullable=True)
    student_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    class_records = db.relationship('ClassRecord', backref='order', lazy=True)
    payment_records = db.relationship('PaymentRecord', backref='order', lazy=True)
    salary_records = db.relationship('SalaryRecord', backref='order', lazy=True)

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
