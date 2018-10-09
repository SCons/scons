class TestLiteral(object):
    def __init__(self, literal):
        self.literal = literal

    def __str__(self):
        return self.literal

    def is_literal(self):
        return 1