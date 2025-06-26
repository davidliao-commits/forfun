import ast
import sys

class FunctionCallChecker(ast.NodeVisitor):
    def __init__(self):
        self.func_defs = {}  # Function name -> expected number of args
        self.errors = []

    def visit_FunctionDef(self, node):
        # Skip methods starting with underscores (optional)
        if node.name.startswith("_"):
            return
        
        arg_count = len([
            arg for arg in node.args.args
            if arg.arg != "self"  # exclude `self` for class methods
        ])
        self.func_defs[node.name] = arg_count
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.func_defs:
                actual_args = len(node.args)
                expected_args = self.func_defs[func_name]
                if actual_args != expected_args:
                    self.errors.append(
                        f"[Line {node.lineno}] Function '{func_name}' called with {actual_args} argument(s), but defined with {expected_args}."
                    )
        self.generic_visit(node)

def analyze_ast(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=filename)
    checker = FunctionCallChecker()
    checker.visit(tree)
    return checker.errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ast_function_checker.py <python_file_to_analyze.py>")
        sys.exit(1)

    target_file = sys.argv[1]
    results = analyze_ast(target_file)
    if not results:
        print("✅ No function call mismatches found.")
    else:
        print("❌ Function call mismatches detected:")
        for err in results:
            print(err)
