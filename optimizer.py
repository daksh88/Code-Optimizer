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



def parse_expression(expr):
    tokens = tokenize(expr)
    parser = Parser(tokens)
    return parser.parse()

def optimize_expression(expr):
    tokens = tokenize(expr)
    parser = Parser(tokens)
    ast = parser.parse()
    steps = []
    optimized_ast = fold_constants(ast, steps)
    return optimized_ast, steps

class Optimizer:
    def __init__(self):
        self.variables = {}
        self.steps = []

    def evaluate_node(self, node, step_trace=True):
        if node is None:
            return None

        # If it's a leaf node (number or variable)
        if node.left is None and node.right is None:
            if node.value.isdigit():
                return int(node.value)
            # If it's a variable, show the substitution step
            if node.value in self.variables and step_trace:
                self.steps.append(f"Substitute {node.value} = {self.variables[node.value]}")
                return self.variables[node.value]
            return None

        # Evaluate left and right subtrees
        left_val = self.evaluate_node(node.left, step_trace)
        right_val = self.evaluate_node(node.right, step_trace)

        if left_val is None or right_val is None:
            return None

        # Show the intermediate calculation step
        result = None
        if node.value == '+': 
            result = left_val + right_val
            if step_trace:
                self.steps.append(f"{left_val} + {right_val} = {result}")
        elif node.value == '-': 
            result = left_val - right_val
            if step_trace:
                self.steps.append(f"{left_val} - {right_val} = {result}")
        elif node.value == '*': 
            result = left_val * right_val
            if step_trace:
                self.steps.append(f"{left_val} × {right_val} = {result}")
        elif node.value == '/': 
            if right_val != 0:
                result = left_val // right_val
                if step_trace:
                    self.steps.append(f"{left_val} ÷ {right_val} = {result}")
            else:
                return None

        return result

    def optimize_line(self, expr):
        tokens = tokenize(expr.strip().rstrip(';'))
        parser = Parser(tokens)
        ast = parser.parse()

        if ast.value == '=':
            var_name = ast.left.value
            self.steps.append(f"Evaluating: {var_name} = {expr[expr.index('=')+1:].strip()}")
            
            # First try evaluating with variables
            result = self.evaluate_node(ast.right)
            
            if result is not None:
                self.variables[var_name] = result
                self.steps.append(f"Final: {var_name} = {result}")
            else:
                # Try constant folding if variable evaluation failed
                optimized_right, fold_steps = optimize_expression(tokens[2:])
                if fold_steps:
                    self.steps.extend(fold_steps)
                    result = int(fold_steps[-1].split('=')[1].strip())
                    self.variables[var_name] = result
                    self.steps.append(f"Final: {var_name} = {result}")

        return ast

def optimize_multiple_lines(code):
    optimizer = Optimizer()
    asts = []
    results = []
    
    # Split code into lines and process each line
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    
    for line in lines:
        ast = optimizer.optimize_line(line)
        asts.append(ast)
        
    return {
        "asts": [ast.to_dict() for ast in asts],
        "steps": optimizer.steps,
        "variables": optimizer.variables
    }

# Make sure to export both functions
__all__ = ['optimize_multiple_lines', 'optimize_expression', 'parse_expression']
