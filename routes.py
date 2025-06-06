from flask import render_template, url_for, flash, redirect, request, jsonify, send_file, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import app, db
from models import User, Order, ClassRecord, PaymentRecord, SalaryRecord
from forms import LoginForm, OrderForm, ClassRecordForm, PaymentRecordForm, SalaryRecordForm, EditNoteForm
from datetime import datetime, timedelta
import json
import io
import csv
from sqlalchemy import func, desc, asc, and_, or_


# Login routes
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password_hash,
                                        form.password.data):
            login_user(user, remember=True)
            app.logger.info(f"用户登录成功: {user.username}")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(
                url_for('dashboard'))
        else:
            app.logger.warning(f"登录失败: 用户名={form.username.data}")
            flash('登录失败，请检查用户名和密码！', 'danger')

    return render_template('login.html', title='登录', form=form)


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        username = current_user.username
        logout_user()
        app.logger.info(f"用户登出: {username}")
        flash('您已成功退出！', 'info')
    return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # 获取本周内的上课记录
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    this_week_classes = ClassRecord.query.filter(
        ClassRecord.class_time >= start_of_week, ClassRecord.class_time
        <= end_of_week + timedelta(days=1)).order_by(
            ClassRecord.class_time).all()

    # 获取本周内的新订单
    this_week_orders = Order.query.filter(
        Order.created_at >= start_of_week, Order.created_at <= end_of_week +
        timedelta(days=1)).order_by(Order.created_at.desc()).all()

    # 获取待支付订单（剩余金额大于0）
    pending_payments = Order.query.filter(Order.remaining_amount > 0).all()

    # 获取待发放工资（剩余工资大于0）
    pending_salaries = Order.query.filter(Order.remaining_salary > 0).all()

    # Forms for modals
    order_form = OrderForm()
    class_record_form = ClassRecordForm()
    payment_record_form = PaymentRecordForm()
    salary_record_form = SalaryRecordForm()

    # Populate order dropdown for class records, payments, and salaries
    orders = Order.query.all()
    class_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in orders
    ]
    payment_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in orders
    ]
    salary_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.teacher_name} - {order.subject}")
        for order in orders
    ]

    return render_template('dashboard.html',
                           title='首页',
                           this_week_classes=this_week_classes,
                           this_week_orders=this_week_orders,
                           pending_payments=pending_payments,
                           pending_salaries=pending_salaries,
                           order_form=order_form,
                           class_record_form=class_record_form,
                           payment_record_form=payment_record_form,
                           salary_record_form=salary_record_form,
                           edit_note_form=EditNoteForm())


# Order list view
@app.route('/orders')
@login_required
def order_list():
    # Get all orders
    orders = Order.query.order_by(Order.created_at.desc()).all()

    # Forms for modals
    order_form = OrderForm()
    class_record_form = ClassRecordForm()
    payment_record_form = PaymentRecordForm()
    salary_record_form = SalaryRecordForm()

    # Populate order dropdown for class records, payments, and salaries
    orders_for_dropdown = Order.query.all()
    class_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in orders_for_dropdown
    ]
    payment_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in orders_for_dropdown
    ]
    salary_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.teacher_name} - {order.subject}")
        for order in orders_for_dropdown
    ]

    return render_template('order_list.html',
                           title='订单列表',
                           orders=orders,
                           order_form=order_form,
                           class_record_form=class_record_form,
                           payment_record_form=payment_record_form,
                           salary_record_form=salary_record_form,
                           edit_note_form=EditNoteForm())


