cmake_minimum_required(VERSION 3.15...3.25)

set(VK_DYN_VER "1.4.344" CACHE STRING "vk-dynamic project version")

project(vk-dynamic LANGUAGES C CXX VERSION ${VK_DYN_VER})

option(VK_DYNAMIC_ENABLE_HPP_DYNAMIC_DISPATCH "Enable Vulkan-Hpp default dynamic dispatch storage and define" ON)
option(VK_DYNAMIC_ENABLE_NO_PROTOTYPES "Define VK_NO_PROTOTYPES for Vulkan headers" ON)
option(VK_DYNAMIC_ENABLE_BETA_EXTENSIONS "Define VK_ENABLE_BETA_EXTENSIONS" ON)

add_library(vk-dynamic INTERFACE)
add_library(vk::dynamic ALIAS vk-dynamic)

target_include_directories(vk-dynamic INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

if (VK_DYNAMIC_ENABLE_NO_PROTOTYPES)
  target_compile_definitions(vk-dynamic INTERFACE VK_NO_PROTOTYPES)
endif()

if (VK_DYNAMIC_ENABLE_BETA_EXTENSIONS)
  target_compile_definitions(vk-dynamic INTERFACE VK_ENABLE_BETA_EXTENSIONS)
endif()

if (VK_DYNAMIC_ENABLE_HPP_DYNAMIC_DISPATCH)
  target_compile_definitions(vk-dynamic INTERFACE VULKAN_HPP_DISPATCH_LOADER_DYNAMIC=1)

  add_library(vk-dynamic-hpp-dispatch STATIC src/vk.cpp)
  add_library(vk::dynamic_hpp_dispatch ALIAS vk-dynamic-hpp-dispatch)

  target_link_libraries(vk-dynamic-hpp-dispatch PUBLIC vk-dynamic)

  target_include_directories(vk-dynamic-hpp-dispatch PUBLIC
      $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
      $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
  )

  if (VK_DYNAMIC_ENABLE_NO_PROTOTYPES)
    target_compile_definitions(vk-dynamic-hpp-dispatch PUBLIC VK_NO_PROTOTYPES)
  endif()

  if (VK_DYNAMIC_ENABLE_BETA_EXTENSIONS)
    target_compile_definitions(vk-dynamic-hpp-dispatch PUBLIC VK_ENABLE_BETA_EXTENSIONS)
  endif()

  target_compile_definitions(vk-dynamic-hpp-dispatch PUBLIC VULKAN_HPP_DISPATCH_LOADER_DYNAMIC=1)

  set_target_properties(vk-dynamic-hpp-dispatch PROPERTIES
      VERSION ${PROJECT_VERSION}
  )
endif()