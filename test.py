def handle_salesman():
    sales_man = []
    total = 0
    x = ['first', 'second', 'third', 'fourth']
    for i in range(0, 4):
        sales_week = int(input(f"Enter your sales of your {x[i]} week:"))

        total += sales_week
    print(f"The total sales for this month is: {total}")

    sales_man.append(f"total sales: {total}")

    if total < 50000:
        commision = 0
    else:
        commision = total * 5 / 100

    sales_man.append(f"commision: {commision}")

    if total >= 80000:
        remarks = "Excellent"
    elif 80000 > total >= 60000:
        remarks = "Good"
    elif 60000 > total >= 40000:
        remarks = "Average"
    else:
        remarks = "Work Hard"

    sales_man.append(f"Remarks: {remarks}")

    print(f"This is your data for the month: {sales_man}")


handle_salesman()

