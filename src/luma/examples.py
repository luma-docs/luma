def fib(n: int) -> int:
    """Calculate the nth Fibonacci number.

    Args:
        n: The index of the Fibonacci number to calculate.

    Returns:
        The nth Fibonacci number.

    Raises:
        ValueError: If n is less than 0.

    Examples:
        >>> fib(0)
        0
        >>> fib(1)
        1
        >>> fib(2)
        1
        >>> fib(3)
        2
        >>> fib(4)
        3
    """
    if n < 0:
        raise ValueError("n must be greater than or equal to 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# Base class representing a general account
class Account:
    def __init__(self, account_holder: str, balance: float = 0.0):
        self.account_holder = account_holder  # Name of the account holder
        self.balance = balance  # Initial balance (default 0.0)

    def deposit(self, amount: float) -> None:
        """Deposit money into the account."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        print(f"Deposited {amount}. New balance: {self.balance}")

    def withdraw(self, amount: float) -> None:
        """Withdraw money from the account."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        print(f"Withdrew {amount}. New balance: {self.balance}")

    def get_balance(self) -> float:
        """Return the current balance."""
        return self.balance

    def __str__(self) -> str:
        """String representation of the account."""
        return f"Account holder: {self.account_holder}, Balance: {self.balance}"


# Derived class representing a savings account (inherits from Account)
class SavingsAccount(Account):
    def __init__(
        self, account_holder: str, balance: float = 0.0, interest_rate: float = 0.02
    ):
        super().__init__(account_holder, balance)  # Call the base class constructor
        self.interest_rate = interest_rate  # Interest rate for the savings account

    def apply_interest(self) -> None:
        """Apply interest to the balance."""
        interest = self.balance * self.interest_rate
        self.balance += interest
        print(f"Applied interest of {interest}. New balance: {self.balance}")


# Derived class representing a checking account (inherits from Account)
class CheckingAccount(Account):
    def __init__(
        self, account_holder: str, balance: float = 0.0, overdraft_limit: float = 500.0
    ):
        super().__init__(account_holder, balance)
        self.overdraft_limit = (
            overdraft_limit  # Overdraft limit for the checking account
        )

    def withdraw(self, amount: float) -> None:
        """Withdraw money, considering overdraft limit."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self.balance + self.overdraft_limit < amount:
            raise ValueError("Insufficient funds, including overdraft limit")
        self.balance -= amount
        print(f"Withdrew {amount}. New balance: {self.balance}")
