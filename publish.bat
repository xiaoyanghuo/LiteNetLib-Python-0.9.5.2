@echo off
REM LiteNetLib-Python 发布脚本
REM 使用前请先配置 %USERPROFILE%\.pypirc 文件

echo ========================================
echo LiteNetLib-Python v1.0.0 发布工具
echo ========================================
echo.

REM 检查构建产物是否存在
if not exist "dist\litenetlib_0952-1.0.0-py3-none-any.whl" (
    echo [错误] 未找到构建产物，正在构建...
    echo.
    python -m build
    if errorlevel 1 (
        echo [错误] 构建失败！
        pause
        exit /b 1
    )
    echo [成功] 构建完成
    echo.
)

REM 验证包
echo [1/4] 验证包...
python -m twine check dist/*
if errorlevel 1 (
    echo [错误] 包验证失败！
    pause
    exit /b 1
)
echo [成功] 包验证通过
echo.

REM 询问发布目标
echo 请选择发布目标:
echo   1 - TestPyPI (测试环境)
echo   2 - PyPI (正式环境)
echo   3 - 两者都发布
echo.
set /p choice="请输入选择 (1/2/3): "

if "%choice%"=="1" goto testpypi
if "%choice%"=="2" goto pypi
if "%choice%"=="3" goto both
echo [错误] 无效的选择！
pause
exit /b 1

:testpypi
echo.
echo [2/4] 上传到 TestPyPI...
python -m twine upload --repository testpypi dist/*
if errorlevel 1 (
    echo [错误] 上传到 TestPyPI 失败！
    pause
    exit /b 1
)
echo [成功] 已上传到 TestPyPI
echo.
echo 测试安装命令:
echo   pip install --index-url https://test.pypi.org/simple/ litenetlib-0952
echo.
goto done

:pypi
echo.
echo [警告] 即将发布到正式 PyPI！
echo 版本号: 1.0.0
echo.
set /p confirm="确认发布？(yes/no): "
if /i not "%confirm%"=="yes" (
    echo [取消] 发布已取消
    pause
    exit /b 0
)
echo.
echo [2/4] 上传到 PyPI...
python -m twine upload dist/*
if errorlevel 1 (
    echo [错误] 上传到 PyPI 失败！
    pause
    exit /b 1
)
echo [成功] 已上传到 PyPI
echo.
echo 安装命令:
echo   pip install litenetlib-0952
echo.
goto done

:both
echo.
echo [2/4] 上传到 TestPyPI...
python -m twine upload --repository testpypi dist/*
if errorlevel 1 (
    echo [错误] 上传到 TestPyPI 失败！
    pause
    exit /b 1
)
echo [成功] 已上传到 TestPyPI
echo.
echo [3/4] 上传到 PyPI...
echo [警告] 即将发布到正式 PyPI！
echo 版本号: 1.0.0
echo.
set /p confirm="确认发布？(yes/no): "
if /i not "%confirm%"=="yes" (
    echo [取消] PyPI 发布已取消（TestPyPI已成功）
    pause
    exit /b 0
)
python -m twine upload dist/*
if errorlevel 1 (
    echo [错误] 上传到 PyPI 失败！
    pause
    exit /b 1
)
echo [成功] 已上传到 PyPI
echo.

:done
echo [4/4] 发布完成！
echo.
echo ========================================
echo 发布信息:
echo   包名: litenetlib-0952
echo   版本: 1.0.0
echo   PyPI: https://pypi.org/project/litenetlib-0952/
echo   TestPyPI: https://test.pypi.org/project/litenetlib-0952/
echo ========================================
echo.
pause
