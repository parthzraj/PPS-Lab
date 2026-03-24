def calculate_bill(units, rate, subsidy_percent=0):
    if units <= 100:
        bill = 0
    else:
        bill = (units - 100) * rate

    
    subsidy_amount = (subsidy_percent / 100) * bill
    final_bill = bill - subsidy_amount

    return bill, subsidy_amount, final_bill


units = int(input("Enter electricity units consumed: "))
rate = float(input("Enter cost per unit: "))
subsidy = float(input("Enter subsidy percentage (0 if none): "))
print()


bill, subsidy_amount, final_bill = calculate_bill(units, rate, subsidy)


print("Electricity Bill ")
print()
print(f"Units Consumed: {units}")
print(f"Bill before subsidy: ₹{bill:.2f}")
print(f"Subsidy: ₹{subsidy_amount:.2f}")
print(f"Final Bill: ₹{final_bill:.2f}")