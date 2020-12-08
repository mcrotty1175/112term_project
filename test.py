def bonusCt2(x):
        def f(g, x): return lambda y: g(x*y)
        def g(n): return 10+n
        return f(f(g, x),x+1)(x+2)
print(bonusCt2(5))