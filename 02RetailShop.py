def retail_billing():
    total_amount = 0
    items = []

    print("Retail Shop Billing System")
    print()

    while True:
        name = input("\nEnter item name: ")
        price = float(input("Enter item price: "))
        quantity = int(input("Enter quantity: "))

        item_total = price * quantity
        total_amount += item_total

        items.append((name, price, quantity, item_total))

        more = input("Add more items? (y/n): ").lower()
        if more != 'y':
            break

    
    print("BILL")
    print()
    print(f"{'Item':<15}{'Price':<10}{'Qty':<5}{'Total':<10}")
    print("-" * 40)

    for item in items:
        print(f"{item[0]:<15}{item[1]:<10}{item[2]:<5}{item[3]:<10}")

    print("-" * 40)
    print(f"Total Amount: ₹{total_amount}")

    
    if total_amount > 1000:
        discount = total_amount * 0.1
        total_amount -= discount
        print(f"Discount Applied (10%): ₹{discount}")

    print(f"Final Amount to Pay: ₹{total_amount}")



retail_billing()