@app.route('/order/create', methods=['POST'])
@login_required
def create_order():
    form = OrderForm()

    if form.validate_on_submit():
        # Calculate total price
        total_price = form.total_classes.data * form.class_price.data

        # 生成订单号
        order_number = Order.generate_order_number(form.student_name.data,
                                                   form.subject.data)

        # Create new order
        new_order = Order(
            order_number=order_number,
            student_name=form.student_name.data,
            subject=form.subject.data,
            teacher_name=form.teacher_name.data,
            semester=form.semester.data,
            total_classes=form.total_classes.data,
            remaining_classes=form.total_classes.data,
            class_price=form.class_price.data,
            salary_price=form.salary_price.data,
            total_price=total_price,
            remaining_amount=0,  # 初始剩余费用为0（已缴费用-已用费用）
            payable_amount=total_price,  # 初始应缴费用等于订单总价（订单总价-已缴费用）
            payable_salary=0,  # Will be updated as classes are completed
            order_note=form.order_note.data)

        db.session.add(new_order)
        db.session.commit()

        flash(f'订单创建成功！订单号：{order_number}', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(request.referrer or url_for('order_list'))


@app.route('/search_orders')
@login_required
def search_orders():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    # Search for orders matching the query
    orders = Order.query.filter(
        Order.order_number.ilike(f'%{query}%')
        | Order.student_name.ilike(f'%{query}%')
        | Order.subject.ilike(f'%{query}%')).limit(10).all()

    # Format the results
    results = [{
        'id':
        order.id,
        'text':
        f"{order.order_number} - {order.student_name} - {order.subject}"
    } for order in orders]

    return jsonify(results)


@app.route('/get_order_details/<int:order_id>')
@login_required
def get_order_details(order_id):
    order = Order.query.get_or_404(order_id)

    return jsonify({
        'student_name': order.student_name,
        'subject': order.subject,
        'semester': order.semester,
        'teacher_name': order.teacher_name,
        'remaining_classes': order.remaining_classes,
        'class_price': order.class_price,
        'salary_price': order.salary_price,
        'remaining_amount': order.remaining_amount,
        'payable_salary': order.payable_salary,
        'paid_salary': order.paid_salary,
        'remaining_salary': order.remaining_salary
    })


# Class record routes
@app.route('/class_record/create', methods=['POST'])
@login_required
def create_class_record():
    form = ClassRecordForm()
    form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in Order.query.all()
    ]

    if form.validate_on_submit():
        order = Order.query.get_or_404(form.order_id.data)

        # Check if there are remaining classes
        if order.remaining_classes <= 0:
            flash('该订单已无剩余课程！', 'danger')
            return redirect(request.referrer or url_for('dashboard'))

        # Create new class record
        new_class_record = ClassRecord(order_id=order.id,
                                       student_name=order.student_name,
                                       subject=order.subject,
                                       semester=order.semester,
                                       teacher_name=order.teacher_name,
                                       class_content=form.class_content.data,
                                       class_time=form.class_time.data,
                                       location=form.location.data,
                                       note=form.note.data)

        # Update order data
        order.completed_classes += 1
        order.remaining_classes -= 1

        # Update financial data
        used_class_cost = order.class_price
        order.used_amount += used_class_cost
        order.remaining_amount = order.paid_amount - order.used_amount

        # Update teacher salary using the salary price field
        class_salary = order.salary_price
        order.payable_salary += class_salary
        order.remaining_salary = order.payable_salary - order.paid_salary

        db.session.add(new_class_record)
        db.session.commit()

        flash('上课记录添加成功！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(request.referrer or url_for('dashboard'))


# Payment record routes
@app.route('/payment/create', methods=['POST'])
@login_required
def create_payment():
    form = PaymentRecordForm()
    form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in Order.query.all()
    ]

    if form.validate_on_submit():
        order = Order.query.get_or_404(form.order_id.data)

        # Create new payment record
        new_payment = PaymentRecord(order_id=order.id,
                                    student_name=order.student_name,
                                    subject=order.subject,
                                    semester=order.semester,
                                    payment_amount=form.payment_amount.data,
                                    payment_time=form.payment_time.data,
                                    payment_method=form.payment_method.data,
                                    note=form.note.data)

        # Update order financial data
        order.paid_amount += form.payment_amount.data
        order.remaining_amount = order.paid_amount - order.used_amount
        order.payable_amount = order.total_price - order.paid_amount

        db.session.add(new_payment)
        db.session.commit()

        flash('缴费记录添加成功！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(request.referrer or url_for('dashboard'))


# Salary record routes
@app.route('/salary/create', methods=['POST'])
@login_required
def create_salary():
    form = SalaryRecordForm()
    form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.teacher_name} - {order.subject}")
        for order in Order.query.all()
    ]

    if form.validate_on_submit():
        order = Order.query.get_or_404(form.order_id.data)

        # Check if the amount doesn't exceed the payable amount
        if form.salary_amount.data > order.payable_salary - order.paid_salary:
            flash('发放金额不能超过待发工资！', 'danger')
            return redirect(request.referrer or url_for('dashboard'))

        # Create new salary record
        new_salary = SalaryRecord(order_id=order.id,
                                  teacher_name=order.teacher_name,
                                  subject=order.subject,
                                  semester=order.semester,
                                  salary_amount=form.salary_amount.data,
                                  payment_time=form.payment_time.data,
                                  note=form.note.data)

        # Update order salary data
        order.paid_salary += form.salary_amount.data
        order.remaining_salary = order.payable_salary - order.paid_salary

        db.session.add(new_salary)
        db.session.commit()

        flash('工资发放记录添加成功！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(request.referrer or url_for('dashboard'))


# Student view
@app.route('/student_view')
@login_required
def student_view():
    # Get filter parameters
    student_name = request.args.get('student_name', '')
    subject = request.args.get('subject', '')
    semester = request.args.get('semester', '')

    # Query orders with filters
    query = Order.query

    if student_name:
        query = query.filter(Order.student_name == student_name)
    if subject:
        query = query.filter(Order.subject == subject)
    if semester:
        query = query.filter(Order.semester == semester)

    orders = query.all()

    # Get unique values for filters
    all_students = db.session.query(Order.student_name).distinct().all()
    all_subjects = db.session.query(Order.subject).distinct().all()
    all_semesters = db.session.query(Order.semester).distinct().all()

    # Forms for modals
    order_form = OrderForm()
    class_record_form = ClassRecordForm()
    payment_record_form = PaymentRecordForm()
    salary_record_form = SalaryRecordForm()

    # Populate order dropdown for class records, payments, and salaries
    all_orders = Order.query.all()
    class_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    payment_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    salary_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.teacher_name} - {order.subject}")
        for order in all_orders
    ]

    return render_template(
        'student_view.html',
        title='学生视图',
        orders=orders,
        all_students=[student[0] for student in all_students],
        all_subjects=[subject[0] for subject in all_subjects],
        all_semesters=[semester[0] for semester in all_semesters],
        selected_student=student_name,
        selected_subject=subject,
        selected_semester=semester,
        edit_note_form=EditNoteForm(),
        order_form=order_form,
        class_record_form=class_record_form,
        payment_record_form=payment_record_form,
        salary_record_form=salary_record_form)


