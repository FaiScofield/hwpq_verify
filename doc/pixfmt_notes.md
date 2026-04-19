# 像素格式管理模块 (pixfmt) 文档

## 1. 整体介绍

`pixfmt` 模块是一个用于管理图像像素格式的完整系统，提供了格式定义、查询、转换等功能。该模块支持 RGB 和 YUV 两大系列的颜色格式，涵盖了从 1bpp 到 64bpp 的多种位深度。

### 1.1 核心数据结构

每个像素格式由 `pixfmt_attr_s` 结构体描述，包含以下关键信息：

- **fmt_id**: 格式枚举 ID
- **base_type**: 基础类型 (RGB/YUV)
- **layout**: 数据布局方式 (INTERLEAVED/PLANAR/SEMIPLANAR/TILE)
- **padding_pos**: Padding 位置 (NO_PADDING/AT_LSB/AT_MSB)
- **bitpacked_order**: 位打包顺序 (UNPACKED/BITPACKED_LSB/BITPACKED_MSB)
- **bpp**: 每像素位数 (bits per pixel)
- **depth**: 有效数据位深度
- **nb_comps**: 分量数量
- **full_name**: 完整名称
- **short_name**: 简短名称
- **alias**: 别名
- **desc**: 格式详细描述符 (RGB 或 YUV 特定)

### 1.2 格式分类

#### RGB 格式

目前都只支持交织排列

- **Unpacked 格式**: 每个分量独立字节，通道顺序按命名从低到高存储 (如 RGB888, RGBA8888)
- **Bitpacked 格式**: 多个分量紧凑打包，通道顺序按命名从高到低存储 (如 RGB565, RGBA5551, PIXFMT_RGBA1010102)
- **10LSB 格式**: 10bit 低位有效数据，6bit 高位填充，通道顺序按命名从低到高存储 (目前仅 PIXFMT_RGBA10Lsb)

#### YUV 格式

- **YUV444**: 无下采样，Y:U:V = 1:1:1
- **YUV422**: 水平 2:1 下采样
- **YUV420**: 水平和垂直 2:1 下采样
- **YUV411**: 水平 4:1 下采样
- **YUV410**: 水平和垂直 4:1 下采样
- **YUV400**: 仅亮度分量 (灰度图)

#### 布局方式

- **INTERLEAVED**: 交错存储 (如 YUYV)
- **PLANAR**: 平面存储 (如 YU12)
- **SEMIPLANAR**: 半平面存储 (如 NV12)
- **TILE**: 分块存储 (用于特定硬件优化)

---

## 2. 详细格式列表

### 2.1 RGB 格式

