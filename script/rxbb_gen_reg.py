import os
import pandas as pd
import json
import numpy as np
import sys
import argparse

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", required=True)
    parser.add_argument("-o", "--output_path", required=True)
    # parser.add_argument("-s", "--sheet_name_i", required=True)
    
    args = parser.parse_args()
    
    input_path = args.input_path
    output_path = args.output_path
    # sheet_name_i = args.sheet_name_i

    with open(output_path, "w") as fp:
        sheet_list = pd.read_excel(input_path, sheet_name=None)
        output_header_name = os.path.basename(output_path).split(".")[0]
        write_header(fp, output_header_name)
        for sheet_name in sheet_list:
            data = sheet_list[sheet_name]
            write_sheet_reg(data, sheet_name, fp)
        write_tail(fp, output_header_name)
    
def write_sheet_reg(data, sheet_name, fp):
    rxbb_info_struct = cvt_datafrom_to_reg_dict(data)
    reg_addr = 0
    str_temp_seq = ["typedef union %s_u {\n" % (sheet_name.lower()), "\tstruct %s_s {\n" % (sheet_name.lower())]
    fp.writelines(str_temp_seq)
    for regs in rxbb_info_struct:
        reg_addr = reg_print(fp, rxbb_info_struct[regs], regs, reg_addr)
    fp.write("\t} regs;\n")
    fp.write("\tunsigned int p_reg_addr[%d];\n" % (reg_addr // 4))
    fp.write("}%s_t;\n\n" % (sheet_name.lower()))

def write_header(fp, output_name):
    str_temp_seq = ["#ifndef __%s_H__\n" % (output_name.upper()), "#define __%s_H__\n" % (output_name.upper()), "\n"]
    fp.writelines(str_temp_seq)

def write_tail(fp, output_name):
    str_temp_seq = ["#endif //__%s_H__\n" % (output_name.upper())]
    fp.writelines(str_temp_seq)


def cvt_datafrom_to_reg_dict(data):
    # 
    reg_series = data["register"]
    reg_name_list = reg_series.drop_duplicates()
    sub_reg_cnt_list = reg_series.value_counts()
    
    rxbb_info_struct = dict()
    for reg_idx in range(0, reg_name_list.size, 1):
        tab_idx = reg_name_list.index[reg_idx]
        reg_name = reg_name_list[tab_idx]
        sub_reg_cnt = sub_reg_cnt_list[reg_name]
        sub_reg_info = dict()
        for sub_reg_idx in range(0, sub_reg_cnt, 1):
            sub_reg_struct = dict()
            sub_reg_name = data["field"][tab_idx + sub_reg_idx]
            for item_idx in range(0, data.columns.size, 1):
                sub_reg_struct[data.columns[item_idx]] = data[data.columns[item_idx]][tab_idx + sub_reg_idx]
            sub_reg_info[sub_reg_name] = sub_reg_struct
            
        rxbb_info_struct[reg_name] = sub_reg_info
    
    return rxbb_info_struct

def reg_print(fp, reg_in, reg_in_key, reg_addr):
    # check reserve register
    reg_offset_cur = reg_in[list(reg_in.keys())[0]]["reg_offset"]
    if reg_offset_cur > reg_addr:
        reserv_reg_num = reg_offset_cur - reg_addr
        reserv_reg_num = reserv_reg_num // 4
        line_rev_reg_0 = "\t\tstruct { \n\t\t\tunsigned int reserve_data[%d];\n\t\t} reserve_reg_%d_%d;\n" % (reserv_reg_num, reg_addr, reg_offset_cur)
        fp.write(line_rev_reg_0)
        reg_addr += reserv_reg_num*4
        # return reg_addr
    
    line_seq0 = ["\t\tunion %s_u { \n" % (reg_in_key.lower()), "\t\t\tstruct %s_s { \n" % (reg_in_key.lower())]
    fp.writelines(line_seq0)
    reserve_cnt = 0
    reserve_idx = 0
    for key_name in reg_in:
        sub_reg_dict = reg_in[key_name]
        sub_reg_name = sub_reg_dict["field"]
        # replace "." by "_" in sub_reg_name
        sub_reg_name = sub_reg_name.replace(".", "_")
        sub_reg_offset_bit = sub_reg_dict["fld_offset"]
        sub_reg_length_bit = sub_reg_dict["fld_size"]
        if (sub_reg_offset_bit == reserve_cnt):
            reg_str_info = "\t\t\t\tunsigned int %s: %d;\n" % (sub_reg_name, sub_reg_length_bit)
            fp.write(reg_str_info)
        else:
            reg_str_info = "\t\t\t\tunsigned int reserve_%d: %d;\n" % (reserve_idx, sub_reg_offset_bit - reserve_cnt)
            fp.write(reg_str_info)
            reserve_cnt += (sub_reg_offset_bit - reserve_cnt)
            reg_str_info = "\t\t\t\tunsigned int %s: %d;\n" % (sub_reg_name, sub_reg_length_bit)
            fp.write(reg_str_info)
            reserve_idx += 1
        reserve_cnt += sub_reg_length_bit
    if (reserve_cnt < 32):
        reg_str_info = "\t\t\t\tunsigned int reserve_%d: %d;\n" % (reserve_idx, 32 - reserve_cnt)
        fp.write(reg_str_info)
    
    line_seq1 = ["\t\t\t} bits;\n", "\t\t\tunsigned int u32;\n"]
    fp.writelines(line_seq1)
    line_temp = "\t\t} sw_%s;\n" % (reg_in_key.lower())
    fp.write(line_temp)
    
    reg_addr += 4
    return reg_addr
        
    
if __name__ == "__main__":
    args = sys.argv
    main(args)