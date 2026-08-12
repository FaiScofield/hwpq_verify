
include_directories(${CMAKE_CURRENT_LIST_DIR})
# message(STATUS "[BCSH] VERIFY_LIBS on BCSH: ${VERIFY_LIBS}")

# hsv 定点 rgb<->hsv 自测（示例色往返，无浮点/无 math 库依赖）
add_executable(hsv_fixed_test
    ${CMAKE_CURRENT_LIST_DIR}/hsv_fixed.c
    ${CMAKE_CURRENT_LIST_DIR}/hsv_fixed_test.c
)

# hsv 浮点参考实现 + rgb->hsv->rgb 往返精度评估（可选参数 full 做 u10 全遍历）
add_executable(hsv_float_test
    ${CMAKE_CURRENT_LIST_DIR}/hsv_fixed.c
    ${CMAKE_CURRENT_LIST_DIR}/hsv_float_test.c
)
if(NOT WIN32)
    target_link_libraries(hsv_float_test m)
endif()

# H/S 定点量化精度分析（u8 全遍历，找零误差最小 bit 组合）
add_executable(hsv_precision_test
    ${CMAKE_CURRENT_LIST_DIR}/hsv_fixed.c
    ${CMAKE_CURRENT_LIST_DIR}/hsv_precision_test.c
)
if(NOT WIN32)
    target_link_libraries(hsv_precision_test m)
endif()

# HSV 调整：直接 RGB 域调整 vs rgb2hsv+调整+hsv2rgb 通路性能对比基准
add_executable(hsv_adjust_bench
    ${CMAKE_CURRENT_LIST_DIR}/hsv_fixed.c
    ${CMAKE_CURRENT_LIST_DIR}/hsv_adjust_bench.c
)
if(NOT WIN32)
    target_link_libraries(hsv_adjust_bench m)
endif()


install(TARGETS hsv_fixed_test hsv_float_test hsv_precision_test hsv_adjust_bench
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
