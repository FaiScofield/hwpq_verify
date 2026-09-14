"""UI entry points for the verify tool application package.

这里不再做包级 re-export：包的 ``__init__`` 会在导入任意子模块时先执行，
连带把整个测试应用（uic 重生成、setup_logger、Qt 控件类）拉起来，打包环境下
会因此失败。测试应用按文件路径直接导入即可，例如：
``from script.verify_tool_app.test_app_acm import AcmTestAppWindow``。
"""
