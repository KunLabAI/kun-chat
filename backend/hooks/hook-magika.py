"""
PyInstaller 钩子文件，用于确保 magika 模块及其数据文件被正确打包
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集 magika 的所有子模块
hiddenimports = collect_submodules('magika')

# 收集 magika 的数据文件，特别是模型文件
datas = collect_data_files('magika')
