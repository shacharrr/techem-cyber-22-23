import numpy as np
from sympy import *
import random
import f
import time

def compute(function, target_value, iteration_number):

    pre, ssym, post, d = f.parse_function(function)
    slist = ssym.split(" ")
    sym = symbols(ssym)
    if type(sym) != list:
        sym = [sym]
    expr = f.build_expr(pre, sym, post, d)
    drs = f.create_deriatives(expr, sym)

    vlist = []
    for _ in range(len(sym)):
        vlist.append(float(random.randint(1, 100)))

    tolerance = 1e-6

    for _ in range(iteration_number):
        feval = f.evaluate_expression(str(expr), slist, vlist)
        if abs(feval - target_value) < tolerance:
            sol = "Solution found:\n"
            for i in range(len(slist)):
                sol += f"{slist[i]} = {vlist[i]}\n"
            print(sol)
            print(f"f({ssym.replace(' ', ',')}) = {feval}")
            return
        
        J = np.array([
            [f.evaluate_expression(str(drs[i]), [slist[i]], [vlist[i]]) for i in range(len(slist))]
        ])
        delta_vlist = np.linalg.pinv(J).dot([feval - target_value])
        for i in range(len(vlist)):
            vlist[i] -= delta_vlist[i]
        
    print("Algorithm did not converge to the desired tolerance.")

def main():
    function_value = input("Choose the function: ")
    target_value = int(input("Choose the target: "))
    randomnese = int(input("Choose the number of iterations (Best about 100-10000): "))
    start = time.time()
    compute(function_value, target_value, randomnese)
    end = time.time()
    print(f"Elapsed time: {end-start}")

main()
