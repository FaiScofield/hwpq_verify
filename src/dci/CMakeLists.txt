
include_directories(${CMAKE_CURRENT_LIST_DIR})
# message(STATUS "[DCI] VERIFY_LIBS on DCI: ${VERIFY_LIBS}")
# message(STATUS "[DCI] PREBUILT_LIBS on DCI: ${PREBUILT_LIBS}")


set(DCI_VERIFY_SRC
    ${CMAKE_CURRENT_LIST_DIR}/dci_verify_demo.cpp
)
set(DCI_PREBUILT_LIBS
    ${PREBUILT_DIR}/libdci_verify.a
    ${PREBUILT_DIR}/libsharp_full_verify.a
    ${PREBUILT_DIR}/libsharp_lite_verify.a
)
if(EXISTS "${PREBUILT_DIR}/libdci_verify.a"
   AND EXISTS "${PREBUILT_DIR}/libsharp_full_verify.a"
   AND EXISTS "${PREBUILT_DIR}/libsharp_lite_verify.a")
    add_executable(dci_verify_demo ${DCI_VERIFY_SRC})
    target_link_libraries(dci_verify_demo
        ${VERIFY_LIBS}
        ${DCI_PREBUILT_LIBS}
    )
    if(NOT WIN32)
        target_link_libraries(dci_verify_demo m)
    endif()

    install(TARGETS dci_verify_demo
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    )
else()
    message(STATUS "[DCI] prebuilt libs not available, skip dci_verify_demo")
endif()