#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : script/tool/rxbb_to_c_header.py
Author      : Rockchip
Description : Read rxbb-format Excel register definition sheets into a C header
              with union/struct bitfield definitions.
              Each sheet = one hardware module; output is one struct per sheet.
LastEditTime: 2025-07-14
"""

import os
import pandas as pd
import json
import numpy as np
import sys
import argparse


## ===================== Utility: Numpy type -> JSON encoder =====================
class NpEncoder(json.JSONEncoder):
    """Convert numpy ints/floats/arrays to native Python types for JSON serialization."""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


## ===================== Entry point =====================
def main(args):
    """
    Main entry point.
    1. Parse CLI args (input .xlsx, output .h)
    2. Open output file, write header guard
    3. Iterate over Excel sheets, call write_sheet_reg() per sheet
    4. Write closing guard
    """
    parser = argparse.ArgumentParser()
    parser.description = "Read rxbb Excel register table, generate C header"
    parser.add_argument(
        "-i", "--input_path", type=str, required=True, help="Input Excel register definition file (.xlsx)"
    )
    parser.add_argument("-o", "--output_path", type=str, required=True, help="Output C header file path (.h)")
    parser.add_argument(
        "-s",
        "--sheet",
        type=str,
        default=None,
        help="Sheet name to process (optional). Only convert this sheet if set.",
    )

    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path
    target_sheet = args.sheet

    with open(output_path, "w") as fp:
        # Get all sheets in the Excel file
        sheet_list = pd.read_excel(input_path, sheet_name=None)

        # If a specific sheet is requested, validate and filter
        if target_sheet is not None:
            if target_sheet not in sheet_list:
                msg = "Error: sheet '" + target_sheet + "' not found in '" + input_path + "'!"
                print(msg)
                print("Available sheets:", list(sheet_list.keys()))
                sys.exit(1)
            sheet_list = {target_sheet: sheet_list[target_sheet]}

        # Output filename determines guard macro and top-level struct name
        output_header_name = os.path.basename(output_path).split(".")[0]
        write_header_guard(fp, output_header_name)
        for sheet_name in sheet_list:
            data = sheet_list[sheet_name]
            write_sheet_reg(data, sheet_name, fp)
        write_tail_guard(fp, output_header_name)
    print(f"Done. Generated the register file: {output_path}")


## ===================== Per-sheet output =====================
def write_sheet_reg(data, sheet_name, fp):
    """
    Convert one sheet of data into a C struct (typedef union ... xxx).
    - Write the top-level union/struct skeleton
    - Iterate over registers (grouped by cvt_datafrom_to_reg_dict)
    - Insert reserve_data[N] padding for address gaps
    """
    rxbb_info_struct = cvt_dataframe_to_reg_dict(data)
    reg_addr = 0
    str_temp_seq = [f"typedef union {sheet_name.lower()} {{\n", f"{' ':4}struct {{\n"]
    fp.writelines(str_temp_seq)
    for regs in rxbb_info_struct:
        reg_addr = reg_print(fp, rxbb_info_struct[regs], regs, reg_addr)
    fp.write(f"{' ':4}}} regs;\n")
    fp.write(f"{' ':4}unsigned int data[{reg_addr // 4}];\n")
    fp.write("} %s_u;\n\n" % (sheet_name.lower()))


## ===================== Header guard (opening) =====================
def write_header_guard(fp, output_name):
    """Write #ifndef/#define guard; name derived from output filename (uppercase)."""
    str_temp_seq = ["#ifndef %s_H\n" % (output_name.upper()), "#define %s_H\n" % (output_name.upper()), "\n"]
    fp.writelines(str_temp_seq)


## ===================== Header guard (closing) =====================
def write_tail_guard(fp, output_name):
    """Write #endif closing the header guard."""
    str_temp_seq = ["#endif /* %s_H */\n" % (output_name.upper())]
    fp.writelines(str_temp_seq)


