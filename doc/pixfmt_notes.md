# 像素格式管理模块 (pixfmt) 文档

## 1. 整体介绍

`pixfmt` 模块是一个用于管理图像像素格式的完整系统，提供了格式定义、查询、转换等功能。该模块支持 RGB 和 YUV 两大系列的颜色格式，涵盖了从 1bpp 到 64bpp 的多种位深度。

### 1.1 核心数据结构

每个像素格式由 `pixfmt_attr_s` 结构体描述，包含以下关键信息：

- **fmt_id**: 格式枚举 ID
- **base_type**: 基础类型 (RGB/YUV)
- **layout**: 数据布局方式 (INTERLEAVED/PLANAR/SEMIPLANAR/TILE)
- **padding_pos**: Padding 位置 (NO_PADDING/AT_LSB/AT_MSB)
- **bitpacked_order**: 位打包顺序 (false/true/true)
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

- **false 格式**: 每个分量独立字节，通道顺序按命名从低到高存储 (如 RGB888, RGBA8888)
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

| fmt_id | drm_code | name (full/short/alias) | bpp | depth | nb_comps | padding_pos | is_bitpacked | desc |
|--------|----------|-------------------------|-----|-------|----------|-------------|-----------------|------|
| PIXFMT_RGB332 | DRM_FORMAT_RGB332 | rgb332 / rgb332 / - | 8 | 3 | 3 | NO_PADDING | true | order: BGR 2:3:3 |
| PIXFMT_BGR233 | DRM_FORMAT_BGR233 | bgr233 / bgr233 / - | 8 | 3 | 3 | NO_PADDING | true | order: RGB 3:3:2 |
| PIXFMT_RGB565 | DRM_FORMAT_RGB565 | rgb565 / rgb565 / - | 16 | 6 | 3 | NO_PADDING | true | order: BGR 5:6:5 |
| PIXFMT_BGR565 | DRM_FORMAT_BGR565 | bgr565 / bgr565 / - | 16 | 6 | 3 | NO_PADDING | true | order: RGB 5:6:5 |
| PIXFMT_RGBA5551 | DRM_FORMAT_RGBA5551 | rgba5551 / rgba5551 / - | 16 | 5 | 4 | NO_PADDING | true | order: ABGR 1:5:5:5 |
| PIXFMT_ABGR1555 | DRM_FORMAT_ARGB1555 | abgr1555 / abgr1555 / - | 16 | 5 | 4 | NO_PADDING | true | order: RGBA 5:5:5:1 |
| PIXFMT_RGBA4444 | DRM_FORMAT_RGBA4444 | rgba4444 / rgba4444 / - | 16 | 4 | 4 | NO_PADDING | true | order: ABGR 4:4:4:4 |
| PIXFMT_ABGR4444 | DRM_FORMAT_ABGR4444 | abgr4444 / abgr4444 / - | 16 | 4 | 4 | NO_PADDING | true | order: RGBA 4:4:4:4 |
| PIXFMT_RGB888 | DRM_FORMAT_BGR888 | rgb888 / rgb24 / rgb | 24 | 8 | 3 | NO_PADDING | false | order: RGB 8:8:8 |
| PIXFMT_BGR888 | DRM_FORMAT_RGB888 | bgr888 / bgr24 / bgr | 24 | 8 | 3 | NO_PADDING | false | order: BGR 8:8:8 |
| PIXFMT_RGBA8888 | DRM_FORMAT_ABGR8888 | rgba8888 / rgba32 / rgba | 32 | 8 | 4 | NO_PADDING | false | order: RGBA 8:8:8:8 |
| PIXFMT_BGRA8888 | DRM_FORMAT_ARGB8888 | bgra8888 / bgra32 / bgra | 32 | 8 | 4 | NO_PADDING | false | order: BGRA 8:8:8:8 |
| PIXFMT_ARGB8888 | DRM_FORMAT_BGRA8888 | argb8888 / argb32 / argb | 32 | 8 | 4 | NO_PADDING | false | order: ARGB 8:8:8:8 |
| PIXFMT_ABGR8888 | DRM_FORMAT_RGBA8888 | abgr8888 / abgr32 / abgr | 32 | 8 | 4 | NO_PADDING | false | order: ABGR 8:8:8:8 |
| PIXFMT_RGBA1010102 | DRM_FORMAT_RGBA1010102 | rgba1010102 / rgba1010102 / - | 32 | 10 | 4 | NO_PADDING | true | order: ABGR 2:10:10:10 |
| PIXFMT_ABGR2101010 | DRM_FORMAT_ABGR2101010 | abgr2101010 / abgr2101010 / - | 32 | 10 | 4 | NO_PADDING | true | order: RGBA 10:10:10:2 |
| PIXFMT_RGBA10Lsb | -                        | rgba10l / rgba10l / - | 64 | 10 | 4 | PADDING_AT_MSB | false | order: RGBA 10:10:10:10 with 6bit padding@MSB |

