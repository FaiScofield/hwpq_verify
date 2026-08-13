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
elseif(ABI STREQUAL "aarch64" OR ABI STREQUAL "armhf")
    # no prebuilt libs shipped for ARM ABIs (e.g. Android), warn and continue
    message(WARNING "[SRC] No prebuilt libraries for ABI: ${ABI}, skip targets that need prebuilt libs!")
    set(PREBUILT_DIR "")
else()
    message(WARNING "[SRC] Unsupported ABI: ${ABI} for prebuilt libraries, skip targets that need prebuilt libs!")
    set(PREBUILT_DIR "")
endif()

## if PREBUILT_DIR is missing/empty, mark prebuilt libs unavailable so dependant targets can be skipped
set(PREBUILT_AVAILABLE ON)
if(PREBUILT_DIR AND EXISTS "${PREBUILT_DIR}")
    file(GLOB PREBUILT_LIBS
        LIST_DIRECTORIES false
        "${PREBUILT_DIR}/${PREBUILT_LIB_SUFFIX}"
    )
    message(STATUS "[SRC] set PREBUILT_DIR: ${PREBUILT_DIR}")
else()
    set(PREBUILT_AVAILABLE OFF)
    set(PREBUILT_LIBS "")
    message(WARNING "[SRC] PREBUILT_DIR not found: '${PREBUILT_DIR}', skip targets that need prebuilt libs!")
endif()
message(STATUS "[SRC] PREBUILT_AVAILABLE: ${PREBUILT_AVAILABLE}")
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
