a = int(input("enter your first number : "))

def EveOdd(x):
   if x%2 == 0:
      print("the entered number is even")
   else: 
      print("the entered number is odd")
   return x

def PassOrFail(x):
   if x<35 and x>=0 :
      print("the person is fail")
   elif x>=35 and x<=100 :
      print("the person is pass")

def main():
  EveOdd(a)
  PassOrFail(a)

main()