### 2.2 YUV Raster 格式

| fmt_id | drm_code | name (full/short/alias) | bpp | depth | nb_comps | layout | padding_pos | is_bitpacked | desc |
|--------|----------|-------------------------|-----|-------|----------|--------|-------------|-----------------|------|
| PIXFMT_YUV444I_VU24 | DRM_FORMAT_VUY888 | yuv444i8 / vu24 / yuv444i_vu24 | 24 | 8 | 3 | INTERLEAVED | NO_PADDING | false | sampling: 4:4:4, order: yuv |
| PIXFMT_YUV444I_VU30 | DRM_FORMAT_VUY101010 | yuv444i10bp / vu30 / yuv444i_vu30 | 30 | 10 | 3 | INTERLEAVED | NO_PADDING | true | sampling: 4:4:4, order: yuv |
| PIXFMT_YUV444I_XV30 | DRM_FORMAT_XVYU2101010 | uyv444i10bpl / xv30 / yuv444i_xv30, uyvx444i10bp | 32 | 10 | 3 | INTERLEAVED | PADDING_AT_MSB | true | sampling: 4:4:4, order: uyv |
| PIXFMT_YUV444I_10LSB | -                | yuv444i10l / yuv444i10l / yuv444i_10lsb | 48 | 10 | 3 | INTERLEAVED | PADDING_AT_MSB | false | sampling: 4:4:4, order: yuv |
| PIXFMT_YUV444P_YU24 | DRM_FORMAT_YUV444 | yuv444p8 / yu24 / yuv444p_yu24 | 24 | 8 | 3 | PLANAR | NO_PADDING | false | sampling: 4:4:4, order: yuv |
| PIXFMT_YUV444P_YV24 | DRM_FORMAT_YVU444 | yvu444p8 / yv24 / yuv444p_yv24 | 24 | 8 | 3 | PLANAR | NO_PADDING | false | sampling: 4:4:4, order: yvu |
| PIXFMT_YUV444P_10LSB | -                | yuv444p10l / yuv444p10l / yuv444p_10lsb | 48 | 10 | 3 | PLANAR | PADDING_AT_MSB | false | sampling: 4:4:4, order: yuv |
| PIXFMT_YUV444SP_NV24 | DRM_FORMAT_NV24 | yuv444sp8 / nv24 / yuv444sp_nv24 | 24 | 8 | 3 | SEMIPLANAR | NO_PADDING | false | sampling: 4:4:4, order: yuv |
| PIXFMT_YUV444SP_NV42 | DRM_FORMAT_NV42 | yvu444sp8 / nv42 / yuv444sp_nv42 | 24 | 8 | 3 | SEMIPLANAR | NO_PADDING | false | sampling: 4:4:4, order: yvu |
| PIXFMT_YUV444SP_NV30 | DRM_FORMAT_NV30 | yuv444sp10bp / nv30 / yuv444sp_nv30 | 30 | 10 | 3 | SEMIPLANAR | NO_PADDING | true | sampling: 4:4:4, order: yuv |
| PIXFMT_YUV444SP_10LSB | -              | yuv444sp10l / yuv444sp10l / yuv444sp_10lsb | 48 | 10 | 3 | SEMIPLANAR | PADDING_AT_MSB | false | sampling: 4:4:4, order: yuv |
| PIXFMT_YUV422I_YUYV | DRM_FORMAT_YUYV | yuyv422i8 / yuyv / yuv422i_yuyv | 16 | 8 | 3 | INTERLEAVED | NO_PADDING | false | sampling: 4:2:2, order: yuyv |
| PIXFMT_YUV422I_YVYU | DRM_FORMAT_YVYU | yvyu422i8 / yvyu / yuv422i_yvyu | 16 | 8 | 3 | INTERLEAVED | NO_PADDING | false | sampling: 4:2:2, order: yvyu |
| PIXFMT_YUV422I_UYVY | DRM_FORMAT_UYVY | uyvy422i8 / uyvy / yuv422i_uyvy | 16 | 8 | 3 | INTERLEAVED | NO_PADDING | false | sampling: 4:2:2, order: uyvy |
| PIXFMT_YUV422I_VYUY | DRM_FORMAT_VYUY | vyuy422i8 / vyuy / yuv422i_vyuy | 16 | 8 | 3 | INTERLEAVED | NO_PADDING | false | sampling: 4:2:2, order: vyuy |
| PIXFMT_YUV422I_Y210 | DRM_FORMAT_Y210 | yuyv422i10m / y210 / yuv422i_y210 | 32 | 10 | 3 | INTERLEAVED | PADDING_AT_LSB | false | sampling: 4:2:2, order: yuyv |
| PIXFMT_YUV422I_Y212 | DRM_FORMAT_Y212 | yuyv422i12m / y212 / yuv422i_y212 | 32 | 12 | 3 | INTERLEAVED | PADDING_AT_LSB | false | sampling: 4:2:2, order: yuyv |
| PIXFMT_YUV422I_Y216 | DRM_FORMAT_Y216 | yuyv422i16 / y216 / yuv422i_y216 | 32 | 16 | 3 | INTERLEAVED | NO_PADDING | false | sampling: 4:2:2, order: yuyv |
| PIXFMT_YUV422P_YU16 | DRM_FORMAT_YUV422 | yuv422p8 / yu16 / yuv422p_yu16 | 16 | 8 | 3 | PLANAR | NO_PADDING | false | sampling: 4:2:2, order: yuv |
| PIXFMT_YUV422P_YV16 | DRM_FORMAT_YVU422 | yvu422p8 / yv16 / yuv422p_yv16 | 16 | 8 | 3 | PLANAR | NO_PADDING | false | sampling: 4:2:2, order: yvu |
| PIXFMT_YUV422P_10LSB | -               | yuv422p10l / yuv422p10l / yuv422p_10lsb | 32 | 10 | 3 | PLANAR | PADDING_AT_MSB | false | sampling: 4:2:2, order: yuv |
| PIXFMT_YUV422SP_NV16 | DRM_FORMAT_NV16 | yuv422sp8 / nv16 / yuv422sp_nv16 | 16 | 8 | 3 | SEMIPLANAR | NO_PADDING | false | sampling: 4:2:2, order: yuv |
| PIXFMT_YUV422SP_NV61 | DRM_FORMAT_NV61 | yvu422sp8 / nv61 / yuv422sp_nv61 | 16 | 8 | 3 | SEMIPLANAR | NO_PADDING | false | sampling: 4:2:2, order: yvu |
| PIXFMT_YUV422SP_NV20 | DRM_FORMAT_NV20 | yuv422sp10bp / nv20 / yuv422sp_nv20 | 20 | 10 | 3 | SEMIPLANAR | NO_PADDING | true | sampling: 4:2:2, order: yuv |
| PIXFMT_YUV422SP_10LSB | -              | yuv422sp10l / yuv422sp10l / yuv422sp_10lsb | 32 | 10 | 3 | SEMIPLANAR | PADDING_AT_MSB | false | sampling: 4:2:2, order: yuv |
| PIXFMT_YUV420P_YU12 | DRM_FORMAT_YUV420 | yuv420p8 / yu12 / yuv420p_yu12 | 12 | 8 | 3 | PLANAR | NO_PADDING | false | sampling: 4:2:0, order: yuv |
| PIXFMT_YUV420P_YV12 | DRM_FORMAT_YVU420 | yvu420p8 / yv12 / yuv420p_yv12 | 12 | 8 | 3 | PLANAR | NO_PADDING | false | sampling: 4:2:0, order: yvu |
| PIXFMT_YUV420P_10LSB | -                | yuv420p10l / yuv420p10l / yuv420p_10lsb | 24 | 10 | 3 | PLANAR | PADDING_AT_MSB | false | sampling: 4:2:0, order: yuv |
| PIXFMT_YUV420SP_NV12 | DRM_FORMAT_NV12 | yuv420sp8 / nv12 / yuv420sp_nv12 | 12 | 8 | 3 | SEMIPLANAR | NO_PADDING | false | sampling: 4:2:0, order: yuv |
| PIXFMT_YUV420SP_NV21 | DRM_FORMAT_NV21 | yvu420sp8 / nv21 / yuv420sp_nv21 | 12 | 8 | 3 | SEMIPLANAR | NO_PADDING | false | sampling: 4:2:0, order: yvu |
| PIXFMT_YUV420SP_NV15 | DRM_FORMAT_NV15 | yuv420sp10bp / nv15 / yuv420sp_nv15 | 15 | 10 | 3 | SEMIPLANAR | NO_PADDING | true | sampling: 4:2:0, order: yuv |
| PIXFMT_YUV420SP_10LSB | -              | yuv420sp10l / yuv420sp10l / yuv420sp_10lsb | 24 | 10 | 3 | SEMIPLANAR | PADDING_AT_MSB | false | sampling: 4:2:0, order: yuv |
| PIXFMT_YUV411P_YU11 | DRM_FORMAT_YUV411 | yuv411p8 / yu11 / yuv411p_yu11 | 12 | 8 | 3 | PLANAR | NO_PADDING | false | sampling: 4:1:1, order: yuv |
| PIXFMT_YUV411P_YV11 | DRM_FORMAT_YVU411 | yvu411p8 / yv11 / yuv411p_yv11 | 12 | 8 | 3 | PLANAR | NO_PADDING | false | sampling: 4:1:1, order: yvu |
| PIXFMT_YUV410P_YUV9 | DRM_FORMAT_YUV410 | yuv410p8 / yuv9 / yuv410p_yuv9 | 9 | 8 | 3 | PLANAR | NO_PADDING | false | sampling: 4:1:0, order: yuv |
_YUV410_YUV410P_YVU9 | DRM_FORMAT_YVU410 | yvu410p8 / yvu9 / yuv410p_yvu9 | 9 | 8 | 33 | PLANAR | NO_PADDING | false | sampling: 4:1:0, order: yvu |

