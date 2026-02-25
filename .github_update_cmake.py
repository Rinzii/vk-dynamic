import os, re, sys

vk_ver = os.environ["VK_VER"]
gl_ver = os.environ["GL_VER"]

p = "CMakeLists.txt"
try:
  txt = open(p, "r", encoding="utf-8").read()
except FileNotFoundError:
  print("CMakeLists.txt not found")
  sys.exit(1)

set_ver = f'set(VK_DYN_VER "{vk_ver}" CACHE STRING "vk-dynamic project version")'
set_tag = f'set(VK_DYN_TAG "v{vk_ver}-{gl_ver}" CACHE STRING "vk-dynamic release tag")'

lines = txt.splitlines(True)

def find_line_idx(rx):
  r = re.compile(rx)
  for i, ln in enumerate(lines):
    if r.match(ln):
      return i
  return -1

i_min = find_line_idx(r'^\s*cmake_minimum_required\s*\(')
if i_min < 0:
  print("cmake_minimum_required line not found")
  sys.exit(1)

i_ver = find_line_idx(r'^\s*set\s*\(\s*VK_DYN_VER\b')
if i_ver >= 0:
  nl = "\n" if lines[i_ver].endswith("\n") else ""
  lines[i_ver] = set_ver + nl
else:
  insert_at = i_min + 1
  lines.insert(insert_at, "\n" if not lines[i_min].endswith("\n") else "")
  lines.insert(insert_at + 1, set_ver + "\n")
  lines.insert(insert_at + 2, "\n")

i_tag = find_line_idx(r'^\s*set\s*\(\s*VK_DYN_TAG\b')
if i_tag >= 0:
  nl = "\n" if lines[i_tag].endswith("\n") else ""
  lines[i_tag] = set_tag + nl
else:
  i_ver2 = find_line_idx(r'^\s*set\s*\(\s*VK_DYN_VER\b')
  insert_at = (i_ver2 + 1) if i_ver2 >= 0 else (i_min + 1)
  if insert_at < len(lines) and lines[insert_at].strip() != "":
    lines.insert(insert_at, "\n")
    insert_at += 1
  lines.insert(insert_at, set_tag + "\n")
  lines.insert(insert_at + 1, "\n")

out = "".join(lines)
open(p, "w", encoding="utf-8", newline="").write(out)

out2 = open(p, "r", encoding="utf-8").read()
if set_ver not in out2:
  print("Failed to set VK_DYN_VER")
  sys.exit(1)
if set_tag not in out2:
  print("Failed to set VK_DYN_TAG")
  sys.exit(1)
