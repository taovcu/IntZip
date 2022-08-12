class BitStream:
    # 1st 0 means the int value of the bit stream is 0
    # 2nd 0 means the bit stream includes 0 bits    
    def __init__(self, value, nbbit):
        self.value = value
        self.nbbit = nbbit
        self.pool = [] # int pool

    def push(self, v, n):
        # push v as n bits into the stream
        # truncate the low n bit of v
        if n == 0:
            return 0

        v = v & ((1<<n) - 1)
        self.value  += (v << self.nbbit)
        self.nbbit += n
        #self.dump()



    def pop(self, n):
        # pop n bits from the stream and return as a int value
        #print(self.nbbit, n)
        if n == 0:
            return 0
        ret = (self.value >> (self.nbbit -n))
        self.nbbit -= n
        self.value = (self.value & ((1<<self.nbbit) - 1))
        #self.reload()
        return ret

    def dump(self):
        if self.nbbit >= 64:
            try:
                v = self.value & ((1<<64) -1)
                self.pool.append(v)
                self.value = self.value >> 64
                self.nbbit -= 64
            except:
                pass

    def reload(self):
        if self.nbbit < 20:
            try:
                v = self.pool.pop()
                self.value = self.value << 64 + v
                self.nbbit += 64
            except:
                pass

"""
bs = BitStream(0,0)
bs.push(5, 3)
v = bs.pop(3)
print(v, "expected to be 5")

bs.push(13, 4)
v = bs.pop(3)
print(v, "expected to be 6")

v = bs.pop(1)
print(v, "expected to be 1")
"""
