from secrets import randbits

flag = open('flag.txt', 'rb').read().strip()
assert len(flag) == 64

K.<a> = QuadraticField(-19)
O = K.maximal_order()
b1 = O(randbits(128) * a + randbits(128))
b2 = O(randbits(128) * a + randbits(128))
x = int.from_bytes(flag, byteorder='big') * a
y1, y2 = x.mod(b1), x.mod(b2)

print(f'{y1 = }\n{y2 = }\n{b1 = }\n{b2 = }')