
include_directories(${CMAKE_CURRENT_LIST_DIR})

set(CSC_DEMO_SRC
    ${CMAKE_CURRENT_LIST_DIR}/../kernel/rockchip_post_csc.c # post_csc from RK3576 kernel
    ${CMAKE_CURRENT_LIST_DIR}/rockchip_post_csc2.c # post_csc new implementation after RK3572, not in kernel
    ${CMAKE_CURRENT_LIST_DIR}/post_csc_kernel_demo.c
)
if(MSVC)
    list(APPEND CSC_DEMO_SRC ${CMAKE_CURRENT_LIST_DIR}/../utils/getopt_win32.c)
endif()

add_executable(post_csc_kernel_demo ${CSC_DEMO_SRC})

install(TARGETS post_csc_kernel_demo
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)