
include_directories(${CMAKE_CURRENT_LIST_DIR})

set(POST_CSC_DEMO_SRC
    ${CMAKE_CURRENT_LIST_DIR}/../kernel/rockchip_post_csc.c # post_csc from RK3576 kernel
    ${CMAKE_CURRENT_LIST_DIR}/rockchip_post_csc2.c # post_csc new implementation after RK3572, not in kernel
    ${CMAKE_CURRENT_LIST_DIR}/post_csc_kernel_demo.c
)
if(MSVC)
    list(APPEND POST_CSC_DEMO_SRC ${CMAKE_CURRENT_LIST_DIR}/../utils/getopt_win32.c)
endif()
add_executable(post_csc_kernel_demo ${POST_CSC_DEMO_SRC})


set(CSC_VERIFY_SRC ${CMAKE_CURRENT_LIST_DIR}/csc_verify_demo.c)
add_executable(csc_verify_demo ${CSC_VERIFY_SRC})
target_link_libraries(csc_verify_demo ${LIB_DEPS})

install(TARGETS post_csc_kernel_demo csc_verify_demo
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)