| fmt_id | drm_code | name (full/short/alias) | bpp | depth | nb_comps | padding_pos | bitpacked_order | desc |
|--------|----------|-------------------------|-----|-------|----------|-------------|-----------------|------|
| PIXFMT_RGB332 | DRM_FORMAT_RGB332 | rgb332 / rgb332 / - | 8 | 3 | 3 | NO_PADDING | BITPACKED_MSB | BGR order, 3:3:2 |
| PIXFMT_BGR233 | DRM_FORMAT_BGR233 | bgr233 / bgr233 / - | 8 | 3 | 3 | NO_PADDING | BITPACKED_MSB | RGB order, 2:3:3 |
| PIXFMT_RGB565 | DRM_FORMAT_RGB565 | rgb565 / rgb565 / - | 16 | 6 | 3 | NO_PADDING | BITPACKED_MSB | BGR order, 5:6:5 |
| PIXFMT_BGR565 | DRM_FORMAT_BGR565 | bgr565 / bgr565 / - | 16 | 6 | 3 | NO_PADDING | BITPACKED_MSB | RGB order, 5:6:5 |
| PIXFMT_RGBA5551 | DRM_FORMAT_RGBA5551 | rgba5551 / rgba5551 / - | 16 | 5 | 4 | NO_PADDING | BITPACKED_MSB | BGR order, Alpha@LSB, 5:5:5:1 |
| PIXFMT_ABGR1555 | DRM_FORMAT_ARGB1555 | abgr1555 / abgr1555 / - | 16 | 5 | 4 | NO_PADDING | BITPACKED_MSB | RGB order, Alpha@MSB, 1:5:5:5 |
| PIXFMT_RGBA4444 | DRM_FORMAT_RGBA4444 | rgba4444 / rgba4444 / - | 16 | 4 | 4 | NO_PADDING | BITPACKED_MSB | BGR order, Alpha@LSB, 4:4:4:4 |
| PIXFMT_ABGR4444 | DRM_FORMAT_ABGR4444 | abgr4444 / abgr4444 / - | 16 | 4 | 4 | NO_PADDING | BITPACKED_MSB | RGB order, Alpha@MSB, 4:4:4:4 |
| PIXFMT_RGB888 | DRM_FORMAT_BGR888 | rgb888 / rgb24 / rgb | 24 | 8 | 3 | NO_PADDING | UNPACKED | RGB order, 8:8:8 |
| PIXFMT_BGR888 | DRM_FORMAT_RGB888 | bgr888 / bgr24 / bgr | 24 | 8 | 3 | NO_PADDING | UNPACKED | BGR order, 8:8:8 |
| PIXFMT_RGBA8888 | DRM_FORMAT_ABGR8888 | rgba8888 / rgba32 / rgba | 32 | 8 | 4 | NO_PADDING | UNPACKED | RGB order, Alpha@LSB, 8:8:8:8 |
| PIXFMT_BGRA8888 | DRM_FORMAT_ARGB8888 | bgra8888 / bgra32 / bgra | 32 | 8 | 4 | NO_PADDING | UNPACKED | BGR order, Alpha@LSB, 8:8:8:8 |
| PIXFMT_ARGB8888 | DRM_FORMAT_BGRA8888 | argb8888 / argb32 / argb | 32 | 8 | 4 | NO_PADDING | UNPACKED | RGB order, Alpha@MSB, 8:8:8:8 |
| PIXFMT_ABGR8888 | DRM_FORMAT_RGBA8888 | abgr8888 / abgr32 / abgr | 32 | 8 | 4 | NO_PADDING | UNPACKED | BGR order, Alpha@MSB, 8:8:8:8 |
| PIXFMT_RGBA1010102 | DRM_FORMAT_RGBA1010102 | rgba1010102 / rgba1010102 / - | 32 | 10 | 4 | NO_PADDING | BITPACKED_MSB | BGR order, Alpha@LSB, 10:10:10:2 |
| PIXFMT_ABGR2101010 | DRM_FORMAT_ABGR2101010 | abgr2101010 / abgr2101010 / - | 32 | 10 | 4 | NO_PADDING | BITPACKED_MSB | RGB order, Alpha@MSB, 2:10:10:10 |
| PIXFMT_RGBA10Lsb | - | rgba10lsb / rgba64 / - | 64 | 10 | 4 | PADDING_AT_MSB | UNPACKED | RGB order, Alpha@MSB, 10:10:10:10 + 6bit padding |

### 2.3 YUV444 格式

