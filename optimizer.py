import re

class ASTNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def to_dict(self):
        if self.left is None and self.right is None:
            return {"type": "number" if self.value.isdigit() else "identifier", "value": self.value}
        return {
            "type": self.value,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }

def tokenize(expr):
    return re.findall(r'\d+|[a-zA-Z]+|[+*/=\-()]', expr)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def parse(self):
        if '=' in self.tokens:
            idx = self.tokens.index('=')
            var = self.tokens[0]
            self.pos = idx + 1
            expr = self.parse_expression()
            return ASTNode('=', ASTNode(var), expr)
        else:
            return self.parse_expression()

    def parse_expression(self):
        node = self.parse_term()
        while self.peek() in ['+', '-']:
            op = self.consume()
            right = self.parse_term()
            node = ASTNode(op, node, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek() in ['*', '/']:
            op = self.consume()
            right = self.parse_factor()
            node = ASTNode(op, node, right)
        return node

    def parse_factor(self):
        tok = self.peek()
        if tok == '(':
            self.consume()
            node = self.parse_expression()
            if self.peek() == ')':
                self.consume()
            return node
        else:
            return ASTNode(self.consume())



def is_constant(node):
    return node and node.left is None and node.right is None and node.value.isdigit()

def fold_constants(node, steps):
    if node is None:
        return None

    node.left = fold_constants(node.left, steps)
    node.right = fold_constants(node.right, steps)

    if is_constant(node.left) and is_constant(node.right):
        l = int(node.left.value)
        r = int(node.right.value)
        result = None

        if node.value == '+': result = l + r
        elif node.value == '-': result = l - r
        elif node.value == '*': result = l * r
        elif node.value == '/': result = l // r if r != 0 else 0

        if result is not None:
            steps.append(f"{l} {node.value} {r} = {result}")
            return ASTNode(str(result))

    return node



def optimize_expression(expr):
    tokens = tokenize(expr)
    parser = Parser(tokens)
    ast = parser.parse()
    steps = []
    optimized_ast = fold_constants(ast, steps)
    return optimized_ast, steps
