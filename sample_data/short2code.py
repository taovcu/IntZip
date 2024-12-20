import sys, os, struct
import bstream as bt

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
            -16: [51,1], -18:[50,1], -20:[49,1], -22:[48,1],
            -12: [55,0], -13:[54,0], -14:[53,0], -15:[52,0],
            -8: [59,0], -9:[58,0], -10:[57,0], -11:[56,0],
            -4: [63,0], -5:[62,0], -6:[61,0], -7:[60,0],
            -1:[66,0], -2:[65,0], -3:[64,0],
            #-16384:[67,0]
        }

# code to baseline and nbbits
c2s_dict = {
            0: [0,0], 1:[1,0], 2:[2,0], 3:[3,0],
            4: [4,0], 5:[5,0], 6:[6,0], 7:[7,0],
            8: [8,0], 9:[9,0], 10:[10,0], 11:[11,0],
            12: [12,0], 13:[13,0], 14:[14,0], 15:[15,0],
            16: [16,1], 17:[18,1], 18:[20,1], 19:[22,1],
            20: [24,2], 21:[28,2], 22:[32,3], 23:[40,3],
            24: [48,4], 25:[64,6], 26:[128,7], 27:[256,8],
            28: [512,9], 29:[1024,10], 30:[2048,11], 31:[4096,12],
            32: [8192,13], 33:[16384,14],
            35:[-8192,13], 34:[-16384,14],
            39:[-512,9], 38:[-1024,10], 37:[-2048,11], 36:[-4096,12],
            43:[-48,4], 42:[-64,6], 41:[-128,7], 40:[-256,8],
            47:[-24,2], 46:[-28,2], 45:[-32,3], 44:[-40,3],
            51:[-16,1], 50:[-18,1], 49:[-20,1], 48:[-22,1],
            55:[-12,0], 54:[-13,0], 53:[-14,0], 52:[-15,0],
            59:[-8,0], 58:[-9,0], 57:[-10,0], 56:[-11,0],
            63:[-4,0], 62:[-5,0], 61:[-6,0], 60:[-7,0],
            66:[-1,0], 65:[-2,0], 64:[-3,0],
            #67:[-16384,0]
        }


sorted_keys = sorted(s2c_dict)
bs = bt.BitStream(0,0)
global MD
MD = 0

debug_level = 0

def print_debug(*args):
    if debug_level:
        print(*args)


def short2code(s):
    global MD
    if s == (0-MD):
        return [67,0]

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

def compress(f):
    global MD
    global bs
    with open(f, 'rb') as fp:
        s_list = []
        txt_bin = fp.read()
        total_bits = 0
        fcode = open(f + '.code', 'wb')
        #fbits = open(f + '.bstream', 'wb')
        for i in range((len(txt_bin) // 2)):
            #print_debug(i, "unpack {}-{} bytes".format(i*2, i*2+1))
            s = struct.unpack("<H", txt_bin[i*2:i*2+2])[0]
            s_list.append(s)
        
        #print_debug("s_list len", len(s_list))
    
        md = (max(s_list) + 1) // 2
        print_debug(md)
        MD = md
        s2c_dict[-MD] = [67,0]
        c2s_dict[67] = [-MD, 0]
    
    
        for i in range(len(s_list)):
            s = s_list[i]
            s = s - MD
            cb = short2code(s)
            #print_debug(s+MD, s, cb)
            if not cb:
                print_debug("Value error: {} cannot be covered by the table".format(s))
                sys.exit(1)
    
            bits_v = 0
            if s > 0:
                bits_v = s - c2s_dict[cb[0]][0]
            if s < 0:
                bits_v = c2s_dict[cb[0]][0] - s
    
            assert(bits_v >= 0)
    
            total_bits += cb[1]
            fcode.write(cb[0].to_bytes(1, 'big'))
            bs.push(bits_v, cb[1])
            print_debug("{}th encode: value={}, code = {}, nbv = {} = {} bits".format(i, s + MD, cb[0], bits_v, cb[1]))
    
    
        # bitstream file include 4 byte header for nbbits
        # bitstream file include 2 byte header for MD value to handle 0
        #fbits.write(bs.nbbit.to_bytes(4, 'little'))
        #fbits.write(MD.to_bytes(2, 'little'))
        #fbits.write(bs.value.to_bytes((bs.nbbit+7)//8, 'little'))
        bs.savefile(f + '.bstream')
    
        fcode.close()
        print_debug("input file size {}".format(os.path.getsize(f)))
        os.system("~/git/FiniteStateEntropy/fse -f {}".format(f+".code"))
        print_debug("compressed code file size {}".format(os.path.getsize(f + '.code.fse')))
        print_debug("bitstream file size {}".format(os.path.getsize(f + '.bstream')))

        # assemble compressed file
        # MD[2bytes] + FSE.bin + bstream.bin
        with open (f + '.iz', 'wb') as fp:
            fp.write(MD.to_bytes(2, 'little'))
            ffse = open(f + '.code.fse', 'rb')
            bf = ffse.read()
            fbits = open(f + '.bstream', 'rb')
            bs = fbits.read()
            fp.write(MD.to_bytes(2, 'little'))
            fp.write(bf)
            fp.write(bs)
            ffse.close()
            fbits.close()


        # decompress validation
        orig_list = []
        os.system("~/git/FiniteStateEntropy/fse -d -f {}".format(f+".code.fse"))
        with open(f+'.iz', 'rb') as fp:
            MD = int.from_bytes(fp.read(2), "little")
            bs_decode = bt.BitStream(f + '.bstream')

        val_len = os.path.getsize(f + '.code')
        with open(f+'.code', 'rb') as fp:
            code_bin = fp.read()
            code_list = []
            for i in range(val_len):
                s = int(code_bin[i])
                code_list.append(s)

        print_debug(code_list)
        for i in range(val_len):
            print("decoding", i)
            code = code_list.pop()
            print_debug("code:", code)
            base = c2s_dict[code][0]
            print_debug("base:", base)
            bitv = bs_decode.pop(c2s_dict[code][1])
            print_debug("nbbits:", c2s_dict[code])
            print_debug("bitv:", bitv)
            print_debug("restroed:", base + bitv + MD)
            if base < 0:
                orig_list.insert(0, base - bitv + MD)
            else:
                orig_list.insert(0, base + bitv + MD)

            print_debug("{}th decode: value={}, code = {}, nbv = {} = {} bits".format(val_len-1-i, base + bitv + MD, code, bitv, c2s_dict[code][1]))

        print("{} --> {} bytes".format(os.path.getsize(f), os.path.getsize(f + '.iz')))
        if orig_list == s_list:
            print("encode and decode PASS")
        else:
            i = len(s_list) - 1
            while i>= 0:
                if orig_list[i] != s_list[i]:
                    print_debug("Fail", i, "orig = {}, restored = {}".format(s_list[i], orig_list[i]))
                    sys.exit(1)
                i -= 1


compress(sys.argv[1])
