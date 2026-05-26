
include_directories(${CMAKE_CURRENT_LIST_DIR})
# message(STATUS "[DCI] VERIFY_LIBS on DCI: ${VERIFY_LIBS}")
# message(STATUS "[DCI] PREBUILT_LIBS on DCI: ${PREBUILT_LIBS}")


set(DCI_VERIFY_SRC
    ${CMAKE_CURRENT_LIST_DIR}/dci_verify_demo.cpp
)
add_executable(dci_verify_demo ${DCI_VERIFY_SRC})
target_link_libraries(dci_verify_demo
    ${VERIFY_LIBS}
    ${PREBUILT_DIR}/libdci_verify.a
    ${PREBUILT_DIR}/libsharp_full_verify.a
)
if(NOT WIN32)
    target_link_libraries(dci_verify_demo m)
endif()

install(TARGETS dci_verify_demo
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