# Teacher view
@app.route('/teacher_view')
@login_required
def teacher_view():
    # Get filter parameters
    teacher_name = request.args.get('teacher_name', '')
    subject = request.args.get('subject', '')
    semester = request.args.get('semester', '')

    # Query orders with filters
    query = Order.query

    if teacher_name:
        query = query.filter(Order.teacher_name == teacher_name)
    if subject:
        query = query.filter(Order.subject == subject)
    if semester:
        query = query.filter(Order.semester == semester)

    orders = query.all()

    # Get unique values for filters
    all_teachers = db.session.query(Order.teacher_name).distinct().all()
    all_subjects = db.session.query(Order.subject).distinct().all()
    all_semesters = db.session.query(Order.semester).distinct().all()

    # Forms for modals
    order_form = OrderForm()
    class_record_form = ClassRecordForm()
    payment_record_form = PaymentRecordForm()
    salary_record_form = SalaryRecordForm()

    # Populate order dropdown for class records, payments, and salaries
    all_orders = Order.query.all()
    class_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    payment_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    salary_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.teacher_name} - {order.subject}")
        for order in all_orders
    ]

    return render_template(
        'teacher_view.html',
        title='教师视图',
        orders=orders,
        all_teachers=[teacher[0] for teacher in all_teachers],
        all_subjects=[subject[0] for subject in all_subjects],
        all_semesters=[semester[0] for semester in all_semesters],
        selected_teacher=teacher_name,
        selected_subject=subject,
        selected_semester=semester,
        edit_note_form=EditNoteForm(),
        order_form=order_form,
        class_record_form=class_record_form,
        payment_record_form=payment_record_form,
        salary_record_form=salary_record_form)


