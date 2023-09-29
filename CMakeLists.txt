project(vk-dynamic INTERFACE VERSION 1.3.260)
add_library(vk::dynamic ALIAS ${PROJECT_NAME})

target_include_directories(${PROJECT_NAME} SYSTEM PUBLIC
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
        )

target_compile_definitions(${PROJECT_NAME} PUBLIC VK_NO_PROTOTYPES VK_ENABLE_BETA_EXTENSIONS)
target_sources(${PROJECT_NAME} PRIVATE src/vk.cpp)
