from Crypto.Util.number import getPrime
import random

def H(A, y):
    h = []
    for a in A:
        h.append(sum(a_ * y_ for a_, y_ in zip(a, y)) % q)
    return h

q = 67
n = 8
m = 20
d = 2
random.seed(random.getrandbits(100))
A = [[random.randint(0, q) for _ in range(m)] for _ in range(n)]

while True:
    y = [random.randint(0, d) - d for _ in range(m)]
    h = H(A, y)
    print('y:', y)
    print('h:', h)
    y_ = list(map(int, input('y\': ').split()))
    assert len(y_) == m and set(map(abs, y_)) <= set(range(d+1))
    h_ = H(A, y_)
    if y != y_ and h == h_:
        flag = open('flag.txt', 'r').read().strip()
        print(flag)
    else:
        print('nope')
