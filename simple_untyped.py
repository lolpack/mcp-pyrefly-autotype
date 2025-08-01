def add(a: int, b: int):
    return a + b

def multiply(x: int, y: int):
    result = x * y
    return result

def process_data(items: list[bool | float | int | str]):
    output = []
    for item in items:
        if isinstance(item, int):
            output.append(item * 2)
        else:
            output.append(str(item))
    return output

name = "test"
age = 25
numbers = [1, 2, 3, 4, 5]

result = add(10, 20)
product = multiply(5, 6)
processed = process_data([1, "hello", 3.14, True])