### 2.3 YUV400 (Grayscale) 格式

| fmt_id | drm_code | name (full/short/alias) | bpp | depth | nb_comps | layout | padding_pos | bitpacked_order | desc |
|--------|----------|-------------------------|-----|-------|----------|--------|-------------|-----------------|------|
| PIXFMT_YUV400_R1 | DRM_FORMAT_R1 | yuv400r1bp / y1bp / - | 1 | 1 | 1 | PLANAR | NO_PADDING | true | sampling: 4:0:0, 1bit grayscale |
| PIXFMT_YUV400_R2 | DRM_FORMAT_R2 | yuv400r2bp / y2bp / - | 2 | 2 | 1 | PLANAR | NO_PADDING | true | sampling: 4:0:0, 2bit grayscale |
| PIXFMT_YUV400_R4 | DRM_FORMAT_R4 | yuv400r4bp / y4bp / - | 4 | 4 | 1 | PLANAR | NO_PADDING | true | sampling: 4:0:0, 4bit grayscale |
| PIXFMT_YUV400_R8 | DRM_FORMAT_R8 | yuv400r8 / y8 / -     | 8 | 8 | 1 | PLANAR | NO_PADDING | false | sampling: 4:0:0, 8bit grayscale |
| PIXFMT_YUV400_R10 | DRM_FORMAT_R10 | yuv400r10l / y10l / - | 16 | 10 | 1 | PLANAR | PADDING_AT_MSB | false | sampling: 4:0:0, 10bit grayscale |
| PIXFMT_YUV400_R12 | DRM_FORMAT_R12 | yuv400r12l / y12l / - | 16 | 12 | 1 | PLANAR | PADDING_AT_MSB | false | sampling: 4:0:0, 12bit grayscale |
| PIXFMT_YUV400_R16 | DRM_FORMAT_R16 | yuv400r16 / y16 / -   | 16 | 16 | 1 | PLANAR | NO_PADDING | false | sampling: 4:0:0, 16bit grayscale |

