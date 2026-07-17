project(
  'vk-dynamic',
  ['c', 'cpp'],
  version: '1.4.357',
  default_options: ['cpp_std=c++17']
)

vk_dynamic_include = include_directories('include')
vk_dynamic_compile_args = []

if get_option('vk_dynamic_enable_no_prototypes')
  vk_dynamic_compile_args += ['-DVK_NO_PROTOTYPES']
endif

if get_option('vk_dynamic_enable_beta_extensions')
  vk_dynamic_compile_args += ['-DVK_ENABLE_BETA_EXTENSIONS']
endif

if get_option('vk_dynamic_enable_hpp_dynamic_dispatch')
  vk_dynamic_compile_args += ['-DVULKAN_HPP_DISPATCH_LOADER_DYNAMIC=1']
endif

vk_dynamic_dep = declare_dependency(
  include_directories: vk_dynamic_include,
  compile_args: vk_dynamic_compile_args
)

meson.override_dependency('vk-dynamic', vk_dynamic_dep)

if get_option('vk_dynamic_enable_hpp_dynamic_dispatch')
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
