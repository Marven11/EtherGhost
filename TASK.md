# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 通过api访问当前“测试dell nixos”webshell是否可以使用
- [ ] 当前ether_ghost/session_connector.py很乱，大量违反简洁原则和深层价值观
  - 删除注释，调整import
  - 需要计划调整各类定义的位置：函数应该放在哪里，全局变量、函数、对象应该放在什么位置
  - 删除所有不需要的函数么函数是根本不需要实现的，有什么函数只是wraper且是否应该删除
- [ ] register_direct_session_class使用元编程定义类，严重违反简洁原则，重构为在各个webshell的实现中手动定义每个connector并用装饰器注册
- [ ] 再次通过api访问当前“测试dell nixos”webshell是否可以使用

# 暂时搁置

- [ ] 添加批量测试webshell的功能 - 得先重构当前的右键菜单系统

# 注意

- 使用nix develop --command poetry run python -m ether_ghost --no-browser启动API服务器，不要自动带起浏览器
- 测试前端时，先在一个终端中启动API服务器，再进入frontend/在另一个终端启动npm run dev
- 缺少frontend/时: 使用nix develop --command poetry run build-frontend构建前端
- 需要在浏览器中右键元素时：使用event而非.click函数
- 使用浏览器时避免使用verbose查看html