### 2.4 YUV Tile 格式

| fmt_id | base_type | name (full/short/alias) | bpp | depth | nb_comps | layout | padding_pos | bitpacked_order | desc |
|--------|-----------|-------------------------|-----|-------|----------|--------|-------------|-----------------|------|
| PIXFMT_YUV444SP_TILE4x4 | YUV | yuv444sp8_tile4x4 / nv24_tile4x4 / - | 24 | 8 | 3 | semiplanar + tile4x4 | NO_PADDING | false | Tile for nv24, 16+32=48 bytes/tile |
| PIXFMT_YUV422SP_TILE4x4 | YUV | yuv422sp8_tile4x4 / nv16_tile4x4 / - | 16 | 8 | 3 | semiplanar + tile4x4 | NO_PADDING | false | Tile for nv16, 16+16=32 bytes/tile |
| PIXFMT_YUV420SP_TILE4x4 | YUV | yuv420sp8_tile4x4 / nv12_tile4x4 / - | 12 | 8 | 3 | semiplanar + tile4x4 | NO_PADDING | false | Tile for nv12, 16+8=24 bytes/tile |

---

## 3. 格式命名规则说明

### 3.1 RGB 格式命名

格式: `<order><depth>[l/m]`

- `<order>` 表示通道顺序，比如 RGB, BGR, RGBA, BGRA 等
  - 如果是非 bitpacked ，通道顺序为从低位到高位
  - 如果是 bitpacked，通道顺序则是从高位到低位
  - 如果包含A，则说明有 Alpha 通道
