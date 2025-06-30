import os
import json
import numpy as np
import getopt
import sys

class shpLiteCfgGenerator:
    def __init__(self, dst_dir, mask_json):
        self.dst_dir = dst_dir
        # load mask json
        with open(mask_json, 'r') as f:
            self.mask_cfg = json.load(f)
        
    def set_random_seed(self, seed):
        np.random.seed(seed)
    
    def recheck_cfg(self):
        if (self.shp_lite_dict["i_shoot_ctrl_pos_unlimit"] < self.shp_lite_dict["i_shoot_ctrl_pos"]):
            self.shp_lite_dict["i_shoot_ctrl_pos_unlimit"] = self.shp_lite_dict["i_shoot_ctrl_pos"]
            
        if (self.shp_lite_dict["i_shoot_ctrl_neg_unlimit"] < self.shp_lite_dict["i_shoot_ctrl_neg"]):
            self.shp_lite_dict["i_shoot_ctrl_neg_unlimit"] = self.shp_lite_dict["i_shoot_ctrl_neg"]
        
        if (self.shp_lite_dict["i_sharp_roi_xend"] < self.shp_lite_dict["i_sharp_roi_xstart"]):
            max_val = self.mask_cfg['sharp_lite_mask']['i_sharp_roi_xend'][2]
            self.shp_lite_dict["i_sharp_roi_xend"] = np.random.randint(self.shp_lite_dict["i_sharp_roi_xstart"], max_val+1)
        
        if (self.shp_lite_dict["i_sharp_roi_yend"] < self.shp_lite_dict["i_sharp_roi_ystart"]):
            max_val = self.mask_cfg['sharp_lite_mask']['i_sharp_roi_yend'][2]
            self.shp_lite_dict["i_sharp_roi_yend"] = np.random.randint(self.shp_lite_dict["i_sharp_roi_ystart"], max_val+1)
            
    def generate_cfg(self, dst_path):
        shp_lite_dict = {}
        shp_lite_mask = self.mask_cfg['sharp_lite_mask']
        for key in shp_lite_mask.keys():
            rand_info = shp_lite_mask[key]
            if rand_info[0] == 0:
                # rand int mode
                min_val = rand_info[1]
                max_val = rand_info[2]
                shp_lite_dict[key] = np.random.randint(min_val, max_val+1)
            elif rand_info[0] == 2:
                # rand float mode
                min_val = rand_info[1]
                max_val = rand_info[2]
                shp_lite_dict[key] = np.random.uniform(min_val, max_val)
            else:
                raise ValueError('Invalid rand mode')
        
        self.shp_lite_dict = shp_lite_dict
        self.recheck_cfg()
        
        dst_cfg_tmp = {}
        dst_cfg_tmp['SHARPNESS_lite'] = self.shp_lite_dict
        dst_cfg = {}
        dst_cfg["pq_tuning_param"] = dst_cfg_tmp
        
        # write to file
        with open(dst_path, 'w') as f:
            json.dump(dst_cfg, f, indent=4)

def usage():
    print("Usage: python generate_json.py -d <dst_dir> -m <mask_json> -s <seed>")

def parse_args(argv):
    try:
        opts, args = getopt.getopt(argv, "hd:m:s:", ["help", "dst_dir=", "mask_json=", "seed="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    dst_dir = None
    mask_json = None
    seed = None
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--dst_dir"):
            dst_dir = arg
        elif opt in ("-m", "--mask_json"):
            mask_json = arg
        elif opt in ("-s", "--seed"):
            seed = int(arg)
    
    if dst_dir is None or mask_json is None or seed is None:
        usage()
        sys.exit(2)
    
    return dst_dir, mask_json, seed


if __name__ == '__main__':
    dst_dir, mask_json, seed = parse_args(sys.argv[1:])
    
    cfg_gen = shpLiteCfgGenerator(dst_dir, mask_json)
    cfg_gen.set_random_seed(seed)
    for cfg_idx in range(100):
        dst_path = "%s//cfg_%d.json" % (dst_dir, cfg_idx)
        cfg_gen.generate_cfg(dst_path)

    
    


        