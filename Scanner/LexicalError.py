class LexicalError:
    def __init__(self, error, error_kind, lineno):
        self.error = error
        self.error_kind = error_kind
        self.lineno = lineno