- `<depth>` 表示对应通道的bit深度 (如 888=8:8:8, 565=5:6:5)
- `[l/m]` 表示低位有效数据或高位有效数据，意味着高位/低位有填充数据

举例:

- bgr233 表示 BGR 通道顺序（从高到低）， 2:3:3 位深度，从位深度可以看出该格式是 bitpacked
- rgba888 表示 RGBA 通道顺序（从低到高）， 8:8:8:8 位深度，从位深度可以看出该格式是 非 bitpacked
- abgr2101010 表示 ABGR 通道顺序（从高到低）， 2:10:10:10 位深度，从位深度可以看出该格式是 bitpacked
- rgba10l 表示 RGBA 通道顺序（从低到高）， 10:10:10:10 位深度， 'l' 表示每个通道低位有效，高位有填充

### 3.2 YUV 格式命名

格式: `<order><sampling><layout><depth>[bp][l/m]`

- `<order>` 表示从低位到高位的通道存储顺序，比如 yvu, yuyv 等
- `<sampling>` 表示色度的下采样方式，比如 444, 422, 410 等
- `<layout>` 表示平面布局，比如 Interleaved(交织), PLANAR(平面), SEMIPLANAR(半平面) 等
- `<depth>` 表示通道的bit深度，比如 8, 10, 12 等
- `[bp]` 表示按bit紧凑存储
- `[l/m]` 表示低位有效数据或高位有效数据，意味着高位/低位有填充数据
- 其他： `nv12/nv15/yu16` 等: 有 DRM 有关的命名

举例：

- uyv444i10lbp: 表示 444 采样，交错存储，通道顺序从低位到高位为 uyv, 10bit紧凑且低位有效，高位有填充
- uyvy422i8: 表示 422 采样，交错存储，通道顺序从低位到高位为 uyvy, 8bit有效数据
- yuyv422i12m: 表示 422 采样，交错存储，通道顺序从低位到高位为 yuyv, 12bit高位有效数据，低位有填充
- yuv420sp10bp: 表示 420 采样，半平面存储，通道顺序从低位到高位为 yuv, 10bit紧凑存储，无填充数据

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
