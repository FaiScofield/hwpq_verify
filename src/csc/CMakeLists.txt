
include_directories(${CMAKE_CURRENT_LIST_DIR})

set(CSC_DEMO_SRC
    ${CMAKE_CURRENT_LIST_DIR}/rockchip_post_csc.c
    ${CMAKE_CURRENT_LIST_DIR}/rockchip_post_csc2.c
    ${CMAKE_CURRENT_LIST_DIR}/main.c
)
if(MSVC)
    list(APPEND CSC_DEMO_SRC ${CMAKE_CURRENT_LIST_DIR}/../utils/getopt_win32.c)
endif()

add_executable(csc_demo_exe ${CSC_DEMO_SRC})

install(TARGETS csc_demo_exe
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)