| fmt_id | base_type | name (full/short/alias) | bpp | depth | nb_comps | layout | padding_pos | bitpacked_order | desc |
|--------|-----------|-------------------------|-----|-------|----------|--------|-------------|-----------------|------|
| PIXFMT_YUV444I_VU24 | YUV | yuv444i_vu24 / yuv444i_vu24 / - | 24 | 8 | 3 | INTERLEAVED | NO_PADDING | UNPACKED | V:U:Y 8:8:8, 1 plane |
| PIXFMT_YUV444I_VU30 | YUV | yuv444i_vu30 / yuv444i_vu30 / - | 30 | 10 | 3 | INTERLEAVED | NO_PADDING | BITPACKED_LSB | V:U:Y 10:10:10, 1 plane |
| PIXFMT_YUV444I_XV30 | YUV | yuv444i_xv30 / yuv444i_xv30 / - | 32 | 10 | 3 | INTERLEAVED | PADDING_AT_MSB | BITPACKED_LSB | X:V:Y:U 2:10:10:10, 1 plane |
| PIXFMT_YUV444I_10LSB | YUV | yuv444i_10lsb / yuv444i_10lsb / - | 48 | 10 | 3 | INTERLEAVED | PADDING_AT_MSB | UNPACKED | X6V10:X6U10:X6Y10, 1 plane |
| PIXFMT_YUV444P_YU24 | YUV | yuv444p_yu24 / yuv444p_yu24 / - | 24 | 8 | 3 | PLANAR | NO_PADDING | UNPACKED | Y8-U8-V8, 3 planes |
| PIXFMT_YUV444P_YV24 | YUV | yuv444p_yv24 / yuv444p_yv24 / - | 24 | 8 | 3 | PLANAR | NO_PADDING | UNPACKED | Y8-V8-U8, 3 planes |
| PIXFMT_YUV444P_10LSB | YUV | yuv444p_10lsb / yuv444p_10lsb / - | 48 | 10 | 3 | PLANAR | PADDING_AT_MSB | UNPACKED | X6Y10-X6U10-X6V10, 3 planes |
| PIXFMT_YUV444SP_NV24 | YUV | yuv444sp_nv24 / yuv444sp_nv24 / - | 24 | 8 | 3 | SEMIPLANAR | NO_PADDING | UNPACKED | Y8-U8/V8, 2 planes |
| PIXFMT_YUV444SP_NV42 | YUV | yuv444sp_nv42 / yuv444sp_nv42 / - | 24 | 8 | 3 | SEMIPLANAR | NO_PADDING | UNPACKED | Y8-V8/U8, 2 planes |
| PIXFMT_YUV444SP_NV30 | YUV | yuv444sp_nv30 / nv30 / - | 30 | 10 | 3 | SEMIPLANAR | NO_PADDING | UNPACKED | Y10-U10/V10, 2 planes |
| PIXFMT_YUV444SP_10LSB | YUV | yuv444sp_10lsb / yuv444sp_10lsb / - | 48 | 10 | 3 | SEMIPLANAR | PADDING_AT_MSB | UNPACKED | X6Y10-X6U10/X6V10, 2 planes |

### 2.4 YUV422 格式

