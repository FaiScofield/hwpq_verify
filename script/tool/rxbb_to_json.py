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


class rxbb_reader():
    def __init__(self, input_xlsx_name):
        self.input_xlsx_name    = input_xlsx_name

        self.xlsx_data          = pd.read_excel(self.input_xlsx_name, sheet_name=None)
        self.sheet_name_list    = list(self.xlsx_data.keys())
        self.sheet_num          = len(self.sheet_name_list)

        self.reg_dict_list      = []
        for sheet_idx in range(0, self.sheet_num, 1):
            reg_dict = self.read_rxbb_reg(self.sheet_name_list[sheet_idx])
            self.reg_dict_list.append(reg_dict)


    def save_to_json(self, dst_path):
        # json_info = json.dumps(self.reg_dict, cls=NpEncoder)
        # with open(dst_path, "w") as fp:
        #     fp.write(json_info)
        for sheet_idx in range(0, self.sheet_num, 1):
            dst_file_name = "%s//%s.json" % (dst_path, self.sheet_name_list[sheet_idx])
            with open(dst_file_name, "w") as f_out:
                json.dump(self.reg_dict_list[sheet_idx], f_out, indent=4, separators=(', ', ': '), cls=NpEncoder)


    def read_rxbb_reg(self, sheet_name):
        data = self.xlsx_data[sheet_name]
        reg_dict = self.cvt_datafrom_to_reg_dict(data)
        return reg_dict

    def cvt_datafrom_to_reg_dict(self, data):
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

if __name__ == "__main__":
    args = sys.argv

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_xlsx_file", required=True)
    parser.add_argument("-o", "--out_path", required=True)

    args = parser.parse_args()

    input_xlsx_file = args.input_xlsx_file
    out_path = args.out_path

    rxbb_proc = rxbb_reader(input_xlsx_file)
    rxbb_proc.save_to_json(out_path)
