from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, IntegerField, DateTimeLocalField, HiddenField, SelectField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class OrderForm(FlaskForm):
    student_name = StringField('学生姓名', validators=[DataRequired()])
    subject = StringField('科目', validators=[DataRequired()])
    teacher_name = StringField('教师姓名', validators=[DataRequired()])
    semester = StringField('学期', validators=[DataRequired()])
    total_classes = IntegerField('总课程数', validators=[DataRequired(), NumberRange(min=1)])
    class_price = FloatField('课程单价', validators=[DataRequired(), NumberRange(min=0)])
    order_note = TextAreaField('订单备注', validators=[Optional()])
    submit = SubmitField('保存')

class ClassRecordForm(FlaskForm):
    order_id = SelectField('订单编号', validators=[DataRequired()], coerce=int)
    student_name = StringField('学生姓名', render_kw={'readonly': True})
    subject = StringField('科目', render_kw={'readonly': True})
    semester = StringField('学期', render_kw={'readonly': True})
    teacher_name = StringField('教师姓名', render_kw={'readonly': True})
    class_content = TextAreaField('教学内容', validators=[Optional()])
    class_time = DateTimeLocalField('上课时间', format='%Y-%m-%dT%H:%M', validators=[DataRequired()], default=datetime.now)
    location = StringField('地点', validators=[DataRequired()])
    note = TextAreaField('备注', validators=[Optional()])
    submit = SubmitField('保存')

class PaymentRecordForm(FlaskForm):
    order_id = SelectField('订单编号', validators=[DataRequired()], coerce=int)
    student_name = StringField('学生姓名', render_kw={'readonly': True})
    subject = StringField('科目', render_kw={'readonly': True})
    semester = StringField('学期', render_kw={'readonly': True})
    payment_amount = FloatField('缴费金额', validators=[DataRequired(), NumberRange(min=0.01)])
    payment_time = DateTimeLocalField('缴费时间', format='%Y-%m-%dT%H:%M', validators=[DataRequired()], default=datetime.now)
    payment_method = StringField('缴费方式', validators=[Optional()])
    note = TextAreaField('备注', validators=[Optional()])
    submit = SubmitField('保存')

class SalaryRecordForm(FlaskForm):
    order_id = SelectField('订单编号', validators=[DataRequired()], coerce=int)
    teacher_name = StringField('教师姓名', render_kw={'readonly': True})
    subject = StringField('科目', render_kw={'readonly': True})
    semester = StringField('学期', render_kw={'readonly': True})
    salary_amount = FloatField('发放金额', validators=[DataRequired(), NumberRange(min=0.01)])
    payment_time = DateTimeLocalField('发放时间', format='%Y-%m-%dT%H:%M', validators=[DataRequired()], default=datetime.now)
    note = TextAreaField('备注', validators=[Optional()])
    submit = SubmitField('保存')

class EditNoteForm(FlaskForm):
    note_id = HiddenField('ID')
    note_type = HiddenField('类型')
    note_text = TextAreaField('备注', validators=[Optional()])
    submit = SubmitField('保存')
