from mock import patch

class SomeClass:
    pass

@patch('__main__.SomeClass')
def function(a, b, c, mockClass):
    print("blaaaaaaaa")
    print(mockClass is SomeClass)

function(1, 2, 3)
