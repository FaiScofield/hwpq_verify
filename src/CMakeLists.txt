include_directories(${CMAKE_CURRENT_LIST_DIR}/include)
include_directories(${CMAKE_CURRENT_LIST_DIR}/include/vop)
include_directories(${CMAKE_CURRENT_LIST_DIR}/utils)
include_directories(${CMAKE_CURRENT_LIST_DIR}/kernel)

set(LIB_DEPS "")
add_subdirectory(utils)
add_subdirectory(kernel)
add_subdirectory(csc)