# Get class records for an order
@app.route('/get_class_records/<int:order_id>')
@login_required
def get_class_records(order_id):
    order = Order.query.get_or_404(order_id)
    class_records = ClassRecord.query.filter_by(order_id=order_id).order_by(
        ClassRecord.class_time.desc()).all()

    records_data = []
    for record in class_records:
        records_data.append({
            'id':
            record.id,
            'class_time':
            record.class_time.strftime('%Y-%m-%d %H:%M'),
            'location':
            record.location,
            'class_content':
            record.class_content,
            'note':
            record.note
        })

    return jsonify({
        'order_id': order.id,
        'student_name': order.student_name,
        'subject': order.subject,
        'semester': order.semester,
        'teacher_name': order.teacher_name,
        'records': records_data
    })


# Update notes
@app.route('/update_note', methods=['POST'])
@login_required
def update_note():
    form = EditNoteForm()

    if form.validate_on_submit():
        note_id = form.note_id.data
        note_type = form.note_type.data
        note_text = form.note_text.data

        if note_type == 'order_note':
            order = Order.query.get_or_404(note_id)
            order.order_note = note_text
        elif note_type == 'student_note':
            order = Order.query.get_or_404(note_id)
            order.student_note = note_text
        elif note_type == 'teacher_note':
            order = Order.query.get_or_404(note_id)
            order.teacher_note = note_text
        elif note_type == 'class_note':
            record = ClassRecord.query.get_or_404(note_id)
            record.note = note_text
        elif note_type == 'payment_note':
            record = PaymentRecord.query.get_or_404(note_id)
            record.note = note_text
        elif note_type == 'salary_note':
            record = SalaryRecord.query.get_or_404(note_id)
            record.note = note_text

        db.session.commit()
        flash('备注更新成功！', 'success')
    else:
        flash('备注更新失败！', 'danger')

    return redirect(request.referrer)


# Export class records to CSV
@app.route('/export_class_records/<int:order_id>')
@login_required
def export_class_records(order_id):
    order = Order.query.get_or_404(order_id)
    class_records = ClassRecord.query.filter_by(order_id=order_id).order_by(
        ClassRecord.class_time).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        ['订单编号', '学生姓名', '科目', '学期', '教师姓名', '上课时间', '上课地点', '教学内容', '备注'])

    # Write data
    for record in class_records:
        writer.writerow([
            order.id, record.student_name, record.subject, record.semester,
            record.teacher_name,
            record.class_time.strftime('%Y-%m-%d %H:%M'), record.location,
            record.class_content, record.note
        ])

    # Prepare response
    output.seek(0)
    filename = f"上课记录_{order.student_name}_{order.subject}_{datetime.now().strftime('%Y%m%d')}.csv"

    return send_file(io.BytesIO(output.getvalue().encode('utf-8-sig')),
                     download_name=filename,
                     as_attachment=True,
                     mimetype='text/csv')


# Class records list view
@app.route('/class_records')
@login_required
def class_records_list():
    # Get filter parameters
    student_name = request.args.get('student_name', '')
    teacher_name = request.args.get('teacher_name', '')
    subject = request.args.get('subject', '')
    semester = request.args.get('semester', '')

    # Query class records with filters
    query = ClassRecord.query

    if student_name:
        query = query.filter(ClassRecord.student_name == student_name)
    if teacher_name:
        query = query.filter(ClassRecord.teacher_name == teacher_name)
    if subject:
        query = query.filter(ClassRecord.subject == subject)
    if semester:
        query = query.filter(ClassRecord.semester == semester)

    class_records = query.order_by(ClassRecord.class_time.desc()).all()

    # Get unique values for filters
    all_students = db.session.query(ClassRecord.student_name).distinct().all()
    all_teachers = db.session.query(ClassRecord.teacher_name).distinct().all()
    all_subjects = db.session.query(ClassRecord.subject).distinct().all()
    all_semesters = db.session.query(ClassRecord.semester).distinct().all()

    # Forms for modals
    order_form = OrderForm()
    class_record_form = ClassRecordForm()
    payment_record_form = PaymentRecordForm()
    salary_record_form = SalaryRecordForm()

    # Populate order dropdown for class records, payments, and salaries
    all_orders = Order.query.all()
    class_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    payment_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    salary_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.teacher_name} - {order.subject}")
        for order in all_orders
    ]

    return render_template(
        'class_records_list.html',
        title='上课记录',
        class_records=class_records,
        all_students=[student[0] for student in all_students],
        all_teachers=[teacher[0] for teacher in all_teachers],
        all_subjects=[subject[0] for subject in all_subjects],
        all_semesters=[semester[0] for semester in all_semesters],
        selected_student=student_name,
        selected_teacher=teacher_name,
        selected_subject=subject,
        selected_semester=semester,
        edit_note_form=EditNoteForm(),
        order_form=order_form,
        class_record_form=class_record_form,
        payment_record_form=payment_record_form,
        salary_record_form=salary_record_form)


