project(
  'gulinalg',
  'c',
  version: '0.1',
  license: 'BSD-3',
  meson_version: '>= 1.5.0',
  default_options: [
    'buildtype=debugoptimized',
    'b_ndebug=if-release',
    'c_std=c17',
  ],
)

py3 = import('python').find_installation(pure: false)
py3_dep = py3.dependency()

cc = meson.get_compiler('c')

_global_c_args = cc.get_supported_arguments(
  '-Wno-unused-but-set-variable',
  '-Wno-unused-function',
  '-Wno-conversion',
  '-Wno-misleading-indentation',
)
add_project_arguments(_global_c_args, language : 'c')

# XXX: -lm needed?
# We need -lm for all C code (assuming it uses math functions, which is safe to
# assume for SciPy). For C++ it isn't needed, because libstdc++/libc++ is
# guaranteed to depend on it. For Fortran code, Meson already adds `-lm`.
m_dep = cc.find_library('m', required : false)
if m_dep.found()
  add_project_link_arguments('-lm', language : 'c')
endif

src_file_cli = find_program('buildscripts/process_src_template.py')
src_file = generator(src_file_cli,
  arguments : ['@INPUT@', '--outfile', '@OUTPUT@'],
  output : '@BASENAME@'
)

openblas = dependency('openblas', method: 'pkg-config', required: true)
openblas_dep = declare_dependency(
  dependencies: openblas,
  compile_args: []
)


# find numpy includes & the npymath library
inc_numpy = run_command(py3,
  ['-c', 'import os; os.chdir(".."); import numpy; print(numpy.get_include())'],
  check : true
).stdout().strip()
inc_np = include_directories(inc_numpy)

npymath_lib_path = inc_numpy / '..' / 'lib'
npymath_lib = cc.find_library('npymath', dirs: npymath_lib_path)

subdir('gulinalg')
