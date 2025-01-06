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


class Account:
    """Base class representing a bank account.

    Examples:
        >>> account = Account("Alice", 100.0)
        >>> account.deposit(50.0)
        Deposited 50.0. New balance: 150.0
        >>> account.withdraw(20.0)
        Withdrew 20.0. New balance: 130.0
        >>> account.get_balance()
        130.0
    """

    def __init__(self, account_holder: str, balance: float = 0.0):
        """Initialize the account with an account holder and an optional balance.

        Args:
            account_holder: The name of the account holder.
            balance: The initial balance of the account (default 0.0).
        """
        self.account_holder = account_holder  # Name of the account holder
        self.balance = balance  # Initial balance (default 0.0)

    def deposit(self, amount: float) -> None:
        """Deposit money into the account.

        Args:
            amount: The amount to deposit.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        print(f"Deposited {amount}. New balance: {self.balance}")

    def withdraw(self, amount: float) -> None:
        """Withdraw money from the account.

        Args:
            amount: The amount to withdraw.
        """
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