# Payment records list view
@app.route('/payment_records')
@login_required
def payment_records_list():
    # Get filter parameters
    student_name = request.args.get('student_name', '')
    subject = request.args.get('subject', '')
    semester = request.args.get('semester', '')

    # Query payment records with filters
    query = PaymentRecord.query

    if student_name:
        query = query.filter(PaymentRecord.student_name == student_name)
    if subject:
        query = query.filter(PaymentRecord.subject == subject)
    if semester:
        query = query.filter(PaymentRecord.semester == semester)

    payment_records = query.order_by(PaymentRecord.payment_time.desc()).all()

    # Get unique values for filters
    all_students = db.session.query(
        PaymentRecord.student_name).distinct().all()
    all_subjects = db.session.query(PaymentRecord.subject).distinct().all()
    all_semesters = db.session.query(PaymentRecord.semester).distinct().all()

    # Forms for modals
    order_form = OrderForm()
    class_record_form = ClassRecordForm()
    payment_record_form = PaymentRecordForm()
    salary_record_form = SalaryRecordForm()

    # Populate order dropdown for class records, payments, and salaries
    all_orders = Order.query.all()
    class_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    payment_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    salary_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.teacher_name} - {order.subject}")
        for order in all_orders
    ]

    return render_template(
        'payment_records_list.html',
        title='缴费记录',
        payment_records=payment_records,
        all_students=[student[0] for student in all_students],
        all_subjects=[subject[0] for subject in all_subjects],
        all_semesters=[semester[0] for semester in all_semesters],
        selected_student=student_name,
        selected_subject=subject,
        selected_semester=semester,
        edit_note_form=EditNoteForm(),
        order_form=order_form,
        class_record_form=class_record_form,
        payment_record_form=payment_record_form,
        salary_record_form=salary_record_form)


# Salary records list view
@app.route('/salary_records')
@login_required
def salary_records_list():
    # Get filter parameters
    teacher_name = request.args.get('teacher_name', '')
    subject = request.args.get('subject', '')
    semester = request.args.get('semester', '')

    # Query salary records with filters
    query = SalaryRecord.query

    if teacher_name:
        query = query.filter(SalaryRecord.teacher_name == teacher_name)
    if subject:
        query = query.filter(SalaryRecord.subject == subject)
    if semester:
        query = query.filter(SalaryRecord.semester == semester)

    salary_records = query.order_by(SalaryRecord.payment_time.desc()).all()

    # Get unique values for filters
    all_teachers = db.session.query(SalaryRecord.teacher_name).distinct().all()
    all_subjects = db.session.query(SalaryRecord.subject).distinct().all()
    all_semesters = db.session.query(SalaryRecord.semester).distinct().all()

    # Forms for modals
    order_form = OrderForm()
    class_record_form = ClassRecordForm()
    payment_record_form = PaymentRecordForm()
    salary_record_form = SalaryRecordForm()

    # Populate order dropdown for class records, payments, and salaries
    all_orders = Order.query.all()
    class_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    payment_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    salary_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.teacher_name} - {order.subject}")
        for order in all_orders
    ]

    return render_template(
        'salary_records_list.html',
        title='工资发放记录',
        salary_records=salary_records,
        all_teachers=[teacher[0] for teacher in all_teachers],
        all_subjects=[subject[0] for subject in all_subjects],
        all_semesters=[semester[0] for semester in all_semesters],
        selected_teacher=teacher_name,
        selected_subject=subject,
        selected_semester=semester,
        edit_note_form=EditNoteForm(),
        order_form=order_form,
        class_record_form=class_record_form,
        payment_record_form=payment_record_form,
        salary_record_form=salary_record_form)


