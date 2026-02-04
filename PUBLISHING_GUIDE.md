# LiteNetLib-Python 发布指南

## 当前状态

✅ **代码已提交**: Commit 2950b7f
⚠️ **GitHub推送失败**: 网络连接问题（需手动重试）
✅ **打包完成**:
  - `litenetlib_0952-1.0.0-py3-none-any.whl` (68K)
  - `litenetlib_0952-1.0.0.tar.gz` (123K)
✅ **包验证通过**: twine check PASSED

---

## 步骤1: 手动推送到GitHub

```bash
git push origin main
```

如果连接失败，可能需要：
1. 检查网络连接
2. 配置代理（如果使用）
3. 使用SSH替代HTTPS

---

## 步骤2: 配置PyPI发布

### 方式1: 使用API Token（推荐）

1. **创建PyPI账号和Token**
   - 访问 https://pypi.org/account/register/
   - 登录后访问 https://pypi.org/manage/account/token/
   - 创建新的API Token（scope: entire account）
   - **复制Token**（只显示一次！）

2. **配置 ~/.pypirc**

创建文件 `%USERPROFILE%\.pypirc`（Windows）或 `~/.pypirc`（Linux/Mac）：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <你的API Token>

[testpypi]
username = __token__
password = <你的TestPyPI API Token>
repository = https://test.pypi.org/legacy/
```

**安全提示**:
- 确保文件权限设置为只有你能读取
- 不要将 `.pypirc` 提交到Git

### 方式2: 使用命令行参数（不推荐，不安全）

```bash
python -m twine upload dist/* --username __token__ --password <你的Token>
```

---

## 步骤3: 测试发布到TestPyPI

```bash
# 上传到TestPyPI
python -m twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ litenetlib-0952
```

如果成功，你会在 https://test.pypi.org/project/litenetlib-0952/ 看到你的包。

---

## 步骤4: 发布到正式PyPI

```bash
# 上传到PyPI（确保版本号正确）
python -m twine upload dist/*
```

**重要提示**:
- PyPI的版本号**不能重复**
- 如果需要重新发布，必须：
  1. 修改 `pyproject.toml` 中的版本号（如 1.0.1）
  2. 重新构建 `python -m build`
  3. 删除旧的 `dist/*` 文件
  4. 重新上传

如果成功，你会在 https://pypi.org/project/litenetlib-0952/ 看到你的包。

---

## 步骤5: 验证发布

```bash
# 从PyPI安装
pip install litenetlib-0952

# 测试导入
python -c "from litenetlib import LiteNetManager; print('Success!')"

# 运行测试
pip install litenetlib-0952[dev]
pytest tests/
```

---

## 常见问题

### Q: 上传失败，提示403 Forbidden
**A**: 检查API Token是否正确，scope是否为"entire account"

### Q: 上传失败，提示文件已存在
**A**: PyPI不允许覆盖已发布的版本。需要：
1. 增加版本号
2. 重新构建
3. 重新上传

### Q: 如何删除已发布的版本？
**A**:
1. 登录 PyPI
2. 访问项目页面
3. 点击 "History" 标签
4. 找到要删除的版本，点击 "Delete"
   - **注意**: 只能删除24小时内发布的版本
   - **注意**: 删除后无法恢复

### Q: TestPyPI上传成功但PyPI失败
**A**: TestPyPI和PyPI使用不同的token，需要分别为其创建token

### Q: 如何回退发布？
**A**:
1. 如果是24小时内，可以从PyPI删除
2. 如果超过24小时，只能发布新版本修复问题
3. 使用 `yank` 功能标记为已废弃（仍可安装，但会提示）

---

## 自动化发布脚本

创建 `publish.sh`（Linux/Mac）或 `publish.bat`（Windows）：

**publish.bat**:
```batch
@echo off
echo Building...
python -m build

echo Uploading to TestPyPI...
python -m twine upload --repository testpypi dist/*

echo Wait for user confirmation...
pause

echo Uploading to PyPI...
python -m twine upload dist/*

echo Done!
```

**publish.sh**:
```bash
#!/bin/bash
set -e

echo "Building..."
python -m build

echo "Uploading to TestPyPI..."
python -m twine upload --repository testpypi dist/*

echo "Wait for user confirmation..."
read -p "Press Enter to continue to PyPI..."

echo "Uploading to PyPI..."
python -m twine upload dist/*

echo "Done!"
```

---

## GitHub Actions自动发布（可选）

创建 `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

配置GitHub Secrets:
1. 访问 GitHub仓库设置
2. Secrets and variables → Actions
3. New repository secret
4. Name: `PYPI_API_TOKEN`
5. Value: 你的PyPI API Token

发布时：
```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 发布后任务

### 1. 创建GitHub Release
```bash
# 使用GitHub CLI
gh release create v1.0.0 \
  --title "LiteNetLib-Python v1.0.0" \
  --notes "See CHANGELOG.md for details" \
  dist/*
```

或在GitHub网页上：
1. 访问仓库 → Releases
2. "Draft a new release"
3. Tag: v1.0.0
4. Title: LiteNetLib-Python v1.0.0
5. 上传构建的文件

### 2. 更新文档
- README.md：添加PyPI徽章
- CHANGELOG.md：记录发布内容
- API文档：如有独立文档站点

### 3. 通告
- 项目README添加PyPI安装说明
- 社交媒体/博客发布通告
- 相关社区通知

---

## 当前包信息

- **名称**: litenetlib-0952
- **版本**: 1.0.0
- **大小**: 68K (wheel) + 123K (sdist)
- **依赖**: 无外部依赖
- **Python版本**: 3.7+
- **许可证**: MIT

---

## 快速命令参考

```bash
# 完整发布流程
git add .
git commit -m "Release v1.0.0"
git push origin main
git tag v1.0.0
git push origin v1.0.0
python -m build
python -m twine check dist/*
python -m twine upload dist/*

# 测试安装
pip install litenetlib-0952
python -c "import litenetlib; print(litenetlib.__version__)"
```

---

**祝发布顺利！** 🎉
