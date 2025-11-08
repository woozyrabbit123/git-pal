import ast
from typing import Set, Union

class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports: Set[Union[ast.Import, ast.ImportFrom]] = set()
    def visit_Import(self, node: ast.Import) -> None:
        self.imports.add(node)
        self.generic_visit(node)
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.imports.add(node)
        self.generic_visit(node)

def get_imports(source_code: str) -> Set[str]:
    try:
        tree = ast.parse(source_code)
        v = ImportVisitor()
        v.visit(tree)
        return {ast.unparse(n) for n in v.imports}
    except Exception:
        return set()

def merge_python_imports(base: str, ours: str, theirs: str) -> str:
    merged = set()
    for block in (get_imports(base), get_imports(ours), get_imports(theirs)):
        merged.update(block)
    return "\n".join(sorted(merged))
