# RK3572 FPGA 验证问题和进度

## VOP (SharpLite / ACM / CSC)

### 【验证中】 SharpLite 开关时会抖动
怀疑是时序问题

### 【验证中】 SharpLite CRC 不对

fpga输入文件： `vop/sharplite/test_1920x1080_tl_roi_720x480_nv24.yuv` (左上角ROI: [0,0,720,480])
cmodel输入文件: `data/test_1920x1080_tl_roi_720x480_yuv444p.yuv`
cmodel输出文件: `Data/test_out_1920x1080_yuv444p10le.yuv`

- ✅ 锐化ROI在纯色区域，开关Sharp模块CRC值应保持一致
  - sharp_en=0x1, peacking_gain=0x100300 , roi=[500,600,1200,900] (0x825801F4, 0x038404B0), CRC=0x9FC471FB / 0x9fc471fb
  - sharp_en=0x0, peacking_gain=0x100300 , roi=[500,600,1200,900] (0x825801F4, 0x038404B0), CRC=0x9FC471FB / 0x9fc471fb
- ❌ 锐化ROI包含一部分有效区域，开关Sharp模块CRC值应不相等
  - sharp_en=0x1, peacking_gain=0x100300 , roi=[500,400,1200,500] (0x819001F4, 0x01F404B0),  CRC=0x9A05C0D4 / 0x8a17f16e
  - sharp_en=0x0, peacking_gain=0x100300 , roi=[500,400,1200,500] (0x819001F4, 0x01F404B0),  CRC=0x9FC471FB
- ✅ 锐化ROI关闭（作用全图），`peacking_gain=0`，开关Sharp模块CRC值应保持一致
  - sharp_en=0x1, peacking_gain=0x100000 , roi=OFF (0x00000000, 0x038404B0), CRC=0x9FC471FB / 0x9fc471fb
  - sharp_en=0x0, peacking_gain=0x100300 , roi=OFF (0x00000000, 0x038404B0), CRC=0x9FC471FB / 0x9fc471fb
  - 0x7B63B960

- roi=x_start=717=02cd, crc fpga/cmodel = **0xDCB509B1** / **0xc9a9d6de** ❌ pixel values:
  - 0x01DF02CC(x=716,y=479): 0A0/214/1F8 ✅
  - 0x01DF02CD(x=717,y=479): 032/21C/1F4 ✅
  - 0x01DF02CE(x=718,y=479): 0AC/21C/1F4 ✅
  - 0x01DF02CF(x=719,y=479): 008/21C/1F4 ✅
  - 0x01DF02D0(x=720,y=479): 208/208/230 ✅
  - 0x01DF02D1(x=721,y=479): 190/208/230 ✅
  - 0x01E002CC(x=716,y=480): 190/208/230 ✅
  - 0x01E002CD(x=717,y=480): 26E/208/230 ✅
  - 0x01E002CE(x=718,y=480): 244/208/230 ✅
  - 0x01E002CF(x=719,y=480): 1F0/208/230 ✅
  - 0x01E002D0(x=720,y=480): 190/208/230 ✅
  - 0x01E002D1(x=721,y=480): 190/208/230 ✅
  - 0x01DE02CC(x=716,y=478): 07C/208/208 ✅
  - 0x01DE02CD(x=717,y=478): 080/210/200 ✅
  - 0x01DE02CE(x=718,y=478): 090/210/200 ✅
  - 0x01DE02CF(x=719,y=478): 098/210/200 ✅
  - 0x01DE02D0(x=720,y=478): 190/208/230 ✅
  - 0x01DE02D1(x=721,y=478): 190/208/230 ✅

- roi=x_start=718=02ce, crc fpga/cmodel = 0x6BDD7D21 / 0x6bdd7d21 ✅
  - 0x27d06c20:  0x00000010 0x00200010 0x00200010 0x81df02ce
  - 0x27d06c30:  0x03200320 0x80000000 0x00000000 0x00000000

- roi=x_start=720=02d0, crc fpga/cmodel = 0x2328484E / 0x2328484e ✅
  - 0x27d06c20:  0x00000010 0x00200010 0x00200010 0x81df02d0
  - 0x27d06c30:  0x03200320 0x80000000 0x00000000 0x00000000

- roi=x_start=721=02d1, crc fpga/cmodel = 0x9FC471FB / 0x9fc471fb ✅
  - 0x27d06c00:  0x00000001 0x00000000 0x00000000 0x00000000
  - 0x27d06c10:  0x00100300 0x00402010 0x00000000 0x00000000
  - 0x27d06c20:  0x00000010 0x00200010 0x00200010 0x81df02d1
  - 0x27d06c30:  0x03200320 0x80000000 0x00000000 0x00000000



### 【已解决】【遗留问题】 反馈ACM部分查表没有镜像导致时序刷新不支持动态配置的问题
- `ACM.DELTA_RANGE`寄存器没有镜像，配置该寄存器会实时刷新效果，导致帧级参数不一致的问题
- 配置该寄存器后看是否需要 cfg_done 才生效，如果是就符合预期，认为pass
- 20250708经过测试，结果符合预期，问题已修正。

### 【已解决】【配置问题】 ACM 开关 左侧有部分列像素值没有变化，看起来像横条线
- 配置错误。ACM开启后 `POST0_CTRL.POST_ACM_CTRL.acm_bypass_en` 需要关掉。
- 20250707 关掉后左侧横线条消失。

### 【已解决】【BUG】 ACM 开关 左侧有部分列像素值没有变化，看起来像横条线
- 接上个问题，`POST0_CTRL.POST_ACM_CTRL.acm_bypass_en` 关掉后，画面像素有细小的偏移，经过IC确认是bug.
- 20250707发布新的固件已解决该问题。



## RGA (CfaDither)