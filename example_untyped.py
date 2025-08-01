# Example untyped Python file for testing
# This file intentionally has no type annotations to demonstrate the MCP server

def calculate_total(items, tax_rate):
    """Calculate total price including tax."""
    subtotal = sum(item.price for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax

def filter_items(items, min_price):
    """Filter items by minimum price."""
    return [item for item in items if item.price >= min_price]

class Item:
    def __init__(self, name, price) -> None:
        self.name = name
        self.price = price
    
    def apply_discount(self, discount_percent):
        """Apply discount to item price."""
        self.price *= (1 - discount_percent / 100)
        return self.price

# Global variables
DEFAULT_TAX_RATE = 0.08
CURRENCY_SYMBOL = "$"

# Function with complex logic
def generate_receipt(items, tax_rate=None) -> str:
    """Generate a receipt for items."""
    if tax_rate is None:
        tax_rate = DEFAULT_TAX_RATE
    
    total = calculate_total(items, tax_rate)
    lines: list[str] = []
    
    for item in items:
        lines.append(f"{item.name}: {CURRENCY_SYMBOL}{item.price:.2f}")
    
    lines.append(f"Tax ({tax_rate*100}%): {CURRENCY_SYMBOL}{total - sum(item.price for item in items):.2f}")
    lines.append(f"Total: {CURRENCY_SYMBOL}{total:.2f}")
    
    return "\n".join(lines)
