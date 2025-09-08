aux_source_directory(${CMAKE_CURRENT_LIST_DIR} VERIFY_UTILS_SRC)
add_library(verify_utils STATIC ${VERIFY_UTILS_SRC})
list(APPEND LIB_DEPS verify_utils)
set(LIB_DEPS "${LIB_DEPS}" PARENT_SCOPE) # update parent scope