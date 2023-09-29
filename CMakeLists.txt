cmake_minimum_required(VERSION 3.15...3.25)

project(vk-dynamic LANGUAGES C VERSION 1.3.260)

add_library(vk-dynamic INTERFACE)
add_library(vk::dynamic ALIAS vk-dynamic)

target_include_directories(vk-dynamic INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_compile_definitions(vk-dynamic INTERFACE VK_NO_PROTOTYPES VK_ENABLE_BETA_EXTENSIONS)
target_sources(vk-dynamic INTERFACE src/vk.cpp)
