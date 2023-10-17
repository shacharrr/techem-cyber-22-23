from sympy import *

def parse_function(func):
    func = func.replace("^", "**")
    parts = func.split(" ")
    sbls = ""

    temp = len(parts)//2+1 if len(parts)%2 == 1 else len(parts)//2
    prefixes = [""]*temp
    postfixes = [""]*temp

    for i in range(0, len(parts), 2):
        passed_symbol = False
        for j in range(len(parts[i])):
            cc = parts[i][j]
            if cc.isalpha():
                sbls += f"{cc} "
                passed_symbol = True
            elif not passed_symbol:
                prefixes[i//2]+=f"{cc}"
            else:
                postfixes[i//2]+=f"{cc}"

    pre = [float(1 if not p else p) for p in prefixes]
    post = [float(p.replace("*", "")) if p else 1.0 for p in postfixes]
    d = [parts[i] for i in range(1, len(parts), 2)]
    return pre, sbls.strip(), post, d

def build_expr(pre, sym, post, d):
    expr = pre[0]*sym[0]**post[0]
    for i in range(1, len(pre)):
        if d[i-1] == "+":
            expr += pre[i]*sym[i]**post[i]
        else:
            expr -= pre[i]*sym[i]**post[i]

    return expr

def create_deriatives(expr, sym):
    r = []
    for s in sym:
        r.append(f"{Derivative(expr, s).doit()}")
    return r

def evaluate_expression(expr, v, n):
    if len(v) != len(n):
        raise Exception("V and N must contain the same number of elements")
    for i in range(len(v)):
        expr = expr.replace(v[i], str(n[i]))
    return eval(expr)