# FPGA 验证说明

## 1. 环境准备

相关软件放于路径 `\\172.16.4.246\vop\3572_pq环境\fpag_software`
参考文件夹内`Marsvip S2800Hard平台使用说明.pdf`，安装FPGA开发板驱动、cygwin环境、ARMDS IDE等。

安装问题：

- `QuartusProProgrammer` 安装后 `JTAG` 驱动安装失败。
  1. 搜索驱动安装日志，一般是`C:\Windows\INF\setupapi.dev.log`，查看文件末尾部分的日志，找到和安装时间对应的部分日志信息。
  2. 将日志信息发给AI分析，可能会告诉你原因是: **​​证书过期​​** (0x800B0101) + **根证书不受信任​**(0x800B0109) + **Windows强制验证签名** 导致
  3. 解决办法之一是：[禁用驱动签名强制验证](https://zhuanlan.zhihu.com/p/622920268) ，之后再重新安装驱动。
  4. 重新安装驱动无需再安装一次`QuartusProProgrammer`，可以直接启动已解压好的驱动安装器： `xxx\intelFPGA_pro\20.1\qprogrammer\quartus\drivers\DPInst.exe`

- ArmDS 调试时提示`Unable to connect to New_configuration.`, `Licensed number of users already reached`的错误。
  - 系 license 同时使用数量达到上限，等待别人退出使用，或切换到其他网段.
  - `8224@172.16.11.206`
  - `8224@172.16.12.252`
  - `8224@172.16.13.206`

## Debug方法
### CRC 校验
- 开关寄存器: `0xf9000C40(POST0_CTRL.POST_SCL_CTRL.crc_en)`
- 读取CRC值: `0xf9000C28(POST0_CTRL.POST_CRC_OUT)`
  ```c
      // enable CRC. POST0_CTRL.POST_SCL_CTRL.crc_en
      word32(VOPLITE_BASE + VOP3_POST0_CTRL_BASE + 0x40) = 0x0100;
      int crc = word32(VOPLITE_BASE + VOP3_POST0_CTRL_BASE + 0x28);
  ```

### DEBUG_POINT 查看像素值
- 开关寄存器: `0x5400(ACM.ACM_CTRL.debug_en)`
- 支持同时查看4个像素的像素值，设置 `0x6410(ACM.DEBUG_POINT0_CFG)` ~ `0x641C(ACM.DEBUG_POINT3_CFG)`
- 显示结果位于`0x6430(ACM.DEBUG0_DATA0)` ~ `0x646C(ACM.DEBUG3_DATA3)`



## 错误

### SharpLite 开关时会抖动

### SharpLite CRC 不对

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

### ACM 开关 左侧有部分列像素值没有变化，看起来像横条线
- 大部分是 delay_num 原因
- 还在排除中