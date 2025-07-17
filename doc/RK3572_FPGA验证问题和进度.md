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

## RGA (CfaDither)