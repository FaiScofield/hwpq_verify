'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : check_crc_result.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-23
Description :
LastEditTime: 2025-08-14
'''

import os
import sys
import re
import argparse
from utils import setup_logger

logger = setup_logger("CRC_FILE_CHECK")

def parse_file1(line, module_name):
    if False:  # module_name:
        pass
    else:
        match = re.match(r'#(\d+)-(\d+) input: (.+),\s*config: (.+),\s*crc(.*): (.+)', line.strip())
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
    match = re.match(r'input: (.+),\s*config: (.+),\s*crc of frame #(\d+): (.+)', line.strip())
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


def compare_crc(data1, data2):
    """比较匹配行的CRC值"""
    errors = []

    for entry1, entry2 in zip(data1, data2):
        if entry1['crc_value'] != entry2['crc_value']:
            errors.append(
                f"❌ CRC mismatch at {entry1['input_name']}/{entry1['config_name']}: "
                f" ({entry1['crc_value']} != {entry2['crc_value']})"
            )

    return errors


def check_crc_result(file1_path, file2_list, module_name, nb_max_errors, group_elems, group_offset):
    nb_pass = 0
    data1 = read_and_parse(file1_path, parse_file1, module_name)
    data2 = read_and_parse(file2_list[0], parse_file2, module_name)
    group_elems = len(data2) if group_elems == 0 else min(group_elems, len(data2))
    if len(data1) < group_elems:
        logger.error(f"❌ CRC file '{file1_path}' not complete, only {len(data1)}/{group_elems} valid crc lines found!")
        return nb_pass
    logger.info(f"find {len(data1)} valid crc data in '{file1_path}' ...")
    logger.info(f"group_elems = {group_elems}, group_offset = {group_offset}")
    logger.info("")

    for i in range(len(file2_list)):
        cmodel_crc_file = file2_list[i]
        if not os.path.exists(cmodel_crc_file):
            logger.error(f"CRC file {cmodel_crc_file} not exist!")
            return nb_pass
        logger.info(f"Checking CRC values for {os.path.basename(cmodel_crc_file)}...")

        data2 = read_and_parse(cmodel_crc_file, parse_file2, module_name)
        if len(data2) == 0:
            logger.error("❌ No valid crc data found in '{cmodel_crc_file}'!")
            return nb_pass
        elif len(data2) != group_elems:
            logger.warning(f"CRC file might not be completed, find {len(data2)}/{group_elems} valid crc data!")
        else:
            logger.info(f"find {len(data2)} / {group_elems} valid crc data.")

        # 比较CRC值
        offset = group_offset + i
        st_idx = offset * group_elems
        ed_idx = st_idx + group_elems
        errors = compare_crc(data1[st_idx:ed_idx], data2)

        # 输出结果
        if len(errors) == 0:
            nb_pass += 1
            logger.info("✅ All CRC values match!")
        else:
            for idx, error in enumerate(errors):
                logger.info(error)
                if nb_max_errors > 0 and idx >= nb_max_errors:
                    logger.error(f"❌ ... and {len(errors) - nb_max_errors} more errors")
                    break

    return nb_pass


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-m", "--module", default="", help="module name (sharp, acm, dci, csc, ...)")
    arg_parser.add_argument("-c1", "--crc1", default="", help="a single total crc file from FPGA")
    arg_parser.add_argument("-c2", "--crc2", default="", help="the first crc file from CMODEL")
    arg_parser.add_argument("-ge", "--group_elems", type=int, default=0, help="crc number in each group")
    arg_parser.add_argument("-go", "--group_offset", type=int, default=0, help="start group offset of the first crc2 file")
    arg_parser.add_argument("-n", "--nb_crc2", type=int, default=1, help="CMODEL crc number of files")
    arg_parser.add_argument("-e", "--max_errors", type=int, default=5, help="show max errors per frame")
    arg_parser.print_usage()
    args = arg_parser.parse_args()

    nb_files = args.nb_crc2
    fpga_crc_file = args.crc1
    cmodel_crc_file = args.crc2
    if not os.path.exists(fpga_crc_file):
        logger.error(f"CRC file {fpga_crc_file} not exist!")
        sys.exit(1)

    cmodel_crc_files = [cmodel_crc_file]
    ## <module>_crc_from_input_random_input_1920x1080_seed_{seed}_nv24_config_num_<nb_config>.dat
    match = re.match(r'(.+)_seed_(\d+)_nv24_(.+)', cmodel_crc_file)
    if match:
        for k in range(1, nb_files):
            seed = int(match.group(2))
            next_file = match.group(1) + f"_seed_{seed+k}_nv24_" + match.group(3)
            cmodel_crc_files.append(next_file)
    logger.info(f"get {len(cmodel_crc_files)} cmodel crc files to check...")

    nb_pass = check_crc_result(fpga_crc_file, cmodel_crc_files, args.module.lower(), args.max_errors, args.group_elems, args.group_offset)
    logger.info("")
    logger.info(f"Check result: {nb_pass}/{len(cmodel_crc_files)} cmodel crc files pass!")