| fmt_id | base_type | name (full/short/alias) | bpp | depth | nb_comps | layout | padding_pos | bitpacked_order | desc |
|--------|-----------|-------------------------|-----|-------|----------|--------|-------------|-----------------|------|
| PIXFMT_YUV422I_YUYV | YUV | yuv422i_yuyv / yuyv / yuv422i | 16 | 8 | 3 | INTERLEAVED | NO_PADDING | UNPACKED | V0:Y1:U0:Y0 8:8:8:8 |
| PIXFMT_YUV422I_YVYU | YUV | YUV422 Interleaved YVYU / yvyu / - | 16 | 8 | 3 | INTERLEAVED | NO_PADDING | UNPACKED | U0:Y1:V0:Y0 8:8:8:8 |
| PIXFMT_YUV422I_UYVY | YUV | yuv422i_uyvy / uyvy / - | 16 | 8 | 3 | INTERLEAVED | NO_PADDING | UNPACKED | Y1:V0:Y1:U0 8:8:8:8 |
| PIXFMT_YUV422I_VYUY | YUV | YUV422 Interleaved VYUY / vyuy / - | 16 | 8 | 3 | INTERLEAVED | NO_PADDING | UNPACKED | Y1:U0:Y1:V0 8:8:8:8 |
| PIXFMT_YUV422I_Y210 | YUV | YUV422 Interleaved Y210 / y210 / - | 32 | 10 | 3 | INTERLEAVED | NO_PADDING | UNPACKED | V0:X:Y1:X:U0:X:Y0:X 10:6:10:6:10:6:10:6 |
| PIXFMT_YUV422I_Y212 | YUV | YUV422 Interleaved Y212 / y212 / - | 32 | 12 | 3 | INTERLEAVED | NO_PADDING | UNPACKED | V0:X:Y1:X:U0:X:Y0:X 12:4:12:4:12:4:12:4 |
| PIXFMT_YUV422I_Y216 | YUV | YUV422 Interleaved Y216 / y216 / - | 32 | 16 | 3 | INTERLEAVED | NO_PADDING | UNPACKED | V0:Y1:U0:Y0 16:16:16:16 |
| PIXFMT_YUV422P_YU16 | YUV | YUV422 Planar YU16 / yu16 / - | 16 | 8 | 3 | PLANAR | NO_PADDING | UNPACKED | Y8-U8-V8, 3 planes |
| PIXFMT_YUV422P_YV16 | YUV | YUV422 Planar YV16 / yv16 / - | 16 | 8 | 3 | PLANAR | NO_PADDING | UNPACKED | Y8-V8-U8, 3 planes |
| PIXFMT_YUV422P_10LSB | YUV | yuv422p_10lsb / yuv422p_10lsb / - | 32 | 10 | 3 | PLANAR | PADDING_AT_MSB | UNPACKED | X6Y10-X6U10-X6V10, 3 planes |
| PIXFMT_YUV422SP_NV16 | YUV | yuv422sp_nv16 / nv16 / yuv422sp | 16 | 8 | 3 | SEMIPLANAR | NO_PADDING | UNPACKED | Y8-U8/V8, 2 planes |
| PIXFMT_YUV422SP_NV61 | YUV | YUV422 Semi-Planar NV61 / nv61 / - | 16 | 8 | 3 | SEMIPLANAR | NO_PADDING | UNPACKED | Y8-V8/U8, 2 planes |
| PIXFMT_YUV422SP_NV20 | YUV | YUV422 Semi-Planar NV20 / nv20 / - | 20 | 10 | 3 | SEMIPLANAR | NO_PADDING | UNPACKED | Y10-U10/V10, 2 planes |
| PIXFMT_YUV422SP_10LSB | YUV | yuv422sp_10lsb / yuv422sp_10lsb / - | 32 | 10 | 3 | SEMIPLANAR | PADDING_AT_MSB | UNPACKED | X6Y10-X6U10/X6V10, 2 planes |

### 2.5 YUV420 格式

| fmt_id | base_type | name (full/short/alias) | bpp | depth | nb_comps | layout | padding_pos | bitpacked_order | desc |
|--------|-----------|-------------------------|-----|-------|----------|--------|-------------|-----------------|------|
| PIXFMT_YUV420P_YU12 | YUV | yuv420p_yu12 / yu12 / yuv420p | 12 | 8 | 3 | PLANAR | NO_PADDING | UNPACKED | Y8-U8-V8, 3 planes |
| PIXFMT_YUV420P_YV12 | YUV | yuv420p_yv12 / yv12 / - | 12 | 8 | 3 | PLANAR | NO_PADDING | UNPACKED | Y8-V8-U8, 3 planes |
| PIXFMT_YUV420P_10LSB | YUV | yuv420p_10lsb / yuv420p_10lsb / - | 24 | 10 | 3 | PLANAR | PADDING_AT_MSB | UNPACKED | X6Y10-X6U10-X6V10, 3 planes |
| PIXFMT_YUV420SP_NV12 | YUV | yuv420sp_nv12 / nv12 / yuv420sp | 12 | 8 | 3 | SEMIPLANAR | NO_PADDING | UNPACKED | Y8-U8/V8, 2 planes |
| PIXFMT_YUV420SP_NV21 | YUV | YUV420 Semi-Planar NV21 / nv21 / - | 12 | 8 | 3 | SEMIPLANAR | NO_PADDING | UNPACKED | Y8-V8/U8, 2 planes |
| PIXFMT_YUV420SP_NV15 | YUV | YUV420 Semi-Planar NV15 / nv15 / - | 15 | 10 | 3 | SEMIPLANAR | NO_PADDING | UNPACKED | Y10-U10/V10, 2 planes |
| PIXFMT_YUV420SP_10LSB | YUV | yuv420sp_10lsb / yuv420sp_10lsb / - | 24 | 10 | 3 | SEMIPLANAR | PADDING_AT_MSB | UNPACKED | X6Y10-X6U10/X6V10, 2 planes |

