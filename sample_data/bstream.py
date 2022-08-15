class BitStream:
    # 1st 0 means the int value of the bit stream is 0
    # 2nd 0 means the bit stream includes 0 bits    
    # f is a bitstream file with 4-byte header indicating the nbbit value
    def __init__(self, f=None, value=0, nbbit=0):
        self.pool = []
        self.value = value
        self.nbbit = nbbit
        if f:
            with open(f, 'rb') as fp:
                total_nbbit = int.from_bytes(fp.read(4), "little")
                data_bytes = fp.read()
                l_idx = 0
                for i in range((len(data_bytes) + 7) // 8 - 1):
                    int64 = int.from_bytes(data_bytes[i*8 : (i+1)*8], "little")
                    self.pool.append(int64)
                    total_nbbit -= 64
                    l_idx = i + 1

                assert(total_nbbit <= 64)
                self.value = int.from_bytes(data_bytes[l_idx*8 : ], "little")
                assert(self.value < (1<<64))
                self.nbbit = total_nbbit


    def push(self, v, n):
        # push v as n bits into the stream
        # truncate the low n bit of v
        if n == 0:
            return 0

        v = v & ((1<<n) - 1)
        self.value  += (v << self.nbbit)
        self.nbbit += n
        # dump after write
        self.dump()



    def pop(self, n):
        # pop n bits from the stream and return as a int value
        #print(self.nbbit, n)
        if n == 0:
            return 0

        # reload before read
        if self.nbbit < n:
            self.reload()

        ret = (self.value & ((1<< self.nbbit) - (1<<(self.nbbit - n))))
        self.nbbit -= n
        ret = ret >> self.nbbit
        return ret

    def dump(self):
        # dump 4096 bit at a time
        if self.nbbit >= 4096:
            try:
                for i in range(4096 // 64):
                    v = self.value & ((1<<64) -1)
                    self.pool.append(v)
                    self.value = self.value >> 64
                    self.nbbit -= 64
            except:
                pass

    def reload(self):
        # reload 4096 bit at a time
        try:
            for i in range(min(len(self.pool), 4096//64)):
                v = self.pool.pop()
                self.value = ((self.value & ((1 << self.nbbit) - 1)) << 64) + v
                self.nbbit += 64
        except:
            pass

    def savefile(self, f):
        total_bits = self.nbbit + len(self.pool) * 64
        with open(f, 'wb') as fp:
            fp.write(total_bits.to_bytes(4, 'little'))
            for i in self.pool:
                fp.write(i.to_bytes(8, 'little'))
            
            fp.write(self.value.to_bytes((self.nbbit + 7) // 8, 'little'))

        
"""
bs = BitStream(0,0)
bs.push(255, 64)
print("push 255, 64", bs.value, bs.nbbit, bs.pool)
#v = bs.pop(3)
#print(v, "expected to be 5")

bs.push(255, 65)
print("push 255, 65", bs.value, bs.nbbit, bs.pool)
#v = bs.pop(3)
#print(v, "expected to be 6")

#v = bs.pop(1)
#print(v, "expected to be 1")

bs.savefile("test.bstream")

##########################
bs2 = BitStream("test.bstream", 0, 0)
print("load bitstream", hex(bs2.value), bs2.nbbit, bs2.pool)
v = bs2.pop(41)
print("after pop 41", hex(bs2.value), bs2.nbbit, bs2.pool)
print(hex(v), "expected to be 0")
v = bs2.pop(16)
print("after pop 16", hex(bs2.value), bs2.nbbit, bs2.pool)
print(hex(v), "expected to be 0")
v = bs2.pop(1)
print("after pop 1", hex(bs2.value), bs2.nbbit, bs2.pool)
print(hex(v), "expected to be 1")
v = bs2.pop(7)
print("after pop 7", hex(bs2.value), bs2.nbbit, bs2.pool)
print(hex(v), "expected to be 127")
v = bs2.pop(63)
print("after pop 63", hex(bs2.value), bs2.nbbit, bs2.pool)
print(hex(v), "expected to be 127")
v = bs2.pop(1)
print("after pop 1", hex(bs2.value), bs2.nbbit, bs2.pool)
print(hex(v), "expected to be 1")
print(hex(bs2.value), bs2.nbbit, bs2.pool)
"""
