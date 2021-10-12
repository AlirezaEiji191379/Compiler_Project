class Token:
    def __init__(self, token_kind, value, lineno):
        self.token_kind = token_kind
        self.value = value
        self.lineno = lineno
