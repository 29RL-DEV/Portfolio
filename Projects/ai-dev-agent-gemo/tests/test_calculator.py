from app.calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(10, 2) == 5

def test_divide_by_zero():
    # BUG intenționat — asta ar trebui să fie protejat
    assert divide(10, 0) == 0
