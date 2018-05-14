import re

# contents = ""
with open("ram.txt", 'r') as f1:
    contents = f1.read()
contents = contents.lower()

ins_set = {"add": 1, "not": 2, "sub": 3, "lsr": 4, "mul": 5, "lsl": 6, "and": 7, "asr": 8,
           "or": 9, "asl": 10, "store": 11, "load": 12, "jmpgez": 13, "jmp": 14, "halt": 15}

size = 32
maccode = [0 for i in range(size)]  # 机器码list
standard_code = ["" for j in range(size)]  # 规范的代码
lines = contents.splitlines()

linenum = 0  # line number in raw code
compiled_linenum = 0  # line number in standard code
storage_num = 0  # the number of used storage

jump_2 = {}  # jump-to L1:addr
jump_from = {}  # jump-from jmp L1,=> L1:addr(jmp)
store_addr = {}  # addr_var:addr
store_addr_start = size // 2

for i in lines:
    linenum += 1
    to_write = 0  # machine code to write
    spltcomm = i.split(';')
    if len(spltcomm) > 0:
        # 以下全是非注释部分(;comments...)
        before_comm = spltcomm[0]
        before_comm_re = re.search(r"^\s*(\w+.*\w+)\s*$", before_comm)  # possible useful codes
        if before_comm_re is not None:
            before_comm = before_comm_re.groups()[0]  # 真正的非注释部分
            ins = re.split(r"\s*:\s*", before_comm)  # list after split by " : "
            op_opr = ""
            if len(ins) == 2:  # 含有xxx:xxx
                #      	try:
                #      		assert(len(ins[0])*len(ins[1])!=0)		#improper use of ":"
                #      	except Exception as e:
                #      		print("[!] Improper use of ':' at line %d"linenum)

                #      	try:
                #      		assert(re.fullmatch(r"[a-zA-Z]+\w+",ins[0])!=None)		# L1:Load 0x20
                #  		except Exception as e:
                #  			print("[!] Improper jump-to label name at line %d"linenum)

                # try:														#jmp2 duplicate
                # 	assert(ins[0] in jump_2)
                # 	jump_2[ins[0]]=compiled_linenum
                # except Exception as e:
                # 	print("[!] Duplicate jump-to name at line %d"linenum)

                jump_2[ins[0]] = compiled_linenum  # {"l1":10} 10 is ln in standard code
                op_opr = ins[1]
            elif len(ins) == 1:
                op_opr = ins[0]

            if len(op_opr) > 0:  # 以下全是纯指令,e.g. load a1, slr, ...
                op_opr_lst = re.split(r"\s+", op_opr)
                if len(op_opr_lst) == 1 and op_opr_lst[0] in ins_set:  # single operand
                    to_write = 256 * ins_set[op_opr_lst[0]]
                    standard_code[compiled_linenum] = op_opr_lst[0]

                elif len(op_opr_lst) == 2 and op_opr_lst[0] in ins_set:  # double operand
                    to_write = 256 * ins_set[op_opr_lst[0]]
                    standard_code[compiled_linenum] = op_opr_lst[0] + " "

                    operand = op_opr_lst[1]  # divide to opcode+operand
                    opcode = op_opr_lst[0]
                    if opcode not in ("jmp", "jmpgez"):
                        if opcode in ("store",):  # OPERAND of store must be an addr
                            if operand in store_addr:
                                store_addr[operand].append(compiled_linenum)
                            else:
                                store_addr[operand] = [compiled_linenum]  # [storage_num + store_addr_start]

                        else:  # add, sub, mul, and, or, load
                            if re.fullmatch(r"[a-zA-Z]+\w*", operand):  # when is an address variable
                                if operand in store_addr:
                                    store_addr[operand].append(compiled_linenum)
                                else:
                                    store_addr[operand] = [compiled_linenum]  # 前提是该地址被开过

                            else:  # when is an immediate num(需要判断合法性
                                if eval(operand) in store_addr:
                                    store_addr[eval(operand)].append(compiled_linenum)
                                else:
                                    store_addr[eval(operand)] = [compiled_linenum]

                    else:
                        jump_from[operand] = compiled_linenum

                maccode[compiled_linenum] = to_write
                compiled_linenum += 1

for i in jump_from:
    jmpfrom = jump_from[i]
    standard_code[jmpfrom] += str(jump_2[i])
    maccode[jmpfrom] += jump_2[i]

for i in store_addr:
    if isinstance(i, int):
        standard_code[storage_num + store_addr_start] = str(i)
        maccode[storage_num + store_addr_start] = i
    for j in store_addr[i]:
        standard_code[j] += str(storage_num + store_addr_start)
        maccode[j] += storage_num + store_addr_start
    storage_num += 1

j = 0
for i in standard_code:
    print(j, '\t', i)
    j += 1

print()
j = 0
for i in maccode:
    print("%02x"%j,'\t',"%04x"%i)  # 
    j += 1

lines = maccode

with open("ramdata.coe", 'w') as f2:
    f2.write("MEMORY_INITIALIZATION_RADIX=10;\n")
    f2.write("MEMORY_INITIALIZATION_VECTOR=\n")
    for i in lines:
        f2.write(str(i) + ',\n')
    f2.write('0;')

with open("ramdata.txt", 'w') as f2:
    f2.write("MEMORY_INITIALIZATION_RADIX=10;\n")
    f2.write("MEMORY_INITIALIZATION_VECTOR=\n")
    for i in lines:
        f2.write(str(i) + ',\n')
    f2.write('0;')
