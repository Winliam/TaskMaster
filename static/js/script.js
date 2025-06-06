// Wait for the document to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Order form - Calculate total price automatically
    const totalClassesInput = document.getElementById('total_classes');
    const classPriceInput = document.getElementById('class_price');
    const salaryPriceInput = document.getElementById('salary_price');
    const totalPriceDisplay = document.getElementById('total_price_display');

    function calculateTotalPrice() {
        if (totalClassesInput && classPriceInput && totalPriceDisplay) {
            const totalClasses = parseInt(totalClassesInput.value) || 0;
            const classPrice = parseFloat(classPriceInput.value) || 0;
            const totalPrice = totalClasses * classPrice;
            totalPriceDisplay.textContent = totalPrice.toFixed(2);

            // Set default salary price to 70% of class price if salary field exists
            if (salaryPriceInput && salaryPriceInput.value === "") {
                salaryPriceInput.value = (classPrice * 0.7).toFixed(2);
            }
        }
    }

    if (totalClassesInput && classPriceInput) {
        totalClassesInput.addEventListener('input', calculateTotalPrice);
        classPriceInput.addEventListener('input', calculateTotalPrice);
        if (salaryPriceInput) {
            salaryPriceInput.addEventListener('input', calculateTotalPrice);
        }
    }

    // 订单模糊搜索功能
    const orderSearchInputs = document.querySelectorAll('.order-search');

    orderSearchInputs.forEach(input => {
        const resultsContainer = input.parentElement.querySelector('.order-search-results');
        const hiddenSelect = input.parentElement.querySelector('select');

        input.addEventListener('input', function() {
            const query = this.value.trim();

            if (query.length < 2) {
                resultsContainer.style.display = 'none';
                return;
            }

            fetch(`/search_orders?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.length === 0) {
                        resultsContainer.innerHTML = '<div class="p-2 text-muted">无匹配结果</div>';
                    } else {
                        let html = '';
                        data.forEach(order => {
                            html += `<div class="p-2 order-result" data-id="${order.id}">${order.text}</div>`;
                        });
                        resultsContainer.innerHTML = html;

                        // 添加点击事件
                        const resultItems = resultsContainer.querySelectorAll('.order-result');
                        resultItems.forEach(item => {
                            item.addEventListener('click', function() {
                                const orderId = this.getAttribute('data-id');
                                const orderText = this.textContent;

                                // 设置输入框和隐藏的select值
                                input.value = orderText;
                                hiddenSelect.value = orderId;

                                // 触发订单详情加载
                                loadOrderDetails(orderId, input.closest('form').id);

                                // 隐藏结果容器
                                resultsContainer.style.display = 'none';
                            });
                        });
                    }

                    resultsContainer.style.display = 'block';
                })
                .catch(error => console.error('Error:', error));
        });

        // 点击外部时隐藏结果
        document.addEventListener('click', function(e) {
            if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
                resultsContainer.style.display = 'none';
            }
        });

        // 样式设置
        resultsContainer.style.cssText = 'position: absolute; z-index: 1000; background: #fff; border: 1px solid #ddd; border-radius: 4px; max-height: 200px; overflow-y: auto; width: 100%;';

        // 添加结果项的hover效果
        const style = document.createElement('style');
        style.textContent = `
            .order-result:hover {
                background-color: #f8f9fa;
                cursor: pointer;
            }
        `;
        document.head.appendChild(style);
    });

    // 加载订单详情函数
    function loadOrderDetails(orderId, formId) {
        if (orderId) {
            fetch(`/get_order_details/${orderId}`)
                .then(response => response.json())
                .then(data => {
                    // 根据表单类型填充数据
                    if (formId === 'class-record-form' || formId === 'newClassRecordModal') {
                        document.querySelector('#newClassRecordModal #student_name').value = data.student_name;
                        document.querySelector('#newClassRecordModal #subject').value = data.subject;
                        document.querySelector('#newClassRecordModal #semester').value = data.semester;
                        document.querySelector('#newClassRecordModal #teacher_name').value = data.teacher_name;
                    } else if (formId === 'payment-form' || formId === 'newPaymentModal') {
                        document.querySelector('#newPaymentModal #student_name').value = data.student_name;
                        document.querySelector('#newPaymentModal #subject').value = data.subject;
                        document.querySelector('#newPaymentModal #semester').value = data.semester;
                    } else if (formId === 'salary-form' || formId === 'newSalaryModal') {
                        document.querySelector('#newSalaryModal #teacher_name').value = data.teacher_name;
                        document.querySelector('#newSalaryModal #subject').value = data.subject;
                        document.querySelector('#newSalaryModal #semester').value = data.semester;
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    }

    // 兼容旧的下拉框选择方式 (如果有)
    const orderSelects = document.querySelectorAll('.order-select');

    orderSelects.forEach(select => {
        select.addEventListener('change', function() {
            const orderId = this.value;
            const formId = this.closest('form').id;

            if (orderId) {
                loadOrderDetails(orderId, formId);
            }
        });
    });

    // Class records modal - Load class records
    const classRecordButtons = document.querySelectorAll('.view-class-records');

    classRecordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const orderId = this.getAttribute('data-order-id');
            const recordsContainer = document.getElementById('class-records-container');
            const modalTitle = document.getElementById('classRecordsModalLabel');

            // Show loading
            recordsContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';

            fetch(`/get_class_records/${orderId}`)
                .then(response => response.json())
                .then(data => {
                    // Update modal title
                    modalTitle.textContent = `${data.student_name} - ${data.subject} - ${data.semester} 上课记录`;

                    // Build records table
                    let html = `
                        <div class="mb-3">
                            <a href="/export_class_records/${orderId}" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-download"></i> 导出CSV
                            </a>
                        </div>
                    `;

                    if (data.records.length === 0) {
                        html += '<div class="alert alert-info">暂无上课记录</div>';
                    } else {
                        html += `
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>上课时间</th>
                                            <th>地点</th>
                                            <th>教学内容</th>
                                            <th>备注</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                        `;

                        data.records.forEach(record => {
                            html += `
                                <tr>
                                    <td>${record.class_time}</td>
                                    <td>${record.location}</td>
                                    <td>${record.class_content || ''}</td>
                                    <td>
                                        <span class="note-text">${record.note || ''}</span>
                                        <button type="button" class="btn btn-sm btn-link edit-note" 
                                            data-bs-toggle="modal" data-bs-target="#editNoteModal"
                                            data-note-id="${record.id}" 
                                            data-note-type="class_note" 
                                            data-note-text="${record.note || ''}">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                    </td>
                                </tr>
                            `;
                        });

                        html += `
                                    </tbody>
                                </table>
                            </div>
                        `;
                    }

                    recordsContainer.innerHTML = html;

                    // Set up edit note buttons
                    setupEditNoteButtons();
                })
                .catch(error => {
                    console.error('Error:', error);
                    recordsContainer.innerHTML = '<div class="alert alert-danger">获取上课记录失败</div>';
                });
        });
    });

    // 设置编辑备注按钮的点击事件
    function setupEditNoteButtons() {
        document.querySelectorAll('.edit-note').forEach(button => {
            button.addEventListener('click', function() {
                const noteId = this.getAttribute('data-note-id');
                const noteType = this.getAttribute('data-note-type');
                const noteText = this.getAttribute('data-note-text');

                document.getElementById('note_id').value = noteId;
                document.getElementById('note_type').value = noteType;
                document.getElementById('note_text').value = noteText;
            });
        });
    }

    // 为全选复选框添加事件监听
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            document.querySelectorAll('.order-checkbox').forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }

    // 设置计算汇总按钮的点击事件
    const calcSumButton = document.getElementById('calculate-sum');
    if (calcSumButton) {
        calcSumButton.addEventListener('click', function() {
            const checkedOrders = document.querySelectorAll('.order-checkbox:checked');
            const viewType = document.body.getAttribute('data-view-type');

            // 获取所有选中订单的完整订单号
            const orderNumbers = Array.from(checkedOrders).map(cb => {
                const row = cb.closest('tr');
                return row.querySelector('td:nth-child(2)').textContent.trim();
            });

            if (orderNumbers.length === 0) {
                alert('请至少选择一个订单');
                return;
            }
            fetch('/calculate_sum', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    order_numbers: orderNumbers,
                    view_type: viewType
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('计算汇总时发生错误');
                }
                return response.json();
            })
            .then(data => {
                const modal = new bootstrap.Modal(document.getElementById('sumResultsModal'));

                // 隐藏所有部分
                document.getElementById('student-sum-section').style.display = 'none';
                document.getElementById('teacher-sum-section').style.display = 'none';

                if (data.view_type === 'student') {
                    // 显示学生部分
                    document.getElementById('student-sum-section').style.display = 'block';

                    // 更新学生部分内容
                    document.getElementById('sum-order-numbers').textContent = data.order_numbers.join('\n');
                    document.getElementById('sum-student-names').textContent = data.student_names.join('\n');
                    document.getElementById('sum-subjects').textContent = data.subjects.join('\n');
                    document.getElementById('sum-semesters').textContent = data.semesters.join('\n');
                    document.getElementById('sum-total-paid').textContent = data.total_paid.toFixed(2);
                    document.getElementById('sum-total-used').textContent = data.total_used.toFixed(2);
                    document.getElementById('sum-total-remaining').textContent = data.total_remaining.toFixed(2);
                } else {
                    // 显示教师部分
                    document.getElementById('teacher-sum-section').style.display = 'block';

                    // 更新教师部分内容
                    document.getElementById('sum-teacher-order-numbers').textContent = data.order_numbers.join('\n');
                    document.getElementById('sum-teacher-names').textContent = data.teacher_names.join('\n');
                    document.getElementById('sum-teacher-subjects').textContent = data.subjects.join('\n');
                    document.getElementById('sum-teacher-semesters').textContent = data.semesters.join('\n');
                    document.getElementById('sum-teacher-total-payable').textContent = data.total_payable.toFixed(2);
                    document.getElementById('sum-teacher-total-paid').textContent = data.total_paid.toFixed(2);
                    document.getElementById('sum-teacher-total-remaining').textContent = data.total_remaining.toFixed(2);
                }

                modal.show();
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message);
            });
        });
    }

    // 页面加载时设置编辑备注按钮
    setupEditNoteButtons();

    // 删除订单按钮点击事件
    const deleteButtons = document.querySelectorAll('.delete-order');
    deleteButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const orderId = this.getAttribute('data-order-id');
            const orderNumber = this.getAttribute('data-order-number');
            const studentName = this.getAttribute('data-student-name');

            // 先检查订单依赖关系
            try {
                const response = await fetch(`/check_order_dependencies/${orderId}`);
                const data = await response.json();

                if (data.has_dependencies) {
                    let message = '该订单存在以下关联记录，无法删除：\n';
                    if (data.class_records) message += '- 上课记录\n';
                    if (data.payment_records) message += '- 缴费记录\n';
                    if (data.salary_records) message += '- 工资发放记录\n';
                    alert(message);
                    return;
                }

                // 如果没有依赖，显示确认对话框
                if (confirm(`确定要删除以下订单吗？\n订单号：${orderNumber}\n学生：${studentName}`)) {
                    const deleteResponse = await fetch(`/delete_order/${orderId}`, {
                        method: 'POST'
                    });
                    const deleteResult = await deleteResponse.json();

                    alert(deleteResult.message);
                    if (deleteResult.success) {
                        window.location.reload();
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                alert('操作失败，请稍后重试');
            }
        });
    });

    // 删除缴费记录按钮点击事件
    const deletePaymentButtons = document.querySelectorAll('.delete-payment-record');
    deletePaymentButtons.forEach(button => {
        button.addEventListener('click', function() {
            const recordId = this.getAttribute('data-record-id');
            const studentName = this.getAttribute('data-student-name');
            const paymentAmount = this.getAttribute('data-payment-amount');
            const paymentTime = this.getAttribute('data-payment-time');

            if (confirm(`确定要删除以下缴费记录吗？\n学生：${studentName}\n缴费金额：¥${paymentAmount}\n缴费时间：${paymentTime}\n\n注意：删除缴费记录将同时更新订单的已缴费金额和剩余金额等数据。`)) {
                const form = document.getElementById(`delete-payment-record-form-${recordId}`);
                if (form) {
                    form.submit();
                }
            }
        });
    });
});