## ===================== Excel row data -> register dict =====================
def cvt_dataframe_to_reg_dict(data):
    """
    Group the DataFrame by the register column into a nested dict:
        { register_name : { field_name : { column : value, ... }, ... }, ... }

    Logic:
    - Deduplicate the register column
    - Count sub-fields per register
    - For each sub-field, save all columns into a per-field sub-dict
    - The returned dict drives per-register C code generation
    """
    # Get the register column, deduplicate to get all names, count how many sub-registers
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
            # Read all columns of this row into a field dict
            sub_reg_struct = dict()
            sub_reg_name = data["field"][tab_idx + sub_reg_idx]
            for item_idx in range(0, data.columns.size, 1):
                sub_reg_struct[data.columns[item_idx]] = data[data.columns[item_idx]][tab_idx + sub_reg_idx]
            sub_reg_info[sub_reg_name] = sub_reg_struct

        rxbb_info_struct[reg_name] = sub_reg_info

    return rxbb_info_struct


## ===================== Single register -> C code =====================
def reg_print(fp, reg_in, reg_in_key, reg_addr):
    """
    Write all bitfields of one register as a C union/struct definition.

    Args:
        fp          - Output file handle
        reg_in      - Bitfield dict for this register
        reg_in_key  - Register name (used for C identifiers)
        reg_addr    - Current byte offset written so far

    Returns:
        Updated reg_addr (+4, or past inserted padding)

    Output format:
        union xxx_u { struct xxx_s { unsigned int f : N; ... } bits; unsigned int val; } sw_xxx;
    """
    # Get register byte offset, check continuity with reg_addr
    reg_offset_cur = reg_in[list(reg_in.keys())[0]]["reg_offset"]
    if reg_offset_cur > reg_addr:
        # Address gap detected; insert reserve_data[N] padding
        reserv_reg_num = reg_offset_cur - reg_addr
        reserv_reg_num = reserv_reg_num // 4
        line_rev_reg_0 = f"{' ':8}struct {{\n{' ':12}unsigned int reserve_data[{reserv_reg_num}];\n{' ':8}}} reserve_reg_{reg_addr}_{reg_offset_cur};\n"
        fp.write(line_rev_reg_0)
        reg_addr += reserv_reg_num * 4

    # ---------- Write union/struct frame ----------
    line_seq0 = [f"{' ':8}union {{ // name: {reg_in_key.lower()}, offset: {reg_addr:#x}\n", f"{' ':12}struct {{\n"]
    fp.writelines(line_seq0)

    # ---------- First pass: collect all (name, width) pairs ----------
    entries = []  # list of (field_name, bit_width)
    reserve_cnt = 0
    reserve_idx = 0
    for key_name in reg_in:
        sub_reg_dict = reg_in[key_name]
        sub_reg_name = sub_reg_dict["field"].replace(".", "_")
        sub_reg_offset_bit = sub_reg_dict["fld_offset"]
        sub_reg_length_bit = sub_reg_dict["fld_size"]
        if sub_reg_offset_bit > reserve_cnt:
            # Gap before field; insert reserve_N padding
            gap = sub_reg_offset_bit - reserve_cnt
            entries.append(("reserve_" + str(reserve_idx), gap))
            reserve_cnt += gap
            reserve_idx += 1
        entries.append((sub_reg_name, sub_reg_length_bit))
        reserve_cnt += sub_reg_length_bit
    if reserve_cnt < 32:
        entries.append(("reserve_" + str(reserve_idx), 32 - reserve_cnt))

    # ---------- Second pass: write with aligned formatting ----------
    max_name_len = max(len(name) for name, _ in entries)
    for name, width in entries:
        reg_str_info = f"{' ':16}unsigned int {name:<{max_name_len}} : {width};\n"
        fp.write(reg_str_info)

    # ---------- Close union/struct ----------
    line_seq1 = [f"{' ':12}}} bits;\n", f"{' ':12}unsigned int val;\n"]
    fp.writelines(line_seq1)
    line_temp = f"{' ':8}}} {reg_in_key.lower()};\n"
    fp.write(line_temp)

    # This register occupies 4 bytes
    reg_addr += 4
    return reg_addr


if __name__ == "__main__":
    """
    Usage: python rxbb_to_c_header.py -i <input.xlsx> -o <output.h>
    """
    args = sys.argv
    main(args)
