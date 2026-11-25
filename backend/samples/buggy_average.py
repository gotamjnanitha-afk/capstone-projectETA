def calculate_average(numbers):
    total = 0
    for i in range(len(numbers) + 1):  # Bug: index goes out of range
        total += numbers[i]
    average = total / len(numbers)  # Bug: empty list causes division by zero
    return average

marks = [80, 90, 70]
print("Average:", calculate_average(marks))
