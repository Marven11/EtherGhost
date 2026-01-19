# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 之前重构右键菜单之后点击session-icon-others不会弹出菜单，需要修复
  - 重构之前的功能：无论是右键session还是点击菜单按钮都会弹出功能列表
- [ ] 打开浏览器MCP，测试以上功能，截图并询问视觉大模型是否存在相关组件

# 暂时搁置

- [ ] 添加批量测试webshell的功能 - 得先重构当前的右键菜单系统

# 注意

- 使用nix develop --command poetry run python -m ether_ghost --no-browser启动API服务器，不要自动带起浏览器
- 测试前端时，先在一个终端中启动API服务器，再进入frontend/在另一个终端启动npm run dev
- 缺少frontend/时: 使用nix develop --command poetry run build-frontend构建前端
- 需要在浏览器中右键元素时：使用event而非.click函数
- 使用浏览器时避免使用verbose查看html

