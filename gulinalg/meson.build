# build the _impl extension

gulinalg_sources = [
  src_file.process('src/gulinalg.c.src'),
]

py3.extension_module('_impl',
  [
    gulinalg_sources,
    'src/conditional_omp.h',
  ],
#  c_args: c_args_common,
  include_directories: [inc_np, 'src/'],
  dependencies: [openblas_dep],
  gnu_symbol_visibility: 'default',
  install: true,
  subdir: 'gulinalg',
)


py3.install_sources(
  ['gufunc_general.py',
   'gufunc_linalg.py',
   '__init__.py',
   'testing.py',
   'ufunc_extras.py'
 ],
  subdir: 'gulinalg'
)


subdir('tests')   # FIXME
