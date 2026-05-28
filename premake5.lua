VK_DYN_VER = "1.4.352"

newoption {
    trigger = "vk-dynamic-no-prototypes",
    value = "VALUE",
    allowed = {
        { "on", "Enable" },
        { "off", "Disable" }
    },
    default = "on",
    description = "Define VK_NO_PROTOTYPES for Vulkan headers"
}

newoption {
    trigger = "vk-dynamic-beta-extensions",
    value = "VALUE",
    allowed = {
        { "on", "Enable" },
        { "off", "Disable" }
    },
    default = "on",
    description = "Define VK_ENABLE_BETA_EXTENSIONS"
}

newoption {
    trigger = "vk-dynamic-hpp-dynamic-dispatch",
    value = "VALUE",
    allowed = {
        { "on", "Enable" },
        { "off", "Disable" }
    },
    default = "on",
    description = "Enable Vulkan-Hpp default dynamic dispatch storage and define"
}

local function option_enabled(name)
    local value = _OPTIONS[name]
    return value == nil or value == "on"
end

workspace "vk-dynamic"
    configurations { "Debug", "Release" }
    architecture "x86_64"
    location "build/premake"

    filter "configurations:Debug"
        symbols "On"

    filter "configurations:Release"
        optimize "On"

    filter {}

project "vk-dynamic"
    kind "Utility"
    language "C++"
    cppdialect "C++17"
    targetdir "bin/%{cfg.buildcfg}"
    objdir "bin-int/%{cfg.buildcfg}/%{prj.name}"

    files {
        "include/**.h",
        "include/**.hpp"
    }

    includedirs {
        "include"
    }

    if option_enabled("vk-dynamic-no-prototypes") then
        defines { "VK_NO_PROTOTYPES" }
    end

    if option_enabled("vk-dynamic-beta-extensions") then
        defines { "VK_ENABLE_BETA_EXTENSIONS" }
    end

    if option_enabled("vk-dynamic-hpp-dynamic-dispatch") then
        defines { "VULKAN_HPP_DISPATCH_LOADER_DYNAMIC=1" }
    end

if option_enabled("vk-dynamic-hpp-dynamic-dispatch") then
    project "vk-dynamic-hpp-dispatch"
        kind "StaticLib"
        language "C++"
        cppdialect "C++17"
        targetdir "bin/%{cfg.buildcfg}"
        objdir "bin-int/%{cfg.buildcfg}/%{prj.name}"

        files {
            "src/vk.cpp"
        }

        includedirs {
            "include"
        }

        defines { "VULKAN_HPP_DISPATCH_LOADER_DYNAMIC=1" }

        if option_enabled("vk-dynamic-no-prototypes") then
            defines { "VK_NO_PROTOTYPES" }
        end

        if option_enabled("vk-dynamic-beta-extensions") then
            defines { "VK_ENABLE_BETA_EXTENSIONS" }
        end
end
