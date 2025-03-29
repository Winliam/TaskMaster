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
    
    // Order dropdown change - Fill form with order details
    const orderSelects = document.querySelectorAll('.order-select');
    
    orderSelects.forEach(select => {
        select.addEventListener('change', function() {
            const orderId = this.value;
            const formId = this.closest('form').id;
            
            if (orderId) {
                fetch(`/get_order_details/${orderId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Fill form based on the form type
                        if (formId === 'class-record-form') {
                            document.getElementById('student_name').value = data.student_name;
                            document.getElementById('subject').value = data.subject;
                            document.getElementById('semester').value = data.semester;
                            document.getElementById('teacher_name').value = data.teacher_name;
                        } else if (formId === 'payment-form') {
                            document.getElementById('student_name').value = data.student_name;
                            document.getElementById('subject').value = data.subject;
                            document.getElementById('semester').value = data.semester;
                        } else if (formId === 'salary-form') {
                            document.getElementById('teacher_name').value = data.teacher_name;
                            document.getElementById('subject').value = data.subject;
                            document.getElementById('semester').value = data.semester;
                            // Set max salary amount to remaining salary
                            document.getElementById('salary_amount').max = data.remaining_salary;
                        }
                    })
                    .catch(error => console.error('Error:', error));
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
    
    // Setup edit note buttons
    function setupEditNoteButtons() {
        const editNoteButtons = document.querySelectorAll('.edit-note');
        
        editNoteButtons.forEach(button => {
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
    
    // Call this on page load to set up any existing edit note buttons
    setupEditNoteButtons();
    
    // Order checkboxes for sum calculation
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
                }),
            })
            .then(response => response.json())
            .then(data => {
                // Populate and show the sum results modal
                const sumResultsModal = new bootstrap.Modal(document.getElementById('sumResultsModal'));
                
                if (data.view_type === 'student') {
                    document.getElementById('sum-student-names').textContent = data.student_names.join('、');
                    document.getElementById('sum-subjects').textContent = data.subjects.join('、');
                    document.getElementById('sum-semesters').textContent = data.semesters.join('、');
                    document.getElementById('sum-total-paid').textContent = data.total_paid.toFixed(2);
                    document.getElementById('sum-total-used').textContent = data.total_used.toFixed(2);
                    document.getElementById('sum-total-remaining').textContent = data.total_remaining.toFixed(2);
                    
                    document.getElementById('student-sum-section').style.display = 'block';
                    document.getElementById('teacher-sum-section').style.display = 'none';
                } else {
                    document.getElementById('sum-teacher-names').textContent = data.teacher_names.join('、');
                    document.getElementById('sum-teacher-subjects').textContent = data.subjects.join('、');
                    document.getElementById('sum-teacher-semesters').textContent = data.semesters.join('、');
                    document.getElementById('sum-total-payable').textContent = data.total_payable.toFixed(2);
                    document.getElementById('sum-total-paid-salary').textContent = data.total_paid.toFixed(2);
                    document.getElementById('sum-total-remaining-salary').textContent = data.total_remaining.toFixed(2);
                    
                    document.getElementById('student-sum-section').style.display = 'none';
                    document.getElementById('teacher-sum-section').style.display = 'block';
                }
                
                sumResultsModal.show();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('计算失败，请重试');
            });
        });
    }
    
    // Select all checkboxes
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const orderCheckboxes = document.querySelectorAll('.order-checkbox');
            orderCheckboxes.forEach(cb => {
                cb.checked = selectAllCheckbox.checked;
            });
        });
    }
});
