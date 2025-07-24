'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : check_crc_result.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-23
Description :
LastEditTime: 2025-07-24
'''

import os
import sys
import re
import argparse
from collections import defaultdict


def parse_file1(line, module_name):
    if False:  # module_name:
        pass
    else:
        match = re.match(r'#(\d+)-(\d+) input: (.+), config: (.+), crc(.*): (.+)', line.strip())
        if match:
            return {
                'frame_idx': int(match.group(1)),
                'config_idx': int(match.group(2)),
                'input_name': match.group(3),
                'config_name': match.group(4),
                'crc_value': match.group(6),
            }
    return None


def parse_file2(line, module_name):
    match = re.match(r'input: (.+), config: (.+), crc of frame #(\d+): (.+)', line.strip())
    if match:
        return {
            'input_name': match.group(1),
            'config_name': match.group(2),
            'frame_idx': int(match.group(3)),
            'crc_value': match.group(4),
        }
    return None


def read_and_parse(filename, parser, module_name):
    """读取文件并解析有效行"""
    data = []
    with open(filename, 'r') as f:
        for line in f:
            parsed = parser(line, module_name)
            if parsed:
                data.append(parsed)
    return data


def find_consecutive_matches(data1, data2):
    """找到连续的匹配行"""
    # 建立第二个文件的索引 {(input_name, config_name): [entries]}
    file2_index = defaultdict(list)
    for entry in data2:
        key = (entry['input_name'], entry['config_name'])
        file2_index[key].append(entry)

    # 遍历第一个文件寻找匹配
    matches = []
    i = 0
    while i < len(data1):
        entry1 = data1[i]
        key = (entry1['input_name'], entry1['config_name'])

        if key in file2_index and file2_index[key]:
            # 找到匹配的第二个文件条目
            entry2 = file2_index[key].pop(0)

            # 检查后续连续多少行是匹配的
            n = 1
            while (
                i + n < len(data1)
                and len(file2_index[key]) > 0
                and (data1[i + n]['input_name'], data1[i + n]['config_name']) == key
            ):
                next_entry2 = file2_index[key].pop(0)
                n += 1

            matches.append({'start_idx1': i, 'start_idx2': data2.index(entry2), 'n': n, 'key': key})
            i += n
        else:
            i += 1
    return matches


def compare_crc(data1, data2, matches):
    """比较匹配行的CRC值"""
    errors = []
    error_count = 0

    for match in matches:
        start1 = match['start_idx1']
        start2 = match['start_idx2']
        n = match['n']

        for i in range(n):
            entry1 = data1[start1 + i]
            entry2 = data2[start2 + i]

            if entry1['crc_value'] != entry2['crc_value']:
                error_count += 1
                if len(errors) < 5:
                    errors.append(
                        f"❌ CRC mismatch at {entry1['input_name']}/{entry1['config_name']}: "
                        f" ({entry1['crc_value']} != {entry2['crc_value']})"
                    )

    return errors, error_count


def check_crc_result(file1_path, file2_path, module_name):
    # 读取并解析两个文件
    data1 = read_and_parse(file1_path, parse_file1, module_name)
    data2 = read_and_parse(file2_path, parse_file2, module_name)
    print(f"match {len(data1)} / {len(data2)} valid crc lines.")
    if len(data1) == 0 or len(data2) == 0:
        print("❌ No valid crc lines found!")
        return -1

    # 找到连续的匹配行
    matches = find_consecutive_matches(data1, data2)
    print(f"find {len(matches)} valid pairs of crc lines.")

    # 比较CRC值
    errors, total_errors = compare_crc(data1, data2, matches)

    # 输出结果
    if not errors and total_errors == 0:
        print("✅ All CRC values match!")
    else:
        for error in errors:
            print(error)
        if total_errors > 5:
            print(f"❌ ... and {total_errors - 5} more errors")

    # 输出统计信息
    # print(f"\nStatistics:")
    # print(f"Total matching blocks: {len(matches)}")
    # print(f"Total CRC mismatches: {total_errors}")
    return total_errors


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-m", "--module", default="", help="module name (sharp, acm, dci, csc, ...)")
    arg_parser.add_argument("-c1", "--crc1", default="", help="a single total crc file from fpga")
    arg_parser.add_argument("-c2", "--crc2", default="", help="the first crc file from cmodel")
    arg_parser.add_argument("-n", "--num", type=int, default=1, help="cmodel crc files number")
    arg_parser.print_usage()
    args = arg_parser.parse_args()

    nb_files = args.num
    fpga_crc_file = args.crc1
    cmodel_crc_file = args.crc2
    if not os.path.exists(fpga_crc_file):
        print(f"CRC file {fpga_crc_file} not exist!")
        sys.exit(1)

    cmodel_crc_files = [cmodel_crc_file]
    ## <module>_crc_from_input_random_input_1920x1080_seed_{seed}_nv24_config_num_<nb_config>.dat
    match = re.match(r'(.+)_seed_(\d+)_nv24_(.+)', cmodel_crc_file)
    if match:
        for k in range(nb_files):
            seed = int(match.group(2))
            next_file = match.group(1) + f"_seed_{seed+k}_nv24_" + match.group(3)
            cmodel_crc_files.append(next_file)
    print(f"get {len(cmodel_crc_files)} cmodel crc files to check...")

    nb_pass = 0
    for cmodel_crc_file in cmodel_crc_files:
        if not os.path.exists(cmodel_crc_file):
            print(f"CRC file {cmodel_crc_file} not exist!")
            break

        print(f"\nChecking CRC values for {os.path.basename(cmodel_crc_file)}...")
        total_errors = check_crc_result(fpga_crc_file, cmodel_crc_file, args.module.lower())
        if total_errors != 0:
            print(f"❌ CRC values mismatch for {os.path.basename(cmodel_crc_file)}!")
            break
        else:
            nb_pass += 1
    print(f"\nTotal {nb_pass} / {len(cmodel_crc_files)} cmodel crc files pass!")
