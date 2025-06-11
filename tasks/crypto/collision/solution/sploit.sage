from pwn import *
import time
import re
from sage.all import *
from sage.modules.free_module_integer import IntegerLattice

q = 67
m = 20
n = 8
max_attempts = 100  # Ограничение на максимальное число попыток для сбора независимых векторов

def parse_output(data):
    y_match = re.search(r"y: \[([-\d, ]+)\]", data)
    h_match = re.search(r"h: \[([-\d, ]+)\]", data)
    if y_match and h_match:
        y = list(map(int, y_match.group(1).split(", ")))
        h = list(map(int, h_match.group(1).split(", ")))
        return y, h
    raise ValueError("Не удалось распарсить вывод сервера")

def collect_independent_samples(conn, m, q, max_attempts):
    Y_rows = []
    H_rows = []
    attempt = 0

    while len(Y_rows) < m and attempt < max_attempts:
        data = conn.recvuntil(b"y': ").decode()
        y, h = parse_output(data.split("y': ")[0])
        
        if len(Y_rows) == 0 or matrix(GF(q), Y_rows + [y]).rank() == len(Y_rows) + 1:
            Y_rows.append(y)
            H_rows.append(h)
            #print(f"Собрано {len(Y_rows)} из {m} независимых образцов")
        
        conn.sendline(" ".join(map(str, y)).encode())
        attempt += 1

    if len(Y_rows) < m:
        raise RuntimeError("Не удалось собрать m линейно независимых векторов после максимального числа попыток")
    
    return Y_rows, H_rows

def build_lattice(A):
    A_mod = matrix(GF(q), A)
    ker = A_mod.right_kernel()
    basis = ker.basis()
    basis_vectors = [vector(ZZ, [int(x) for x in v]) for v in basis]
    I_m = identity_matrix(ZZ, m)
    generators = basis_vectors + [q * e for e in I_m.rows()]
    L = IntegerLattice(generators)
    return L.LLL()

def main():
    start_time = time.time()
    conn = remote('localhost', 1111)
    
    try:
        # Собираем независимые образцы
        Y_rows, H_rows = collect_independent_samples(conn, m, q, max_attempts)
        
        # Формируем матрицы
        Y_matrix = matrix(GF(q), Y_rows).transpose()  # m x m
        H_matrix = matrix(GF(q), H_rows).transpose()  # n x m
        
        # Вычисляем A
        A_mod = H_matrix * Y_matrix.inverse()  # n x m
        A = [list(row) for row in A_mod]
        
        #print("Матрица A восстановлена")
        
        # Строим решетку и находим короткие векторы
        reduced_basis = build_lattice(A)
        collision_vecs = [v for v in reduced_basis if v.norm() <= 10]
        
        if not collision_vecs:
            raise RuntimeError("Не найдено подходящих векторов")
        
        # Ищем коллизию
        while True:
            data = conn.recvuntil(b"y': ").decode()
            current_y, _ = parse_output(data.split("y': ")[0])
            current_y = vector(ZZ, current_y)
            
            for v in collision_vecs:
                for sign in [1, -1]:
                    y_prime = current_y + sign * v
                    if all(-2 <= x <= 2 for x in y_prime) and y_prime != current_y:
                        print(f"Отправка коллизии: {y_prime}")
                        conn.sendline(" ".join(map(str, y_prime)).encode())
                        print(conn.recvall(timeout=2).decode())
                        return
            # Если не найдено, отправляем оригинальный y
            conn.sendline(" ".join(map(str, current_y)).encode())
    
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()
        #print(f"Затрачено времени: {time.time() - start_time} секунд")

if __name__ == "__main__":
    main()