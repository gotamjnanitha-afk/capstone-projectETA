from submitted import calculate_average

def test_normal_list():
    assert calculate_average([80, 90, 70]) == 80

def test_two_values():
    assert calculate_average([10, 20]) == 15

def test_empty_list():
    assert calculate_average([]) == 0
