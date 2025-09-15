include_directories(${CMAKE_CURRENT_LIST_DIR}/include)
include_directories(${CMAKE_CURRENT_LIST_DIR}/include/vop)
include_directories(${CMAKE_CURRENT_LIST_DIR}/utils)
include_directories(${CMAKE_CURRENT_LIST_DIR}/kernel)

set(PREBUILT_LIB_SUFFIX "*.a")
if(WIN32)
    set(PREBUILT_DIR ${CMAKE_CURRENT_LIST_DIR}/../prebuilt/x86_win32/lib/)
    if(MSVC)
        set(PREBUILT_LIB_SUFFIX "*.lib")
    endif()
elseif(ABI STREQUAL "x86_64")
    set(PREBUILT_DIR ${CMAKE_CURRENT_LIST_DIR}/../prebuilt/x86_linux/lib)
else()
    message(FATAL_ERROR "Unsupported ABI: ${ABI} for prebuilt libraries!")
endif()
file(GLOB PREBUILT_LIBS
    LIST_DIRECTORIES false
    "${PREBUILT_DIR}/${PREBUILT_LIB_SUFFIX}"
)
message(STATUS "set PREBUILT_DIR: ${PREBUILT_DIR}")
message(STATUS "set PREBUILT_LIBS: ${PREBUILT_LIBS}")

add_subdirectory(utils)
add_subdirectory(kernel)
add_subdirectory(csc)
message(STATUS "built VERIFY_LIBS: ${VERIFY_LIBS}")
