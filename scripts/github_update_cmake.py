import os, re, sys

vk_ver = os.environ["VK_VER"]

p = "CMakeLists.txt"
try:
  txt = open(p, "r", encoding="utf-8").read()
except FileNotFoundError:
  print("CMakeLists.txt not found")
  sys.exit(1)

lines = txt.splitlines(True)

rx_ver = re.compile(r'^\s*set\s*\(\s*VK_DYN_VER\b', re.IGNORECASE)
rx_tag = re.compile(r'^\s*set\s*\(\s*VK_DYN_TAG\b', re.IGNORECASE)
rx_min = re.compile(r'^\s*cmake_minimum_required\s*\(', re.IGNORECASE)

set_ver = f'set(VK_DYN_VER "{vk_ver}" CACHE STRING "vk-dynamic project version")\n'

min_idx = None
filtered = []
for ln in lines:
  if min_idx is None and rx_min.match(ln):
    min_idx = len(filtered)
  if rx_ver.match(ln) or rx_tag.match(ln):
    continue
  filtered.append(ln)

if min_idx is None:
  print("cmake_minimum_required line not found")
  sys.exit(1)

insert_at = min_idx + 1
while insert_at < len(filtered) and filtered[insert_at].strip() == "":
  insert_at += 1

out = []
out.extend(filtered[:min_idx + 1])
if not filtered[min_idx].endswith("\n"):
  out.append("\n")
out.append("\n")
out.append(set_ver)
out.append("\n")
out.extend(filtered[insert_at:])

open(p, "w", encoding="utf-8", newline="").write("".join(out))

chk = open(p, "r", encoding="utf-8").read()
if set_ver.strip() not in chk:
  print("Failed to set VK_DYN_VER")
  sys.exit(1)
if "VK_DYN_TAG" in chk:
  print("VK_DYN_TAG still present, expected it to be removed")
  sys.exit(1)

premake = f"""VK_DYN_VER = "{vk_ver}"

newoption {{
    trigger = "vk-dynamic-no-prototypes",
    value = "VALUE",
    allowed = {{
        {{ "on", "Enable" }},
        {{ "off", "Disable" }}
    }},
    default = "on",
    description = "Define VK_NO_PROTOTYPES for Vulkan headers"
}}

newoption {{
    trigger = "vk-dynamic-beta-extensions",
    value = "VALUE",
    allowed = {{
        {{ "on", "Enable" }},
        {{ "off", "Disable" }}
    }},
    default = "on",
    description = "Define VK_ENABLE_BETA_EXTENSIONS"
}}

newoption {{
    trigger = "vk-dynamic-hpp-dynamic-dispatch",
    value = "VALUE",
    allowed = {{
        {{ "on", "Enable" }},
        {{ "off", "Disable" }}
    }},
    default = "on",
    description = "Enable Vulkan-Hpp default dynamic dispatch storage and define"
}}

local function option_enabled(name)
    local value = _OPTIONS[name]
    return value == nil or value == "on"
end

workspace "vk-dynamic"
    configurations {{ "Debug", "Release" }}
    architecture "x86_64"
    location "build/premake"

    filter "configurations:Debug"
        symbols "On"

    filter "configurations:Release"
        optimize "On"

    filter {{}}

project "vk-dynamic"
    kind "Utility"
    language "C++"
    cppdialect "C++17"
    targetdir "bin/%{{cfg.buildcfg}}"
    objdir "bin-int/%{{cfg.buildcfg}}/%{{prj.name}}"

    files {{
        "include/**.h",
        "include/**.hpp"
    }}

    includedirs {{
        "include"
    }}

    if option_enabled("vk-dynamic-no-prototypes") then
        defines {{ "VK_NO_PROTOTYPES" }}
    end

    if option_enabled("vk-dynamic-beta-extensions") then
        defines {{ "VK_ENABLE_BETA_EXTENSIONS" }}
    end

    if option_enabled("vk-dynamic-hpp-dynamic-dispatch") then
        defines {{ "VULKAN_HPP_DISPATCH_LOADER_DYNAMIC=1" }}
    end

if option_enabled("vk-dynamic-hpp-dynamic-dispatch") then
    project "vk-dynamic-hpp-dispatch"
        kind "StaticLib"
        language "C++"
        cppdialect "C++17"
        targetdir "bin/%{{cfg.buildcfg}}"
        objdir "bin-int/%{{cfg.buildcfg}}/%{{prj.name}}"

        files {{
            "src/vk.cpp"
        }}

        includedirs {{
            "include"
        }}

        defines {{ "VULKAN_HPP_DISPATCH_LOADER_DYNAMIC=1" }}

        if option_enabled("vk-dynamic-no-prototypes") then
            defines {{ "VK_NO_PROTOTYPES" }}
        end

        if option_enabled("vk-dynamic-beta-extensions") then
            defines {{ "VK_ENABLE_BETA_EXTENSIONS" }}
        end
end
"""

open("premake5.lua", "w", encoding="utf-8", newline="").write(premake)

premake_chk = open("premake5.lua", "r", encoding="utf-8").read()
if f'VK_DYN_VER = "{vk_ver}"' not in premake_chk:
  print("Failed to set VK_DYN_VER in premake5.lua")
  sys.exit(1)
