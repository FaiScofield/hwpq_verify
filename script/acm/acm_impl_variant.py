"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : acm_impl_variant.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-13
Description : ACM implementation with variable LUT lengths and interpolation support
"""

import os
import sys
import numpy as np
import cv2

if __package__:
    from .. import utils as utl
    from .acm_impl import AcmImpl, round_rshift, linear_resize_array_1d, linear_resize_array_2d, gaussian_down_sample
else:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    import utils as utl
    from acm_impl import AcmImpl, round_rshift, linear_resize_array_1d, linear_resize_array_2d, gaussian_down_sample


class AcmImplVariant(AcmImpl):
    """ACM implementation with variable LUT lengths and interpolation support."""
    
    def __init__(self, len_y: int = 9, len_s: int = 13, len_h: int = 65, len_h2: int = 65):
        super().__init__(len_y, len_s, len_h, len_h2)
        self.source_algo = None
        self.source_config = None
    
    def interpolate_from(self, source_acm, kernel=None):
        """Interpolate LUT data from another ACM instance.
        
        Resamples all 9 LUT tables from source_acm to match self's dimensions.
        
        Args:
            source_acm: An AcmImpl/AcmEVideo/AcmImplVariant instance with loaded LUTs.
            kernel: Optional 2D kernel for downsample (default: 5x5 Gaussian).
        """
        if not source_acm.b_lut_ready:
            print("[ACM] Source ACM LUT is not ready!")
            return False
        
        print(f"[ACM] Interpolating LUTs from source: y={source_acm.len_y}x{self.len_y}, s={source_acm.len_s}x{self.len_s}, h={source_acm.len_h}x{self.len_h}, h2={source_acm.len_h2}x{self.len_h2}")
        
        # 1D delta LUTs: resample from source.len_h → self.len_h
        if source_acm.len_h != self.len_h:
            self.lut_delta_ybyh = linear_resize_array_1d(source_acm.lut_delta_ybyh, self.len_h)
            self.lut_delta_sbyh = linear_resize_array_1d(source_acm.lut_delta_sbyh, self.len_h)
            self.lut_delta_hbyh = linear_resize_array_1d(source_acm.lut_delta_hbyh, self.len_h)
            print(f"[ACM] Updated delta LUT size: {source_acm.len_h} => {self.len_h}")
        else:
            self.lut_delta_ybyh = source_acm.lut_delta_ybyh.copy()
            self.lut_delta_sbyh = source_acm.lut_delta_sbyh.copy()
            self.lut_delta_hbyh = source_acm.lut_delta_hbyh.copy()
        
        # 2D gain LUTs: resample from source (len_h2, len_y/len_s) → self (len_h2, len_y/len_s)
        # First handle h2 dimension change, then y/s dimension change
        
        def resize_2d_lut(src_lut, src_h2, src_dim, dst_h2, dst_dim, kernel):
            """Resize a 2D LUT from (src_h2, src_dim) to (dst_h2, dst_dim)."""
            if src_lut.shape == (dst_h2, dst_dim):
                return src_lut.copy()
            
            # First resize h2 dimension if needed
            if src_h2 != dst_h2:
                tmp = np.zeros((dst_h2, src_dim), dtype=src_lut.dtype)
                for i in range(src_dim):
                    tmp[:, i] = linear_resize_array_1d(src_lut[:, i], dst_h2)
            else:
                tmp = src_lut.copy()
            
            # Then resize the other dimension if needed
            if src_dim != dst_dim:
                result = np.zeros((dst_h2, dst_dim), dtype=src_lut.dtype)
                for i in range(dst_h2):
                    result[i, :] = linear_resize_array_1d(tmp[i, :], dst_dim)
                return result
            return tmp
        
        # Gain Y by Y
        self.lut_gain_ybyy = resize_2d_lut(source_acm.lut_gain_ybyy, source_acm.len_h2, source_acm.len_y, 
                                           self.len_h2, self.len_y, kernel)
        self.lut_gain_sbyy = resize_2d_lut(source_acm.lut_gain_sbyy, source_acm.len_h2, source_acm.len_y, 
                                           self.len_h2, self.len_y, kernel)
        self.lut_gain_hbyy = resize_2d_lut(source_acm.lut_gain_hbyy, source_acm.len_h2, source_acm.len_y, 
                                           self.len_h2, self.len_y, kernel)
        
        # Gain Y by S
        self.lut_gain_ybys = resize_2d_lut(source_acm.lut_gain_ybys, source_acm.len_h2, source_acm.len_s, 
                                           self.len_h2, self.len_s, kernel)
        self.lut_gain_sbys = resize_2d_lut(source_acm.lut_gain_sbys, source_acm.len_h2, source_acm.len_s, 
                                           self.len_h2, self.len_s, kernel)
        self.lut_gain_hbys = resize_2d_lut(source_acm.lut_gain_hbys, source_acm.len_h2, source_acm.len_s, 
                                           self.len_h2, self.len_s, kernel)
        
        # Copy gains
        self.gain_y = source_acm.gain_y
        self.gain_s = source_acm.gain_s
        self.gain_h = source_acm.gain_h
        
        # Save source info
        self.source_algo = type(source_acm).__name__
        self.source_config = getattr(source_acm, 'source_config', None)
        
        print("[ACM] Interpolation completed successfully.")
        return True
    
    def set_len_variant(self, len_y, len_s, len_h, len_h2, kernel=None):
        """Change LUT dimensions with resampling of existing data."""
        old_len_y, old_len_s, old_len_h, old_len_h2 = self.len_y, self.len_s, self.len_h, self.len_h2
        
        # Update dimensions and steps
        self.len_y = utl.clamp(len_y, 2, 255 + 1)
        self.len_s = utl.clamp(len_s, 2, 181 + 1)
        self.len_h = utl.clamp(len_h, 2, 360 + 1)
        self.len_h2 = self.len_h if len_h2 <= 0 else utl.clamp(len_h2, 2, self.len_h)
        self.step_y = 255.0 / (self.len_y - 1)
        self.step_s = 181.0 / (self.len_s - 1)
        self.step_h = 360.0 / (self.len_h - 1)
        self.step_h2 = 360.0 / (self.len_h2 - 1)
        
        print(f"[ACM] set variant lut len: y={self.len_y}, s={self.len_s}, h={self.len_h}, h2={self.len_h2}")
        
        # If LUTs are ready, resample them
        if self.b_lut_ready:
            # 1D LUTs
            if old_len_h != self.len_h:
                self.lut_delta_ybyh = linear_resize_array_1d(self.lut_delta_ybyh, self.len_h)
                self.lut_delta_sbyh = linear_resize_array_1d(self.lut_delta_sbyh, self.len_h)
                self.lut_delta_hbyh = linear_resize_array_1d(self.lut_delta_hbyh, self.len_h)
            
            # 2D LUTs - resize both dimensions if needed
            if old_len_h2 != self.len_h2 or old_len_y != self.len_y:
                self.lut_gain_ybyy = linear_resize_array_2d(self.lut_gain_ybyy, self.len_h2, self.len_y, kernel)
                self.lut_gain_sbyy = linear_resize_array_2d(self.lut_gain_sbyy, self.len_h2, self.len_y, kernel)
                self.lut_gain_hbyy = linear_resize_array_2d(self.lut_gain_hbyy, self.len_h2, self.len_y, kernel)
            
            if old_len_h2 != self.len_h2 or old_len_s != self.len_s:
                self.lut_gain_ybys = linear_resize_array_2d(self.lut_gain_ybys, self.len_h2, self.len_s, kernel)
                self.lut_gain_sbys = linear_resize_array_2d(self.lut_gain_sbys, self.len_h2, self.len_s, kernel)
                self.lut_gain_hbys = linear_resize_array_2d(self.lut_gain_hbys, self.len_h2, self.len_s, kernel)
        else:
            # Initialize empty LUTs
            self.lut_delta_ybyh = np.zeros(self.len_h, dtype=np.int16)
            self.lut_delta_sbyh = np.zeros(self.len_h, dtype=np.int16)
            self.lut_delta_hbyh = np.zeros(self.len_h, dtype=np.int16)
            self.lut_gain_ybyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
            self.lut_gain_sbyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
            self.lut_gain_hbyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
            self.lut_gain_ybys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)
            self.lut_gain_sbys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)
            self.lut_gain_hbys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)
            self.b_lut_ready = True


def test_interpolation():
    """Test interpolation functionality."""
    from acm_impl import AcmImpl
    from acm_evideo import AcmEVideo
    
    # Create source ACM with standard config
    source_acm = AcmImpl(9, 13, 65, 65)
    source_acm.gen_test_config(b_strict=True, random_seed=114514)
    
    # Create variant with smaller LUT
    variant = AcmImplVariant(5, 9, 33, 17)
    variant.interpolate_from(source_acm)
    
    # Dump results
    variant.dump_json("acm_variant_test.json")
    variant.dump_lut("test_lut_dump")
    
    print("Test completed successfully!")


if __name__ == '__main__':
    test_interpolation()
