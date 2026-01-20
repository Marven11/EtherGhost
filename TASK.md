# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 使用浏览器MCP探索当前主页功能，报告当前session-icon-others菜单有什么功能，输出到/tmp规划文件夹中的HOMEPAGE.md中
- [ ] 你在commit 0028586完成了批量选择并测试webshell的功能，但是前端有一些逻辑问题需要修复
  - 当用户右键某个webshell并选择“多选webshell”时，这个webshell需要被选中
  - 当前没有选择webshell时多选模式没有自动退出，应该改成会自动退出
  - webshell的描述文本可以被光标滑动选中，这会干扰点击操作，需要改成不可被选中
- [ ] 打开浏览器MCP，测试以上功能，截图并询问视觉大模型是否存在相关组件

# 暂时搁置

# 注意

- 使用nix develop --command poetry run python -m ether_ghost --no-browser启动API服务器，不要自动带起浏览器
- 测试前端时，先在一个终端中启动API服务器，再进入frontend/在另一个终端启动npm run dev
- 缺少frontend/时: 使用nix develop --command poetry run build-frontend构建前端
- 需要在浏览器中右键元素时：使用event而非.click函数
- 使用浏览器时避免使用verbose查看html