# Financial report
@app.route('/financial_report')
@login_required
def financial_report():
    # Get filter parameters
    subject = request.args.get('subject', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # Convert date strings to datetime objects if provided
    if date_from:
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
    else:
        date_from = datetime(2000, 1, 1)  # Default start date

    if date_to:
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
        date_to = date_to.replace(hour=23, minute=59,
                                  second=59)  # End of the day
    else:
        date_to = datetime.now()  # Default end date

    # Query orders with filters
    query = Order.query.filter(Order.created_at.between(date_from, date_to))

    if subject:
        query = query.filter(Order.subject == subject)

    orders = query.all()

    # Calculate totals
    total_price = sum(order.total_price for order in orders)
    total_paid = sum(order.paid_amount for order in orders)
    total_used = sum(order.used_amount for order in orders)
    total_payable_salary = sum(order.payable_salary for order in orders)
    total_paid_salary = sum(order.paid_salary for order in orders)
    total_remaining_salary = sum(order.remaining_salary for order in orders)

    # Calculate profits
    gross_profit = total_price - total_payable_salary
    net_profit = total_paid - total_paid_salary
    current_balance = total_paid - total_paid_salary

    # Group by subject for statistics
    subject_stats = []
    subjects = db.session.query(Order.subject).distinct().all()

    for subject_tuple in subjects:
        subject_name = subject_tuple[0]
        subject_orders = [
            order for order in orders if order.subject == subject_name
        ]

        if not subject_orders:
            continue

        subject_total_price = sum(order.total_price
                                  for order in subject_orders)
        subject_paid_amount = sum(order.paid_amount
                                  for order in subject_orders)
        subject_payable_salary = sum(order.payable_salary
                                     for order in subject_orders)
        subject_paid_salary = sum(order.paid_salary
                                  for order in subject_orders)
        subject_gross_profit = subject_total_price - subject_payable_salary

        # Calculate profit rate
        if subject_total_price > 0:
            profit_rate = (subject_gross_profit / subject_total_price) * 100
        else:
            profit_rate = 0

        subject_stats.append({
            'subject': subject_name,
            'total_price': subject_total_price,
            'paid_amount': subject_paid_amount,
            'payable_salary': subject_payable_salary,
            'paid_salary': subject_paid_salary,
            'gross_profit': subject_gross_profit,
            'profit_rate': profit_rate
        })

    # 按利润率排序
    subject_stats = sorted(subject_stats,
                           key=lambda x: x['profit_rate'],
                           reverse=True)

    # 创建表单实例，以便在模板中使用
    order_form = OrderForm()
    class_record_form = ClassRecordForm()
    payment_record_form = PaymentRecordForm()
    salary_record_form = SalaryRecordForm()

    # 为下拉菜单添加选项
    all_orders = Order.query.all()
    class_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    payment_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.student_name} - {order.subject}")
        for order in all_orders
    ]
    salary_record_form.order_id.choices = [
        (order.id,
         f"{order.order_number} - {order.teacher_name} - {order.subject}")
        for order in all_orders
    ]

    return render_template('financial_report.html',
                           title='财务报表',
                           today=datetime.now(),
                           total_price=total_price,
                           total_paid=total_paid,
                           total_used=total_used,
                           total_payable_salary=total_payable_salary,
                           total_paid_salary=total_paid_salary,
                           total_remaining_salary=total_remaining_salary,
                           gross_profit=gross_profit,
                           net_profit=net_profit,
                           current_balance=current_balance,
                           subject_stats=subject_stats,
                           order_form=order_form,
                           class_record_form=class_record_form,
                           payment_record_form=payment_record_form,
                           salary_record_form=salary_record_form,
                           edit_note_form=EditNoteForm())


# 删除订单
@app.route('/check_order_dependencies/<int:order_id>')
@login_required
def check_order_dependencies(order_id):
    order = Order.query.get_or_404(order_id)

    dependencies = {
        'has_dependencies': False,
        'class_records': len(order.class_records) > 0,
        'payment_records': len(order.payment_records) > 0,
        'salary_records': len(order.salary_records) > 0
    }

    dependencies['has_dependencies'] = any([
        dependencies['class_records'], dependencies['payment_records'],
        dependencies['salary_records']
    ])

    return jsonify(dependencies)


