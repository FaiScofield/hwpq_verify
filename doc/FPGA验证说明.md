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