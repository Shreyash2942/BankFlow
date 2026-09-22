"""
ATM Simulation
CSC505 - Principles of Software Engineering

This program follows the numbered activities in the UML Activity Diagram.
It demonstrates PIN authentication, failed-attempt counting, withdrawal
validation, balance updates, account closure, and session completion.
"""

CORRECT_PIN = "2468"
MAX_ATTEMPTS = 3
STARTING_BALANCE = 500.00


def print_step(number, message):
    """Print a numbered activity that matches the UML Activity Diagram."""
    print(f"{number}. {message}")


def authenticate_customer():
    """Authenticate the customer using a PIN with a maximum of three attempts."""
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        print_step(3, "Request PIN")
        print_step(4, "Enter PIN")
        entered_pin = input("   Enter your 4-digit PIN: ")

        print_step(5, "Validate PIN")

        if entered_pin == CORRECT_PIN:
            print("   PIN correct.")
            print_step(8, "Authenticate Customer")
            print("   Access granted.")
            return True

        attempts += 1
        print("   PIN incorrect.")
        print_step(6, "Increment Failed Attempt Counter")
        print(f"   Failed attempts: {attempts}/{MAX_ATTEMPTS}")

        if attempts >= MAX_ATTEMPTS:
            print_step(7, "Reject Customer")
            print("   Maximum PIN attempts reached. Card retained and access denied.")
            return False

        print("   Please try again.\n")

    return False


def request_withdrawal(balance):
    """Request and validate a withdrawal amount."""
    while True:
        print_step(9, "Request Withdrawal Amount")
        amount_text = input("   Enter withdrawal amount: $")

        try:
            amount = float(amount_text)
        except ValueError:
            print_step(10, "Validate Withdrawal Amount")
            print("   Invalid input. Please enter a numeric amount.\n")
            continue

        print_step(10, "Validate Withdrawal Amount")

        if amount <= 0:
            print("   Withdrawal amount must be greater than $0.\n")
            continue

        if amount > balance:
            print("   Insufficient funds.")
            print(f"   Available balance: ${balance:.2f}\n")
            continue

        return amount


def run_atm():
    """Run one complete ATM session."""
    balance = STARTING_BALANCE

    print("=" * 58)
    print("               ATM SYSTEM SIMULATION")
    print("=" * 58)

    print_step(1, "Start ATM Session")
    print_step(2, "Insert Card")
    print("   Card accepted.\n")

    authenticated = authenticate_customer()

    if not authenticated:
        print_step(16, "End ATM Session")
        print("   Session ended.")
        print("=" * 58)
        return

    print(f"\n   Current account balance: ${balance:.2f}\n")

    amount = request_withdrawal(balance)

    print_step(11, "Dispense Cash")
    print(f"   Cash dispensed: ${amount:.2f}")

    print_step(12, "Update Account Balance")
    balance -= amount
    print(f"   New balance: ${balance:.2f}")

    print_step(13, "Check Account Balance")

    if balance == 0:
        print("   Balance is $0.00.")
        print_step(14, "Close Account")
        print("   Account status: CLOSED")
    else:
        print(f"   Balance remaining: ${balance:.2f}")
        print_step(15, "Display Transaction Complete / Updated Balance")
        print("   Transaction completed successfully.")
        print(f"   Updated balance: ${balance:.2f}")
        print("   Account status: ACTIVE")

    print_step(16, "End ATM Session")
    print("   Please remove your card. Thank you.")
    print("=" * 58)


if __name__ == "__main__":
    run_atm()