### 2.6 YUV411 格式

| fmt_id | base_type | name (full/short/alias) | bpp | depth | nb_comps | layout | padding_pos | bitpacked_order | desc |
|--------|-----------|-------------------------|-----|-------|----------|--------|-------------|-----------------|------|
| PIXFMT_YUV411P_YU11 | YUV | YUV411 Planar YU11 / yu11 / - | 12 | 8 | 3 | PLANAR | NO_PADDING | UNPACKED | Y8-U8-V8, 3 planes, H:4:1 subsampling |
| PIXFMT_YUV411P_YV11 | YUV | YUV411 Planar YV11 / yv11 / - | 12 | 8 | 3 | PLANAR | NO_PADDING | UNPACKED | Y8-V8-U8, 3 planes, H:4:1 subsampling |

### 2.7 YUV410 格式

| fmt_id | base_type | name (full/short/alias) | bpp | depth | nb_comps | layout | padding_pos | bitpacked_order | desc |
|--------|-----------|-------------------------|-----|-------|----------|--------|-------------|-----------------|------|
| PIXFMT_YUV410P_YUV9 | YUV | YUV410 Planar YUV9 / yuv9 / - | 9 | 8 | 3 | PLANAR | NO_PADDING | UNPACKED | Y8-U8-V8, 3 planes, H:V:4:1 subsampling |
| PIXFMT_YUV410P_YVU9 | YUV | YUV410 Planar YVU9 / yvu9 / - | 9 | 8 | 3 | PLANAR | NO_PADDING | UNPACKED | Y8-V8-U8, 3 planes, H:V:4:1 subsampling |

### 2.8 YUV400 (灰度) 格式

| fmt_id | base_type | name (full/short/alias) | bpp | depth | nb_comps | layout | padding_pos | bitpacked_order | desc |
|--------|-----------|-------------------------|-----|-------|----------|--------|-------------|-----------------|------|
| PIXFMT_YUV400_R1 | YUV | YUV400 R1 / yuv400_r1 / - | 1 | 1 | 1 | PLANAR | NO_PADDING | UNPACKED | 1bit grayscale, bitpacked |
| PIXFMT_YUV400_R2 | YUV | YUV400 R2 / yuv400_r2 / - | 2 | 2 | 1 | PLANAR | NO_PADDING | UNPACKED | 2bit grayscale, bitpacked |
| PIXFMT_YUV400_R4 | YUV | YUV400 R4 / yuv400_r4 / - | 4 | 4 | 1 | PLANAR | NO_PADDING | UNPACKED | 4bit grayscale, bitpacked |
| PIXFMT_YUV400_R8 | YUV | YUV400 R8 / yuv400_r8 / - | 8 | 8 | 1 | PLANAR | NO_PADDING | UNPACKED | 8bit grayscale |
| PIXFMT_YUV400_R10 | YUV | YUV400 R10 / yuv400_r10 / - | 16 | 10 | 1 | PLANAR | NO_PADDING | UNPACKED | 10bit grayscale + 6bit padding |
| PIXFMT_YUV400_R12 | YUV | YUV400 R12 / yuv400_r12 / - | 16 | 12 | 1 | PLANAR | NO_PADDING | UNPACKED | 12bit grayscale + 4bit padding |
| PIXFMT_YUV400_R16 | YUV | YUV400 R16 / yuv400_r16 / - | 16 | 16 | 1 | PLANAR | NO_PADDING | UNPACKED | 16bit grayscale |

