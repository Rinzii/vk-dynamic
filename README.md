# VK Dynamic

`vk-dynamic` is a small, vendored helper for using Vulkan-Hpp with dynamic dispatch.

It centralizes Vulkan-Hpp dynamic-dispatch setup so consumers do not need to define dispatcher storage manually, repeat source boilerplate or wire the same setup through the build system.

## Quickstart

Link against the CMake alias target:

```cmake
target_link_libraries(your_target PRIVATE vk::dynamic)
```

Include Vulkan-Hpp as normal:

```cpp
#include <vulkan/vulkan.hpp>
```

Initialize the default dispatcher as usual:

```cpp
VULKAN_HPP_DEFAULT_DISPATCHER.init();
```

## Reasoning

Without `vk-dynamic`, each project usually needs to repeat the same setup in source:

```cpp
#define VULKAN_HPP_DISPATCH_LOADER_DYNAMIC 1
#include <vulkan/vulkan.hpp>

VULKAN_HPP_DEFAULT_DISPATCH_LOADER_DYNAMIC_STORAGE
```

And each target needs matching build-system setup:

```cmake
target_compile_definitions(your_target PRIVATE
    VULKAN_HPP_DISPATCH_LOADER_DYNAMIC=1
)
```

This is easy to copy incorrectly when multiple applications, examples or test targets all use Vulkan-Hpp. One target might define the macro but forget dispatcher storage. Another might define storage in more than one source file. Another might use different compile definitions from the rest of the project.

With `vk-dynamic`, that setup is handled once by the linked target:

```cpp
#include <vulkan/vulkan.hpp>
```

```cmake
target_link_libraries(your_target PRIVATE vk::dynamic)
```

Each consuming project uses the same setup path, which saves time and keeps Vulkan-Hpp dynamic dispatch configured consistently across targets.

`vk-dynamic` also keeps updates tied directly to the Vulkan headers it vendors. Branches, tags and releases are generated around the actual Vulkan header versions, so updating a project is a matter of selecting the matching version instead of manually checking which headers, build files and dispatch setup belong together.

The project also provides native build-system support for CMake, Premake5 and Meson. That makes the same vendored dispatch setup usable across different project layouts without rewriting the integration for each build system.
