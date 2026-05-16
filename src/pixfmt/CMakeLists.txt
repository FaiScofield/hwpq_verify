
set(PIXFMT_SRC
    ${CMAKE_CURRENT_LIST_DIR}/pixfmt_csc.c
    ${CMAKE_CURRENT_LIST_DIR}/pixfmt_cvt.c
    ${CMAKE_CURRENT_LIST_DIR}/pixfmt_frame.c
    ${CMAKE_CURRENT_LIST_DIR}/pixfmt_rgb.c
    ${CMAKE_CURRENT_LIST_DIR}/pixfmt_yuv.c
    ${CMAKE_CURRENT_LIST_DIR}/pixfmt.c
)

add_library(pixfmt OBJECT ${PIXFMT_SRC})
