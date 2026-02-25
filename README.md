# VK Dynamic

`vk-dynamic` is a small, vendored helper for using Vulkan-Hpp with dynamic dispatch.

## Quickstart

Link against the CMake alias target:

- `vk::dynamic`

```cmake
target_link_libraries(your_target PRIVATE vk::dynamic)
````

Include headers as normal:

```cpp
#include <vulkan/vulkan.hpp>
```
