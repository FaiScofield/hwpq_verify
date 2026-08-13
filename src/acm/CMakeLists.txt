
include_directories(${CMAKE_CURRENT_LIST_DIR})
# message(STATUS "[ACM] VERIFY_LIBS on ACM: ${VERIFY_LIBS}")
# message(STATUS "[ACM] PREBUILT_LIBS on ACM: ${PREBUILT_LIBS}")

set(ACM_VERIFY_SRC
    ${CMAKE_CURRENT_LIST_DIR}/acm_verify_api.cpp
    ${CMAKE_CURRENT_LIST_DIR}/acm_verify_demo.cpp
)
if(PREBUILT_LIBS)
    add_executable(acm_verify_demo ${ACM_VERIFY_SRC})
    target_link_libraries(acm_verify_demo ${VERIFY_LIBS} ${PREBUILT_LIBS})
    if(NOT WIN32)
        target_link_libraries(acm_verify_demo m)
    endif()

    install(TARGETS acm_verify_demo
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    )
else()
    message(STATUS "[ACM] PREBUILT_LIBS not available, skip acm_verify_demo")
endif()
