'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : check_crc_result.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-23
Description :
LastEditTime: 2025-07-23
'''

import os
import sys
import re
from collections import defaultdict

def parse_file1(line):
    match = re.match(r'#(\d+)-(\d+) input: (.+), config: (.+), crc: (.+)', line.strip())
    if match:
        return {
            'frame_idx': int(match.group(1)),
            'config_idx': int(match.group(2)),
            'input_name': match.group(3),
            'config_name': match.group(4),
            'crc_value': match.group(5)
        }
    return None

def parse_file2(line):
    match = re.match(r'input: (.+), config: (.+), crc of frame #(\d+): (.+)', line.strip())
    if match:
        return {
            'input_name': match.group(1),
            'config_name': match.group(2),
            'frame_idx': int(match.group(3)),
            'crc_value': match.group(4)
        }
    return None

def read_and_parse(filename, parser):
    """读取文件并解析有效行"""
    data = []
    with open(filename, 'r') as f:
        for line in f:
            parsed = parser(line)
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
            while (i + n < len(data1) and
                   len(file2_index[key]) > 0 and
                   (data1[i+n]['input_name'], data1[i+n]['config_name']) == key):
                next_entry2 = file2_index[key].pop(0)
                n += 1

            matches.append({
                'start_idx1': i,
                'start_idx2': data2.index(entry2),
                'n': n,
                'key': key
            })
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

def check_crc_result(file1_path, file2_path):
    # 读取并解析两个文件
    data1 = read_and_parse(file1_path, parse_file1)
    data2 = read_and_parse(file2_path, parse_file2)
    print(f"match {len(data1)} / {len(data2)} valid crc lines.")

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
    if len(sys.argv) < 2:
        print("Usage: python check_crc_result.py <fpga_crc_file> <cmodel_crc_file> [nb_files]")
        sys.exit(1)
    nb_files = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    fpga_crc_file = sys.argv[1]
    cmodel_crc_file = sys.argv[2]
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

    for cmodel_crc_file in cmodel_crc_files:
        if not os.path.exists(cmodel_crc_file):
            print(f"CRC file {cmodel_crc_file} not exist!")
            break

        print(f"\nChecking CRC values for {os.path.basename(cmodel_crc_file)}...")
        total_errors = check_crc_result(fpga_crc_file, cmodel_crc_file)
        if total_errors > 0:
            print(f"❌ CRC values mismatch for {os.path.basename(cmodel_crc_file)}!")





