@echo off
REM TestPyPI 一键发布脚本
REM 使用前请先配置环境变量:
REM   set TWINE_USERNAME=__token__
REM   set TWINE_PASSWORD=pypi-xxxxxxxxxxxxx

echo ============================================
echo LiteNetLib-Python TestPyPI 发布
echo ============================================
echo.

echo [1/3] 检查包...
python -m twine check dist\*
if errorlevel 1 (
    echo 包检查失败！
    pause
    exit /b 1
)
echo.

echo [2/3] 发布到 TestPyPI...
python -m twine upload --repository testpypi dist\*
if errorlevel 1 (
    echo 发布失败！
    echo.
    echo 请确保:
    echo 1. 已配置 TWINE_USERNAME 和 TWINE_PASSWORD
    echo 2. Token 格式正确: pypi-xxxxxxxxxxxxx
    echo.
    pause
    exit /b 1
)
echo.

echo [3/3] 从 TestPyPI 安装测试...
pip uninstall litenetlib-python -y 2>nul
pip install --index-url https://test.pypi.org/simple/ litenetlib-python
if errorlevel 1 (
    echo 安装测试失败！
    pause
    exit /b 1
)
echo.

echo ============================================
echo 验证安装...
python -c "from litenetlib.core.constants import NetConstants; print('PROTOCOL_ID:', NetConstants.PROTOCOL_ID, '- ACK:', NetConstants.ACK)"
echo.

echo ============================================
echo TestPyPI 发布成功！
echo.
echo TestPyPI URL: https://test.pypi.org/project/litenetlib-python/
echo.

pause
