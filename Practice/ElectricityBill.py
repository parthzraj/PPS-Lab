def Fun1(unit, rate, subsidyP=0):
    bill = 0 
    subsidy=0
    if unit<=100:
        print("You dont need to pay bill")
        return unit, bill, subsidy
    
    bill = unit*rate
    subsidy = (subsidyP/100)*bill
    finalBill = bill - subsidy

    return unit, finalBill, subsidy

unit = float(input("Enter the unit consumed : "))
rate = float(input("Enter the rate of each unit : "))
subsidyPercentage = float(input("Enter the subsidy percentage : "))

unitConsumed, finalBills, SubsidyGiven = Fun1(unit, rate, subsidyPercentage)

print()       
print("Electricity Bill")
print("-"*30)
print(f"{'Units':<10}{'Rate':<10}{'Bill':<10}")
print("-"*30)
print(f"{unitConsumed:<10}{rate:<10}{finalBills:<10}")
print()
print(f"Subsidy Given : {SubsidyGiven}")
print()
