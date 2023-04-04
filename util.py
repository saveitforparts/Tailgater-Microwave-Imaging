def send_dish_command(dish, command, value):
    for char in command.encode():
        dish.write(bytes([char]))
    dish.write(b' ')
    value = str(value)
    for char in value.encode():
        dish.write(bytes([char]))
    dish.write(b'\r')

# Prompt for scan parameters, with default values and valid range checks
def input_with_range_check(prompt, default, min_val, max_val):
    value = int(input(prompt) or default)
    value = max(min_val, min(value, max_val))
    if value != int(default):
        print(f"Value out of range, setting to {value}")
    return value