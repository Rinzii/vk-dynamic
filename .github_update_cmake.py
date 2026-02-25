import os, re, sys

vk_ver = os.environ["VK_VER"]
gl_ver = os.environ["GL_VER"]

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
set_tag = f'set(VK_DYN_TAG "v{vk_ver}-{gl_ver}" CACHE STRING "vk-dynamic release tag")\n'

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
out.append(set_tag)
out.append("\n")
out.extend(filtered[insert_at:])

open(p, "w", encoding="utf-8", newline="").write("".join(out))

chk = open(p, "r", encoding="utf-8").read()
if f'set(VK_DYN_VER "{vk_ver}" CACHE STRING "vk-dynamic project version")' not in chk:
  print("Failed to set VK_DYN_VER")
  sys.exit(1)
if f'set(VK_DYN_TAG "v{vk_ver}-{gl_ver}" CACHE STRING "vk-dynamic release tag")' not in chk:
  print("Failed to set VK_DYN_TAG")
  sys.exit(1)
