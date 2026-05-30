
include_directories(${CMAKE_CURRENT_LIST_DIR})
# message(STATUS "[DCI] VERIFY_LIBS on DCI: ${VERIFY_LIBS}")


set(DCI_VERIFY_SRC
    ${CMAKE_CURRENT_LIST_DIR}/dci_verify_demo.cpp
)
add_executable(dci_verify_demo ${DCI_VERIFY_SRC})
target_link_libraries(dci_verify_demo ${VERIFY_LIBS} ${PREBUILT_LIBS})
if(NOT WIN32)
    target_link_libraries(dci_verify_demo m)
endif()

# Layer 1 JSON-driven runner target
set(DCI_RUNNER_SRC
    ${CMAKE_CURRENT_LIST_DIR}/dci_verify_runner.cpp
    ${CMAKE_CURRENT_LIST_DIR}/dci_request_io.cpp
    ${CMAKE_CURRENT_LIST_DIR}/dci_verify_stubs.cpp
)
add_executable(dci_verify_runner ${DCI_RUNNER_SRC})
target_link_libraries(dci_verify_runner ${VERIFY_LIBS} ${PREBUILT_LIBS})
if(NOT WIN32)
    target_link_libraries(dci_verify_runner m)
endif()

install(TARGETS dci_verify_demo dci_verify_runner
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
