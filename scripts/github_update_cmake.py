import argparse
import os
import re
import sys
from pathlib import Path
from textwrap import dedent

PROJECT_NAME = "vk-dynamic"
DEFAULT_CPP_STD = "c++17"
ROOT = Path(__file__).resolve().parents[1]
BUILD_FILES = {
  "cmake": ROOT / "CMakeLists.txt",
  "premake": ROOT / "premake5.lua",
  "meson": ROOT / "meson.build",
  "meson_options": ROOT / "meson_options.txt",
}

FEATURES = [
  {
    "cmake": "VK_DYNAMIC_ENABLE_NO_PROTOTYPES",
    "premake": "vk-dynamic-no-prototypes",
    "meson": "vk_dynamic_enable_no_prototypes",
    "define": "VK_NO_PROTOTYPES",
    "description": "Define VK_NO_PROTOTYPES for Vulkan headers",
    "default": True,
  },
  {
    "cmake": "VK_DYNAMIC_ENABLE_BETA_EXTENSIONS",
    "premake": "vk-dynamic-beta-extensions",
    "meson": "vk_dynamic_enable_beta_extensions",
    "define": "VK_ENABLE_BETA_EXTENSIONS",
    "description": "Define VK_ENABLE_BETA_EXTENSIONS",
    "default": True,
  },
  {
    "cmake": "VK_DYNAMIC_ENABLE_HPP_DYNAMIC_DISPATCH",
    "premake": "vk-dynamic-hpp-dynamic-dispatch",
    "meson": "vk_dynamic_enable_hpp_dynamic_dispatch",
    "define": "VULKAN_HPP_DISPATCH_LOADER_DYNAMIC=1",
    "description": "Enable Vulkan-Hpp default dynamic dispatch storage and define",
    "default": True,
  },
]


def die(message):
  print(message, file=sys.stderr)
  sys.exit(1)


def write_text(path, text):
  path.write_text(text, encoding="utf-8", newline="")


def read_text(path):
  try:
    return path.read_text(encoding="utf-8")
  except FileNotFoundError:
    die(f"{path.relative_to(ROOT)} not found")


def resolve_version(argv):
  parser = argparse.ArgumentParser(description="Update vk-dynamic build-system metadata")
  parser.add_argument("version", nargs="?", help="Vulkan-Headers version, for example 1.4.352")
  args = parser.parse_args(argv)
  version = args.version or os.environ.get("VK_VER")
  if not version:
    die("Missing version. Pass it as an argument or set VK_VER")
  if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
    die(f"Invalid version: {version}")
  return version


def update_cmake_version(version):
  path = BUILD_FILES["cmake"]
  lines = read_text(path).splitlines(True)
  rx_ver = re.compile(r"^\s*set\s*\(\s*VK_DYN_VER\b", re.IGNORECASE)
  rx_tag = re.compile(r"^\s*set\s*\(\s*VK_DYN_TAG\b", re.IGNORECASE)
  rx_min = re.compile(r"^\s*cmake_minimum_required\s*\(", re.IGNORECASE)
  set_ver = f'set(VK_DYN_VER "{version}" CACHE STRING "vk-dynamic project version")\n'

  min_idx = None
  filtered = []
  for line in lines:
    if min_idx is None and rx_min.match(line):
      min_idx = len(filtered)
    if rx_ver.match(line) or rx_tag.match(line):
      continue
    filtered.append(line)

  if min_idx is None:
    die("cmake_minimum_required line not found")

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
  write_text(path, "".join(out))


def premake_option(feature):
  default = "on" if feature["default"] else "off"
  return dedent(f"""
    newoption {{
        trigger = "{feature['premake']}",
        value = "VALUE",
        allowed = {{
            {{ "on", "Enable" }},
            {{ "off", "Disable" }}
        }},
        default = "{default}",
        description = "{feature['description']}"
    }}
  """).strip()


