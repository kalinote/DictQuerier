from dictquerier.path.tokenizer.lexer import Lexer
from dictquerier.path.syntax_tree.parser import Parser

# FIXME 暂时还没办法解析 @random.randint(1, 10) 这种格式
test_str = 'root.items[("key" > 10 || "value" < @max(10, $var)) && "key" == "value"]."te\\"st"[\'index\'].value'

lexer = Lexer(test_str)
tokens = list(lexer.tokenize())

print("Token列表:")
for i, token in enumerate(tokens):
    print(f"{i}: {token}")

parser = Parser(tokens)
ast_root = parser.parse()

ast_root.print_ast(indent=4)
