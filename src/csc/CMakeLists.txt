
include_directories(${CMAKE_CURRENT_LIST_DIR})

add_executable(csc_exe
    ${CMAKE_SOURCE_DIR}/rockchip_post_csc.c
    ${CMAKE_SOURCE_DIR}/main.c
)