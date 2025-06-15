---
trigger: always_on
description: test python module
globs:**/*.py
---
1. 统一测试根目录: **所有** 单元测试文件必须放在 **`/Users/junix/knowledge-forge-office/tests`** 目录下，严禁散落在其他目录。
2. 保持相同的相对目录层级:
   * 被测源文件相对于 **第二个 `knowledge_forge/`** 目录的层级结构，必须在 **`tests/`** 目录下 **原样复制**。
   * 例如：

     * 源文件：  `/Users/junix/knowledge-forge-office/knowledge_forge/path/to/module.py`
     * 测试文件：`/Users/junix/knowledge-forge-office/tests/path/to/test_module.py`

3. **测试文件命名规则**

   * 文件名必须以 **`test_`** 前缀 + 原模块文件名组成，保持 **`.py`** 扩展名不变。
   * 若模块名为 `example.py`，测试文件应命名为 **`test_example.py`**。

4. **示例**

| 源文件完整路径                                                | 对应测试文件完整路径                                                 |
| ------------------------------------------------------ | ---------------------------------------------------------- |
| `/Users/junix/knowledge-forge-office/knowledge_forge/utils/helpers.py`          | `/Users/junix/knowledge-forge-office/tests/utils/test_helpers.py`          |
| `/Users/junix/knowledge-forge-office/knowledge_forge/core/algorithms/sorter.py` | `/Users/junix/knowledge-forge-office/tests/core/algorithms/test_sorter.py` |

按照以上规范创建单元测试，可确保项目结构统一、可维护性强，并方便测试框架（如 `pytest`）的自动发现。
