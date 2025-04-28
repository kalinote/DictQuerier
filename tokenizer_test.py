from dictquerier.path.tokenizer.lexer import Lexer


lexer = Lexer('root.items["value">@not_registered(15, num=1, s="test")].sub_value')
tokens = lexer.tokenize()

for token in tokens:
    print(token)