@app.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)

    # 检查是否有关联记录
    if order.class_records or order.payment_records or order.salary_records:
        return jsonify({'success': False, 'message': '该订单存在关联记录，无法删除！'})

    # 删除订单
    try:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'success': True, 'message': '订单删除成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})


# 删除上课记录
@app.route('/delete_class_record/<int:record_id>', methods=['POST'])
@login_required
def delete_class_record(record_id):
    record = ClassRecord.query.get_or_404(record_id)
    order = Order.query.get(record.order_id)

    if order:
        # 更新订单数据
        order.completed_classes -= 1
        order.remaining_classes += 1

        # 更新财务数据
        used_class_cost = order.class_price
        order.used_amount -= used_class_cost
        order.remaining_amount = order.paid_amount - order.used_amount

        # 更新教师工资
        class_salary = order.salary_price
        order.payable_salary -= class_salary
        order.remaining_salary = order.payable_salary - order.paid_salary

    # 删除记录
    db.session.delete(record)
    db.session.commit()

    flash('上课记录删除成功！', 'success')
    return redirect(request.referrer or url_for('class_records_list'))


# 删除缴费记录
@app.route('/delete_payment_record/<int:record_id>', methods=['POST'])
@login_required
def delete_payment_record(record_id):
    record = PaymentRecord.query.get_or_404(record_id)
    order = Order.query.get(record.order_id)

    if order:
        # 更新订单财务数据
        order.paid_amount -= record.payment_amount
        order.remaining_amount = order.paid_amount - order.used_amount
        order.payable_amount = order.total_price - order.paid_amount

    # 删除记录
    db.session.delete(record)
    db.session.commit()

    flash('缴费记录删除成功！', 'success')
    return redirect(request.referrer or url_for('payment_records_list'))


# 删除工资发放记录
@app.route('/delete_salary_record/<int:record_id>', methods=['POST'])
@login_required
def delete_salary_record(record_id):
    record = SalaryRecord.query.get_or_404(record_id)
    order = Order.query.get(record.order_id)

    if order:
        # 更新订单工资数据
        order.paid_salary -= record.salary_amount
        order.remaining_salary = order.payable_salary - order.paid_salary

    # 删除记录
    db.session.delete(record)
    db.session.commit()

    flash('工资发放记录删除成功！', 'success')
    return redirect(request.referrer or url_for('salary_records_list'))


# Calculate sum of selected orders
@app.route('/calculate_sum', methods=['POST'])
@login_required
def calculate_sum():
    order_numbers = request.json.get('order_numbers', []) # Added this line
    view_type = request.json.get('view_type', 'student')

    if not order_numbers: # Modified this line
        return jsonify({'error': 'No orders selected'}), 400

    if order_numbers: # Added this conditional block
        orders = Order.query.filter(Order.order_number.in_(order_numbers)).all()

    if view_type == 'student':
        # Calculate student view sums
        total_paid = sum(order.paid_amount for order in orders)
        total_used = sum(order.used_amount for order in orders)
        total_remaining = sum(order.remaining_amount for order in orders)
        total_payable = sum(order.total_price - order.paid_amount
                            for order in orders)

        # Get unique values
        student_names = set(order.student_name for order in orders)
        subjects = set(order.subject for order in orders)
        semesters = set(order.semester for order in orders)

        return jsonify({
            'view_type': 'student',
            'total_paid': total_paid,
            'total_used': total_used,
            'total_remaining': total_remaining,
            'total_payable': total_payable,
            'student_names': list(student_names),
            'subjects': list(subjects),
            'semesters': list(semesters),
            'order_numbers': order_numbers # Changed to order_numbers
        })
    else:
        # Calculate teacher view sums
        total_payable = sum(order.payable_salary for order in orders)
        total_paid = sum(order.paid_salary for order in orders)
        total_remaining = sum(order.remaining_salary for order in orders)

        # Get unique values
        teacher_names = set(order.teacher_name for order in orders)
        subjects = set(order.subject for order in orders)
        semesters = set(order.semester for order in orders)

        return jsonify({
            'view_type': 'teacher',
            'total_payable': total_payable,
            'total_paid': total_paid,
            'total_remaining': total_remaining,
            'teacher_names': list(teacher_names),
            'subjects': list(subjects),
            'semesters': list(semesters),
            'order_numbers': order_numbers # Changed to order_numbers
        })