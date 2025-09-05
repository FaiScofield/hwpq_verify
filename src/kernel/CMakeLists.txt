aux_source_directory(${CMAKE_CURRENT_LIST_DIR} VERIFY_KERNEL_SRC)
add_library(verify_kernel STATIC ${VERIFY_KERNEL_SRC})
list(APPEND LIB_DEPS verify_kernel)