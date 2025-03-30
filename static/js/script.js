// Wait for the document to be ready
document.addEventListener('DOMContentLoaded', function() {
    // 全选复选框处理
    const selectAllCheckbox = document.getElementById('select-all-orders');
    const batchDeleteBtn = document.getElementById('batch-delete-btn');

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const orderCheckboxes = document.querySelectorAll('.order-checkbox');
            orderCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBatchDeleteButton();
        });
    }

    // 单个复选框变化时更新全选状态和删除按钮状态
    document.querySelectorAll('.order-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectAllCheckbox();
            updateBatchDeleteButton();
        });
    });

    // 批量删除按钮点击事件
    if (batchDeleteBtn) {
        batchDeleteBtn.addEventListener('click', function() {
            const selectedOrders = getSelectedOrders();
            if (selectedOrders.length === 0) {
                return;
            }

            // 验证是否可以删除
            fetch('/validate_batch_delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    order_ids: selectedOrders.map(order => order.id)
                })
            })
            .then(response => response.json())
            .then(data => {
                const validationMessageDiv = document.getElementById('delete-validation-message');
                const confirmationMessageDiv = document.getElementById('delete-confirmation-message');
                const confirmDeleteBtn = document.getElementById('confirm-batch-delete');

                if (data.has_records) {
                    // 有关联记录，显示错误信息
                    validationMessageDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <p>以下订单存在关联记录，无法删除：</p>
                            <ul>
                                ${data.orders_with_records.map(order => `
                                    <li>${order.order_number}
                                        ${order.has_class_records ? '<br>- 存在上课记录' : ''}
                                        ${order.has_payment_records ? '<br>- 存在缴费记录' : ''}
                                        ${order.has_salary_records ? '<br>- 存在工资记录' : ''}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>`;
                    confirmationMessageDiv.innerHTML = '';
                    confirmDeleteBtn.style.display = 'none';
                } else {
                    // 可以删除，显示确认信息
                    validationMessageDiv.innerHTML = '';
                    confirmationMessageDiv.innerHTML = `
                        <p>确定要删除以下订单吗？此操作不可恢复！</p>
                        <ul>
                            ${selectedOrders.map(order => `<li>${order.orderNumber}</li>`).join('')}
                        </ul>`;
                    confirmDeleteBtn.style.display = 'block';
                }

                const batchDeleteModal = new bootstrap.Modal(document.getElementById('batchDeleteModal'));
                batchDeleteModal.show();
            });
        });
    }

    // 辅助函数：获取选中的订单
    function getSelectedOrders() {
        const checkedBoxes = document.querySelectorAll('.order-checkbox:checked');
        return Array.from(checkedBoxes).map(checkbox => ({
            id: checkbox.value,
            orderNumber: checkbox.getAttribute('data-order-number')
        }));
    }

    // 辅助函数：更新全选复选框状态
    function updateSelectAllCheckbox() {
        const selectAll = document.getElementById('select-all-orders');
        const orderCheckboxes = document.querySelectorAll('.order-checkbox');
        const checkedBoxes = document.querySelectorAll('.order-checkbox:checked');
        
        if (selectAll) {
            selectAll.checked = orderCheckboxes.length > 0 && checkedBoxes.length === orderCheckboxes.length;
        }
    }

    // 辅助函数：更新批量删除按钮状态
    function updateBatchDeleteButton() {
        const checkedBoxes = document.querySelectorAll('.order-checkbox:checked');
        if (batchDeleteBtn) {
            batchDeleteBtn.disabled = checkedBoxes.length === 0;
        }
    }click', function() {
            const selectedOrders = getSelectedOrders();

            // 验证选中的订单是否可以删除
            fetch('/validate_batch_delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    order_ids: selectedOrders.map(order => order.id)
                })
            })
            .then(response => response.json())
            .then(data => {
                const validationMessageDiv = document.getElementById('delete-validation-message');
                const confirmationMessageDiv = document.getElementById('delete-confirmation-message');
                const confirmDeleteBtn = document.getElementById('confirm-batch-delete');

                if (data.has_records) {
                    // 有关联记录，显示错误信息
                    validationMessageDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <p>以下订单存在关联记录，无法删除：</p>
                            <ul>
                                ${data.orders_with_records.map(order => `
                                    <li>${order.order_number}
                                        ${order.has_class_records ? '<br>- 存在上课记录' : ''}
                                        ${order.has_payment_records ? '<br>- 存在缴费记录' : ''}
                                        ${order.has_salary_records ? '<br>- 存在工资记录' : ''}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>`;
                    confirmationMessageDiv.innerHTML = '';
                    confirmDeleteBtn.style.display = 'none';
                } else {
                    // 可以删除，显示确认信息
                    validationMessageDiv.innerHTML = '';
                    confirmationMessageDiv.innerHTML = `
                        <p>确定要删除以下订单吗？此操作不可恢复！</p>
                        <ul>
                            ${selectedOrders.map(order => `<li>${order.orderNumber}</li>`).join('')}
                        </ul>`;
                    confirmDeleteBtn.style.display = 'block';
                }

                const batchDeleteModal = new bootstrap.Modal(document.getElementById('batchDeleteModal'));
                batchDeleteModal.show();
            });
        });
    }

    // 确认批量删除按钮点击事件
    const confirmBatchDeleteBtn = document.getElementById('confirm-batch-delete');
    if (confirmBatchDeleteBtn) {
        confirmBatchDeleteBtn.addEventListener('click', function() {
            const selectedOrders = getSelectedOrders();

            fetch('/batch_delete_orders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    order_ids: selectedOrders.map(order => order.id)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('删除失败：' + data.message);
                }
            });
        });
    }

    // 辅助函数
    function updateSelectAllCheckbox() {
        const selectAllCheckbox = document.getElementById('select-all-orders');
        const orderCheckboxes = document.querySelectorAll('.order-checkbox');
        const checkedCheckboxes = document.querySelectorAll('.order-checkbox:checked');

        if (selectAllCheckbox) {
            selectAllCheckbox.checked = orderCheckboxes.length > 0 && 
                                      orderCheckboxes.length === checkedCheckboxes.length;
        }
    }

    function updateBatchDeleteButton() {
        const checkedCheckboxes = document.querySelectorAll('.order-checkbox:checked');
        if (batchDeleteBtn) {
            batchDeleteBtn.disabled = checkedCheckboxes.length === 0;
        }
    }

    function getSelectedOrders() {
        const selectedOrders = [];
        document.querySelectorAll('.order-checkbox:checked').forEach(checkbox => {
            selectedOrders.push({
                id: checkbox.value,
                orderNumber: checkbox.getAttribute('data-order-number')
            });
        });
        return selectedOrders;
    }

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

    // 为全选复选框添加事件监听 (原代码中已存在，此处保留并与新代码整合)
    const selectAllCheckbox2 = document.getElementById('select-all');
    if (selectAllCheckbox2) {
        selectAllCheckbox2.addEventListener('change', function() {
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
            const orderIds = Array.from(checkedOrders).map(cb => parseInt(cb.value));
            const viewType = document.body.getAttribute('data-view-type');

            if (orderIds.length === 0) {
                alert('请至少选择一个订单');
                return;
            }

            fetch('/calculate_sum', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    order_ids: orderIds,
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
                    document.getElementById('sum-order-numbers').textContent = data.order_ids.join('\n');
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
                    document.getElementById('sum-teacher-order-numbers').textContent = data.order_ids.join('\n');
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
});