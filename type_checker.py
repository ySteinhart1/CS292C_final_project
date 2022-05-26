from z3 import *
import inspect
import ast
from typing import *

#int - 0
#string - 1
#bool - 2

param_constraints = dict()
out_of_consideration = set()
symbolic_vars = dict()
solver = Solver()


class MyZ3Solver():
    def solve(self, func):
        global param_constraints
        global out_of_consideration

        sig = inspect.signature(func)
        param_names = sig.parameters.keys()
        
        param_constraints = dict()
        out_of_consideration = set() 

        for i in param_names:
            param_constraints[i] = []
            symbolic_vars[i] = Int(i)
        symbolic_vars['return'] = Int('return')
        src = inspect.getsource(func)
        func_ast = ast.parse(src)
        # print(ast.dump(func_ast))

        global solver

        visitor().visit(func_ast)
        for i in param_constraints:
            for c in param_constraints[i]:
                cons = []
                for j, ty in enumerate((int, str, bool)):
                    if c in dir(ty):
                        cons.append(symbolic_vars[i] == j)
                solver.add(Or(cons))
                        
                
        print(solver)
        s = solver.check()
        if(s == z3.sat):
            for i in param_names:
                int_type = solver.model()[symbolic_vars[i]]
                if int_type == 0:
                    str_type = int
                elif int_type == 1:
                    str_type = str
                else:
                    str_type = bool
                print(i,'has type', str_type)
            int_type = solver.model()[symbolic_vars['return']]
            if int_type == 0:
                str_type = int
            elif int_type == 1:
                str_type = str
            else:
                str_type = bool
            print('This function has return type', str_type)
        else:
            print(s)


        

        
        

