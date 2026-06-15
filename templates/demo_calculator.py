"""
Demo Calculator Program
A simple calculator to demonstrate the IDE Compiler Manager
"""

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b

def main():
    print("="*50)
    print("Simple Calculator")
    print("="*50)
    print()
    
    while True:
        print("\nOperations:")
        print("1. Add")
        print("2. Subtract")
        print("3. Multiply")
        print("4. Divide")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ")
        
        if choice == '5':
            print("\nThank you for using Calculator!")
            break
        
        if choice not in ['1', '2', '3', '4']:
            print("Invalid choice! Please try again.")
            continue
        
        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
            
            if choice == '1':
                result = add(num1, num2)
                print(f"\nResult: {num1} + {num2} = {result}")
            elif choice == '2':
                result = subtract(num1, num2)
                print(f"\nResult: {num1} - {num2} = {result}")
            elif choice == '3':
                result = multiply(num1, num2)
                print(f"\nResult: {num1} × {num2} = {result}")
            elif choice == '4':
                result = divide(num1, num2)
                print(f"\nResult: {num1} ÷ {num2} = {result}")
        
        except ValueError:
            print("\nError: Please enter valid numbers!")
        except Exception as e:
            print(f"\nError: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()

# Made with Bob