### 2.9 YUV Tile 格式

| fmt_id | base_type | name (full/short/alias) | bpp | depth | nb_comps | layout | padding_pos | bitpacked_order | desc |
|--------|-----------|-------------------------|-----|-------|----------|--------|-------------|-----------------|------|
| PIXFMT_YUV444SP_TILE4x4 | YUV | YUV444 Semi-Planar Tile 4x4 / yuv444sp_tile4x4 / - | 24 | 8 | 3 | TILE | NO_PADDING | UNPACKED | Tile for NV24, 16+32=48 bytes/tile |
| PIXFMT_YUV422SP_TILE4x4 | YUV | YUV422 Semi-Planar Tile 4x4 / yuv422sp_tile4x4 / - | 16 | 8 | 3 | TILE | NO_PADDING | UNPACKED | Tile for NV16, 16+16=32 bytes/tile |
| PIXFMT_YUV420SP_TILE4x4 | YUV | yuv420sp_tile4x4 / yuv420sp_tile4x4 / - | 12 | 8 | 3 | TILE | NO_PADDING | UNPACKED | Tile for NV12, 16+8=24 bytes/tile |

---

## 3. 格式命名规则说明

### 3.1 RGB 格式命名

- **RGB/BGR**: 表示通道顺序
- **数字后缀**: 表示每个通道的位数 (如 888=8:8:8, 565=5:6:5)
- **A 的位置**:
  - ARGB/ABGR: Alpha 在 MSB
  - RGBA/BGRA: Alpha 在 LSB
- **Lsb 后缀**: 表示 10bit 有效数据，MSB 有 padding

### 3.2 YUV 格式命名

- **YUV444/422/420/411/410**: 表示色度下采样方式
- **I/P/SP**:
  - I = Interleaved (交错)
  - P = Planar (平面)
  - SP = Semi-Planar (半平面)
- **YU/VU**: 表示 UV 分量的顺序
- **NV12/NV21 等**: Semi-planar 格式的 DRM 标准命名
- **10LSB**: 10bit 有效数据，LSB 对齐，MSB 有 padding

---

## 4. 使用示例

### 4.1 查询格式信息

```c
const pixfmt_attr_s *attr = pixfmt_get_attr(PIXFMT_RGB888);
printf("Format: %s (%s)\n", attr->full_name, attr->short_name);
printf("BPP: %d, Depth: %d, Components: %d\n", attr->bpp, attr->depth, attr->nb_comps);
```

### 4.2 计算帧大小

```c
size_t frame_size = pixfmt_get_frame_size(PIXFMT_NV12, 1920, 1080, 0);
printf("Frame size for 1920x1080 NV12: %zu bytes\n", frame_size);
```

### 4.3 获取平面信息

```c
int nb_planes = pixfmt_nb_planes(PIXFMT_YUV420P_YU12);
printf("YU12 has %d planes\n", nb_planes);

int pitches[3];
pixfmt_get_min_pitches(PIXFMT_YUV420P_YU12, 1920, pitches);
printf("Y plane pitch: %d bytes\n", pitches[0]);
```

---

## 5. 注意事项

1. **位深度对齐**: 对于 10LSB 格式，实际存储为 16bit，其中高 6bit 为 padding
2. **平面布局**: PLANAR 格式每个分量独立存储，SEMIPLANAR 格式 Y 分量独立，UV 分量交错
3. **Tile 格式**: 用于特定硬件优化，访问时需要考虑 tile 布局
4. **字节序**: 所有格式均假设小端字节序
5. **DRM 兼容性**: 大部分格式与 DRM FourCC 标准兼容，具体映射见 `pixfmt_to_drm_fourcc()`