class visitor(ast.NodeVisitor):
    """AST visitor. 
    
    For all "interesting" / constraint-generating nodes, we determine if it is a parameter, and if so add the constraints to the global dict"""
    def visit_Attribute(self, node: ast.Attribute) -> Any:
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        param = node.value.id
        if param in param_constraints and param not in out_of_consideration:
            param_constraints[param].append(node.attr)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        super().generic_visit(node)
        expr1 = symbolic_vars[node.left]
        expr2 = symbolic_vars[node.right]
        symbolic_vars[node] = Int(str(node))
        if type(node.op) == ast.Mult:
            case1 = And(symbolic_vars[node] == expr1, symbolic_vars[node] == expr2)
            case2 = And(expr1 == 1, expr2 == 0, symbolic_vars[node] == 1)
            solver.add(Or(case1, case2))
        else:
            solver.add(symbolic_vars[node] == expr1, symbolic_vars[node] == expr2)

        try:
            param1 = node.left.id
           
            if param1 in param_constraints and param1 not in out_of_consideration:
                param_constraints[param1].append(binop_tostr(node.op))
 
        except:
            pass

        try:
             param2 = node.right.id
             if param2 in param_constraints and param2 not in out_of_consideration:
                param_constraints[param2].append(binop_tostr(node.op))
        except:
            pass

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        super().generic_visit(node)
        expr1 = symbolic_vars[node.left]
        expr2 = symbolic_vars[node.right]
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node] == expr1, symbolic_vars[node] == expr2)
        try:
            param1 = node.left.id
            if param1 in param_constraints and param1 not in out_of_consideration:
                param_constraints[param1].append(boolop_tostr(node.op))
        except:
            pass
        try:
            param2 = node.right.id

            if param2 in param_constraints and param2 not in out_of_consideration:
                param_constraints[param2].append(boolop_tostr(node.op))
        except:
            pass
    
    def visit_Compare(self, node: ast.Compare) -> Any:
        super().generic_visit(node)
        expr1 = symbolic_vars[node.left]
        expr2 = symbolic_vars[node.comparators[0]]
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node] == expr1, symbolic_vars[node] == expr2)

        try:
            param = node.left.id
            if param in param_constraints and param not in out_of_consideration:
                param_constraints[param].append(compare_tostr(node.ops[0]))
        except:
            pass
        try:
            param = node.comparators[0].id
            if param in param_constraints and param not in out_of_consideration:
                param_constraints[param].append(compare_tostr(node.ops[0]))
        except:
            pass

    def visit_ListComp(self, node: ast.ListComp) -> Any:
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node.iter] == 1)
        try:
            param = node.iter.id
            if param in param_constraints and param not in out_of_consideration:
                param_constraints[param].append('__iter__')
        except:
            pass
    
    def visit_comprehension(self, node: ast.comprehension) -> Any:
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node.iter] == 1)
        try:
            param = node.iter.id
            if param in param_constraints and param not in out_of_consideration:
                param_constraints[param].append('__iter__')
        except:
            pass
                    
    
    def visit_Slice(self, node: ast.Slice) -> Any:
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node.lower] == 0, symbolic_vars[node.upper] == 0)
        try:
            param1 = node.lower.id
            if param1 in param_constraints and param1 not in out_of_consideration:
                param_constraints[param1].append("__int__")
        except:
            pass
        try:
            param2 = node.upper.id
            if param2 in param_constraints and param2 not in out_of_consideration:
                param_constraints[param2].append("__int__")
        except:
            pass
        
    def visit_Subscript(self, node: ast.Subscript) -> Any:
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node.value] == 1)
        try:
            param = node.value.id
            if param in param_constraints and param not in out_of_consideration:
                param_constraints[param].append("index")
        except:
            pass
    
    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node] == symbolic_vars[node.operand])
        try:
            param = node.operand.id
            if param in param_constraints and param not in out_of_consideration:
                param_constraints[param].append(unop_tostr(node.op))
        except:
            pass
    
    def visit_AugAssign(self, node: ast.AugAssign) -> Any:
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node.target] == symbolic_vars[node.value])
        solver.add(symbolic_vars[node] == symbolic_vars[node.target])
        try:
            param = node.target.id
            if param in param_constraints and param not in out_of_consideration:
                param_constraints[param].append(binop_tostr(node.op))
        except:
            pass
        try:
            param = node.value.id
            if param in param_constraints and param not in out_of_consideration:
                param_constraints[param].append(binop_tostr(node.op))
        except:
            pass

    def visit_Assign(self, node: ast.Assign) -> Any:
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node.targets[0]] == symbolic_vars[node.value])
        solver.add(symbolic_vars[node] == symbolic_vars[node.targets[0]])
        try:
            param = node.targets[0].id
            if param in param_constraints and param not in out_of_consideration:
                out_of_consideration.add(param)
            if param not in param_constraints:
                param_constraints[param] = list()
        except:
            pass
    
    def visit_For(self, node: ast.For) -> Any:
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node.iter] == 1)
        try:
            param = node.iter.id
            if param in param_constraints and param not in out_of_consideration:
                param_constraints[param].append("__iter__")
        except:
            pass
    
    def visit_While(self, node: ast.While):
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node.test] == 2)

    def visit_If(self, node):
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node.test] == 2)
    
    def visit_Expression(self, node):
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars[node.test] == symbolic_vars[node.body])

    def visit_Call(self, node):
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))

    def visit_Constant(self, node):
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        t = type(node.value)
        i = 0 if t == int else (1 if t == str else 2)
        solver.add(symbolic_vars[node] == i)

    def visit_Name(self, node):
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        if node.id not in symbolic_vars:
            symbolic_vars[node.id] = Int(node.id)
        solver.add(symbolic_vars[node] == symbolic_vars[node.id])

    def visit_Return(self, node):
        super().generic_visit(node)
        symbolic_vars[node] = Int(str(node))
        solver.add(symbolic_vars['return'] == symbolic_vars[node])
        try:
            val = node.value
            solver.add(symbolic_vars[node] == symbolic_vars[node.value])
        except:
            pass
 



def binop_tostr(node):
    ops = {
        ast.Add: "__add__",
        ast.Sub: "__sub__",
        ast.Mult: "__mul__",
        ast.Div: "__div__",
        ast.FloorDiv: "__floordiv__",
        ast.Mod: "__mod__",
        ast.Pow: "__pow__",
        ast.LShift: "__lshift__",
        ast.RShift: "__rshift__",
        ast.BitOr: "__or__",
        ast.BitXor: "__xor__",
        ast.BitAnd: "__and__"
    }
    return ops[type(node)]

def boolop_tostr(node):
    if type(node) == ast.And:
        return "__and__"
    else:
        return "__or__"

def compare_tostr(node):
    ops = {
        ast.Eq: "__eq__",
        ast.NotEq: "__neq__",
        ast.Lt: "__lt__",
        ast.LtE: "__lte__",
        ast.Gt: "__gt__",
        ast.GtE: "__gte__",
        ast.Is: "__init__",
        ast.IsNot: "__init__",
        ast.In: "__iter__",
        ast.NotIn: "__iter__"
    }
    return ops[type(node)]

def unop_tostr(node):
    ops = {
        ast.UAdd: "__uadd__",
        ast.USub: "__usub__",
        ast.Not: "__not__",
        ast.Invert: "__invert__"
    }
    return ops[type(node)]



