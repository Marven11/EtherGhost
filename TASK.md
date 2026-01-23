# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 你在66c2274完成了批量执行命令的功能，查看并改进
  - 其使用localStorage保存内容，这打破了项目的惯例
    - 改成和其他页面一致的使用参数传参，用空格分隔
  - 代码过长
    - 考虑将webshell组件等组件抽离出来
    - 大量注释
  - getTypeCode的设计不合理，api本身已经返回了LINUX_CMD_ONELINER等type，应该直接使用
  - 目标: 700行以内
- [ ] 打开浏览器MCP，测试以上功能，截图并询问视觉大模型是否存在相关组件
  - 测试执行功能是否可以正常使用
  - 测试导出功能是否可以正确导出json

# 暂时搁置

# 注意

- 使用nix develop --command poetry run python -m ether_ghost --no-browser启动API服务器，不要自动带起浏览器
- 测试前端时，先在一个终端中启动API服务器，再进入frontend/在另一个终端启动npm run dev
- 缺少public/时: 使用nix develop --command poetry run build-frontend构建前端
- 需要在浏览器中右键元素时：使用event而非.click函数
- 使用浏览器时避免使用verbose查看html

