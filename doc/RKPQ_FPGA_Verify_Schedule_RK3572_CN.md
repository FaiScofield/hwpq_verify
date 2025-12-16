# RK3572 FPGA 验证问题和进度

## VOP (SharpLite / ACM / CSC)

### 【验证中】 SharpLite 开关时会抖动

怀疑是时序问题

### 【验证中】【配置问题】 SharpLite CRC 不对

- 输入的NV24格式需要交换UV通道(`POST0_CTRL.POST_SCL_CTRL.crc_en=1`)，VOP输出需要设为10bit(`dsp_out_mode=0xF`)
- 20250716 批量2000组参数单输入验证CRC一致

### 【已解决】【遗留问题】 反馈ACM部分查表没有镜像导致时序刷新不支持动态配置的问题

- `ACM.DELTA_RANGE`寄存器没有镜像，配置该寄存器会实时刷新效果，导致帧级参数不一致的问题
- 配置该寄存器后看是否需要 cfg_done 才生效，如果是就符合预期，认为pass
- 20250708 经过测试，结果符合预期，问题已修正。

### 【已解决】【配置问题】 ACM 开关 左侧有部分列像素值没有变化，看起来像横条线

- 配置错误。ACM开启后 `POST0_CTRL.POST_ACM_CTRL.acm_bypass_en` 需要关掉。
- 20250707 关掉后左侧横线条消失。

### 【已解决】【BUG】 ACM 开关 左侧有部分列像素值没有变化，看起来像横条线

- 接上个问题，`POST0_CTRL.POST_ACM_CTRL.acm_bypass_en` 关掉后，画面像素有细小的偏移，经过IC确认是bug.
- 20250707 发布新的固件已解决该问题。

### 【验证中】CSC 批仿

## VDPP

1. 新模块功能测试
   - VEP通路的 金字塔Pyramid，  pass
   - VEP通路的 黑边检测BBD，  pass  （由于输入可能是LimitedRange, BBD的检测阈值（统一按Fullrange设定）要转到LimitedRange再传给寄存器，在驱动内完成。）
   - DCI_HIST通路的黑边检测BBD，
     - 由于DCI平均/间隔取数， 检测结果跟实际结果存在一个倍率关系，这个倍率等于采样间隔。 目前是在驱动层面将结果回乘，这样和实际结果最多有3个像素的误差。
     - 由于DCI 通路存在CSC一定会将输入转为 YUV Fullrange， 所以BBD的检测阈值跟VEP通路不一样，不需要做F2L。

2. 直方图结果核验
   - 测了 rgb888, Y8, Y10(packed)  格式的输出并和cmodel对比，pass
   - 测了1080P VEP通路 pass
   - 测了4K  DCI_HIST通路 pass

## RGA (CfaDither)
