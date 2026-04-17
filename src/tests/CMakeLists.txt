
include_directories(${CMAKE_CURRENT_LIST_DIR})

# test_img_fmt
# add_executable(test_img_fmt
#     ${CMAKE_CURRENT_LIST_DIR}/test_verify_img_fmt.c
# )
# target_link_libraries(test_img_fmt ${VERIFY_LIBS})

# test_verify_com
set(TEST_VERIFY_COM_SRC ${CMAKE_CURRENT_LIST_DIR}/test_verify_com.c)
if(NOT WIN32)
    list(REMOVE_ITEM TEST_VERIFY_COM_SRC ${CMAKE_CURRENT_LIST_DIR}/getopt_win32.c)
endif()
add_executable(test_verify_com ${TEST_VERIFY_COM_SRC})
target_link_libraries(test_verify_com ${VERIFY_LIBS})

# test_pqfmt
add_executable(test_pqfmt ${CMAKE_CURRENT_LIST_DIR}/test_pqfmt.c)
target_link_libraries(test_pqfmt ${VERIFY_LIBS})

# install
install(TARGETS test_verify_com test_pqfmt
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
