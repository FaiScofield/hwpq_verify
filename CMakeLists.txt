

cmake_minimum_required(VERSION 3.1...3.21)

project(hwpq_verify)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

################################################################################
## Build type & build options
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()
message(STATUS "CMake version: ${CMAKE_VERSION}")
message(STATUS "CMake build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Host platform:  ${CMAKE_HOST_SYSTEM_NAME}")
message(STATUS "Target platform: ${CMAKE_SYSTEM_NAME} - ${CMAKE_SYSTEM_PROCESSOR}")
if(MSVC)
    # /wd4996 = -Wno-deprecated-declarations
    add_compile_options(/wd4996)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
else()
    add_compile_options(-std=c99 -Wno-deprecated-declarations -Wno-format-truncation)
    if(CMAKE_BUILD_TYPE MATCHES "Debug")
        add_compile_options(-g -fno-inline -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer)
    endif()
    # add_link_options(-static-libstdc++) # get rid of link of libstdc++.so
endif()

## get ABI
string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" SYSPROC)
if(WIN32)
    set(X86_ALIASES x86 i386 i686 x86_64 amd64)
    list(FIND X86_ALIASES "${SYSPROC}" X86MATCH)
    if((SYSPROC STREQUAL "") OR (X86MATCH GREATER "-1"))
        message(STATUS "Detected x86 system processor")
        if(CMAKE_SIZEOF_VOID_P MATCHES 8)
            set(ABI "win_x64")
        else()
            set(ABI "win_x86")
        endif()
    else()
        message(FATAL_ERROR "Unknown Windows ABI: ${SYSPROC}")
    endif()
elseif(UNIX)
    set(ARMV7_ALIASES armv7-a armv7l armv7 armhf)
    list(FIND ARMV7_ALIASES "${SYSPROC}" ARMV7MATCH)
    if(SYSPROC STREQUAL "aarch64")
        set(ABI "aarch64")
        message(STATUS "Detected ARMv8 Linux system processor")
    elseif(ARMV7MATCH GREATER "-1")
        set(ABI "armhf")
        message(STATUS "Detected ARMv7 Linux system processor")
    elseif(SYSPROC STREQUAL "x86_64")
        set(ABI "x86_64")
        message(STATUS "Detected x86_64 Linux system processor")
    else()
        message(FATAL_ERROR "Unknown Linux ABI: ${SYSPROC}")
    endif()
else()
    message(FATAL_ERROR "CMAKE_SYSTEM_PROCESSOR value `${CMAKE_SYSTEM_PROCESSOR}` is unknown")
endif()
message(STATUS "Get target platform ABI: ${ABI}")

## parse RK_SOC like: RK3399[PRO], RK3588[S]
if(DEFINED RK_SOC)
    string(TOUPPER "${RK_SOC}" RK_SOC)
    string(SUBSTRING "${RK_SOC}" 0 6 RK_SOC_PREFIX)
    message(STATUS "Set target RK_SOC platform: ${RK_SOC}")
    add_definitions(-D${RK_SOC})
    add_definitions(-D${RK_SOC_PREFIX})
    message(STATUS "\tAdd definition: ${RK_SOC}")
    message(STATUS "\tAdd definition: ${RK_SOC_PREFIX}")

    if(RK_SOC MATCHES "RK3566" OR RK_SOC MATCHES "RK3568")
        add_definitions(-DRK356X)
        message(STATUS "\tAdd definition: RK356X")
    endif()
else()
    message(WARNING "Target RK_SOC not set!")
endif()

## install path
set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/output/)


################################################################################
## add subdirectories
add_subdirectory(src)
