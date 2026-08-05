include_directories(${CMAKE_CURRENT_LIST_DIR}/include)
include_directories(${CMAKE_CURRENT_LIST_DIR}/include/vop)
include_directories(${CMAKE_CURRENT_LIST_DIR}/utils)
include_directories(${CMAKE_CURRENT_LIST_DIR}/kernel)
include_directories(${CMAKE_CURRENT_LIST_DIR}/../prebuilt/include)

## set prebuilt libraries for module verification
set(PREBUILT_LIB_SUFFIX "*.a")
if(WIN32)
    set(PREBUILT_DIR ${CMAKE_CURRENT_LIST_DIR}/../prebuilt/lib/x86_windows)
    if(MSVC)
        set(PREBUILT_LIB_SUFFIX "*.lib")
    endif()
elseif(ABI STREQUAL "x86_64")
    set(PREBUILT_DIR ${CMAKE_CURRENT_LIST_DIR}/../prebuilt/x86_linux/lib)
else()
    message(FATAL_ERROR "[SRC] Unsupported ABI: ${ABI} for prebuilt libraries!")
endif()
file(GLOB PREBUILT_LIBS
    LIST_DIRECTORIES false
    "${PREBUILT_DIR}/${PREBUILT_LIB_SUFFIX}"
)
message(STATUS "[SRC] set PREBUILT_DIR: ${PREBUILT_DIR}")
# message(STATUS "[SRC] set PREBUILT_LIBS: ${PREBUILT_LIBS}")

## add common utility libraries
add_subdirectory(utils)
add_subdirectory(kernel)
add_subdirectory(tests)
message(STATUS "[SRC] built VERIFY_LIBS: ${VERIFY_LIBS}")

## add module verify directories
add_subdirectory(csc)
add_subdirectory(acm)
add_subdirectory(dci)
add_subdirectory(bcsh)
