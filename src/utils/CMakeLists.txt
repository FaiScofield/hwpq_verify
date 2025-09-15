aux_source_directory(${CMAKE_CURRENT_LIST_DIR} VERIFY_UTILS_SRC)
if(NOT WIN32)
    list(REMOVE_ITEM VERIFY_UTILS_SRC ${CMAKE_CURRENT_LIST_DIR}/getopt_win32.c)
endif()
# message(STATUS "[UTILS] get VERIFY_UTILS_SRC: ${VERIFY_UTILS_SRC}")

add_library(verify_utils STATIC ${VERIFY_UTILS_SRC})

list(APPEND VERIFY_LIBS verify_utils)
set(VERIFY_LIBS "${VERIFY_LIBS}" PARENT_SCOPE) # set into parent scopes
