aux_source_directory(${CMAKE_CURRENT_LIST_DIR} VERIFY_KERNEL_SRC)
add_library(verify_kernel STATIC ${VERIFY_KERNEL_SRC})
target_compile_options(verify_kernel PRIVATE "-std=c99")

list(APPEND VERIFY_LIBS verify_kernel)
set(VERIFY_LIBS "${VERIFY_LIBS}" PARENT_SCOPE) # set into parent scope