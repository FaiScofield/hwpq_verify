

cmake_minimum_required(VERSION 3.1...3.21)

project(rkalgo_fpga_verify)

################################################################################
## Build type & build options
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()
message(STATUS "CMake version: ${CMAKE_VERSION}")
message(STATUS "CMake build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Host platform:  ${CMAKE_HOST_SYSTEM_NAME}")
message(STATUS "Target platform: ${CMAKE_SYSTEM_NAME}")
if(MSVC)
    # /wd4996 = -Wno-deprecated-declarations
    add_compile_options(/wd4996 /std:c++20)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
else()
    if(WIN32 AND CMAKE_C_COMPILER_ID STREQUAL "Clang")
        # WIN32 + LLVM case, see https://github.com/llvm/llvm-project/issues/61539 for option '-femulated-tls'
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread -femulated-tls")
    endif()
    add_compile_options(-std=c++11 -Wno-deprecated-declarations -Wno-unused-command-line-argument)
    if(CMAKE_BUILD_TYPE MATCHES "Debug")
        add_compile_options(-g -fno-inline -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer)
    endif()
    add_link_options(-static-libstdc++) # get rid of link of libstdc++.so
endif()

## get ABI
string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" SYSPROC)
if(WIN32)
    set(X86_ALIASES x86 i386 i686 x86_64 amd64)
    list(FIND X86_ALIASES "${SYSPROC}" X86MATCH)
    if((SYSPROC STREQUAL "") OR (X86MATCH GREATER "-1"))
        message(STATUS "Detected x86 system processor")
        if(CMAKE_SIZEOF_VOID_P MATCHES 8)
            set(ABI "x64")
        else()
            set(ABI "x86")
        endif()
    endif()
elseif(UNIX)
    message(STATUS "Detected Linux ARM system processor")
    if(SYSPROC STREQUAL "aarch64")
        set(ABI "aarch64")
    elseif(SYSPROC STREQUAL "armv7-a" OR SYSPROC STREQUAL "armv7l" OR SYSPROC STREQUAL "armv7" or SYSPROC STREQUAL "armhf")
        set(ABI "armhf")
    else()
        message(FATAL_ERROR "Unknown Linux ABI: ${SYSPROC}")
    endif()
else()
    message(FATAL_ERROR "CMAKE_SYSTEM_PROCESSOR value `${CMAKE_SYSTEM_PROCESSOR}` is unknown")
endif()
message(STATUS "get target platform ABI: ${ABI}")

################################################################################
## add executable
include_directories(include)
include_directories(src/ocl_program)

add_executable(ocl_demo_use_c_api src/ocl_demo_use_c_api.cpp)
set_target_properties(ocl_demo_use_c_api PROPERTIES LINK_FLAGS_RELEASE "-s") # set elf file stripped
target_link_libraries(ocl_demo_use_c_api ${OpenCL_LIBRARIES})
list(APPEND INSTALL_TARGETS ocl_demo_use_c_api)

## install
install(TARGETS ${INSTALL_TARGETS}
    RUNTIME DESTINATION ${CMAKE_SOURCE_DIR}/output/${ABI}
    LIBRARY DESTINATION ${CMAKE_SOURCE_DIR}/output/${ABI}
    ARCHIVE DESTINATION ${CMAKE_SOURCE_DIR}/output/${ABI}
)