def render_premake(version):
  options = "\n\n".join(premake_option(feature) for feature in FEATURES)
  no_prototypes = FEATURES[0]["premake"]
  beta_extensions = FEATURES[1]["premake"]
  dynamic_dispatch = FEATURES[2]["premake"]
  return dedent(f"""
    VK_DYN_VER = "{version}"

    {options}

    local function option_enabled(name)
        local value = _OPTIONS[name]
        return value == nil or value == "on"
    end

    workspace "{PROJECT_NAME}"
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

        if option_enabled("{no_prototypes}") then
            defines {{ "VK_NO_PROTOTYPES" }}
        end

        if option_enabled("{beta_extensions}") then
            defines {{ "VK_ENABLE_BETA_EXTENSIONS" }}
        end

        if option_enabled("{dynamic_dispatch}") then
            defines {{ "VULKAN_HPP_DISPATCH_LOADER_DYNAMIC=1" }}
        end

    if option_enabled("{dynamic_dispatch}") then
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

            if option_enabled("{no_prototypes}") then
                defines {{ "VK_NO_PROTOTYPES" }}
            end

            if option_enabled("{beta_extensions}") then
                defines {{ "VK_ENABLE_BETA_EXTENSIONS" }}
            end
    end
  """).lstrip()


def render_meson(version):
  return dedent(f"""
    project(
      'vk-dynamic',
      ['c', 'cpp'],
      version: '{version}',
      default_options: ['cpp_std={DEFAULT_CPP_STD}']
    )

    vk_dynamic_include = include_directories('include')
    vk_dynamic_compile_args = []

    if get_option('{FEATURES[0]['meson']}')
      vk_dynamic_compile_args += ['-D{FEATURES[0]['define']}']
    endif

    if get_option('{FEATURES[1]['meson']}')
      vk_dynamic_compile_args += ['-D{FEATURES[1]['define']}']
    endif

    if get_option('{FEATURES[2]['meson']}')
      vk_dynamic_compile_args += ['-D{FEATURES[2]['define']}']
    endif

    vk_dynamic_dep = declare_dependency(
      include_directories: vk_dynamic_include,
      compile_args: vk_dynamic_compile_args
    )

    meson.override_dependency('vk-dynamic', vk_dynamic_dep)

    if get_option('{FEATURES[2]['meson']}')
      vk_dynamic_hpp_dispatch_lib = static_library(
        'vk-dynamic-hpp-dispatch',
        'src/vk.cpp',
        include_directories: vk_dynamic_include,
        cpp_args: vk_dynamic_compile_args
      )

      vk_dynamic_hpp_dispatch_dep = declare_dependency(
        include_directories: vk_dynamic_include,
        compile_args: vk_dynamic_compile_args,
        link_with: vk_dynamic_hpp_dispatch_lib
      )

      meson.override_dependency('vk-dynamic-hpp-dispatch', vk_dynamic_hpp_dispatch_dep)
    endif
  """).lstrip()


def render_meson_options():
  blocks = []
  for feature in FEATURES:
    value = "true" if feature["default"] else "false"
    blocks.append(dedent(f"""
      option(
        '{feature['meson']}',
        type: 'boolean',
        value: {value},
        description: '{feature['description']}'
      )
    """).strip())
  return "\n\n".join(blocks) + "\n"


def write_generated_files(version):
  write_text(BUILD_FILES["premake"], render_premake(version))
  write_text(BUILD_FILES["meson"], render_meson(version))
  write_text(BUILD_FILES["meson_options"], render_meson_options())


def validate(version):
  checks = {
    "cmake": f'VK_DYN_VER "{version}"',
    "premake": f'VK_DYN_VER = "{version}"',
    "meson": f"version: '{version}'",
  }
  for name, needle in checks.items():
    path = BUILD_FILES[name]
    text = read_text(path)
    if needle not in text:
      die(f"Failed to update {path.relative_to(ROOT)}")
  if "VK_DYN_TAG" in read_text(BUILD_FILES["cmake"]):
    die("VK_DYN_TAG still present, expected it to be removed")


def main(argv):
  version = resolve_version(argv)
  update_cmake_version(version)
  write_generated_files(version)
  validate(version)
  print(f"Updated build metadata for Vulkan-Headers {version}")


if __name__ == "__main__":
  main(sys.argv[1:])
