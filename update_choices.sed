s/\(order\.id, f"{order\.id}\) - \({order\.student_name} - {order\.subject}"\)/\1, f"{order.order_number} - \2/g
s/\(order\.id, f"{order\.id}\) - \({order\.teacher_name} - {order\.subject}"\)/\1, f"{order.order_number} - \2/g
