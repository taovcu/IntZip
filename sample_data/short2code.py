import sys, os, struct

# transform short to [code, nb_bits]
s2c_dict = {
            0: [0,0], 1:[1,0], 2:[2,0], 3:[3,0],
            4: [4,0], 5:[5,0], 6:[6,0], 7:[7,0],
            8: [8,0], 9:[9,0], 10:[10,0], 11:[11,0],
            12: [12,0], 13:[13,0], 14:[14,0], 15:[15,0],
            16: [16,1], 18:[17,1], 20:[18,1], 22:[19,1],
            24: [20,2], 28:[21,2], 32:[22,3], 40:[23,3],
            48: [24,4], 64:[25,6], 128:[26,7], 256:[27,8],
            512: [28,9], 1024:[29,10], 2048:[30,11], 4096:[31,12],
            8192: [32,13], 16384:[33,14], 
            -8192: [35,13], -16384:[34,14], 
            -512: [39,9], -1024:[38,10], -2048:[37,11], -4096:[36,12],
            -48: [43,4], -64:[42,6], -128:[41,7], -256:[40,8],
            -24: [47,2], -28:[46,2], -32:[45,3], -40:[44,3],
            -16: [51,1], -18:[50,1], -20:[49,1], 22:[48,1],
            -12: [55,0], -13:[54,0], -14:[53,0], -15:[52,0],
            -8: [59,0], -9:[58,0], -10:[57,0], -11:[56,0],
            -4: [63,0], -5:[62,0], -6:[61,0], -7:[60,0],
            -1:[66,0], -2:[65,0], -3:[64,0],
        }

sorted_keys = sorted(s2c_dict)

def short2code(s):
    if s in s2c_dict:
        return s2c_dict[s]

    if s > sorted_keys[-1]:
        return s2c_dict[sorted_keys[-1]]

    if s < sorted_keys[0]:
        return s2c_dict[sorted_keys[0]]

    for i in range(len(sorted_keys)):
        if s >= 0:
            if s > sorted_keys[i] and s < sorted_keys[i+1]:
                return s2c_dict[sorted_keys[i]]
        else:
            if s > sorted_keys[i] and s < sorted_keys[i+1]:
                return s2c_dict[sorted_keys[i+1]]

    return None


with open(sys.argv[1], 'rb') as fp:
    s_list = []
    txt_bin = fp.read()
    total_bits = 0
    fo = open(sys.argv[2], 'wb')
    for i in range(len(txt_bin) // 2):
        s = struct.unpack("<H", txt_bin[i*2:i*2+2])[0]
        s_list.append(s)

    md = (max(s_list) + 1) // 2
    for s in s_list:
        s = s - md
        cb = short2code(s)
        #print(s, cb)
        if not cb:
            print("Value error: {} cannot be covered by the table".format(s))
            sys.exit(1)

        total_bits += cb[1]
        fo.write(cb[0].to_bytes(1, 'big'))

    fo.close()
    print("nbbits = {}, = {} bytes".format(total_bits, total_bits//8))





