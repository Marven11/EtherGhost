# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 当前项目的webui中的某些按钮比较难看，你需要重构
  - 问题：某些按钮是扁扁的文字结构，且样式不统一
  - 这是一个较大的重构，需要仔细列出并仔细测试每个修改的按钮
  - 期望：有一个component统一这些按钮的实现，并改进样式，使其使用这个项目定义好的icon
  - 自由：
    - 有30个小时完成这个任务，慢慢完成
    - 积极使用视觉大模型
  - 限制：
    - ralph loop: 运行超过2小时会被自动杀死并重启以避免陷入僵局，你可以在./tmp留下任何文档以在被重启后继续运行
    - 报告完成任务：在使用视觉大模型确认完成任务后可以sleep
    - 必须使用视觉大模型验证任务，以主页样式为8.5分，使用十分制给完成的每一个页面打分
    - 如果你发现任务好像已经完成：使用浏览器MCP重新测试功能并使用视觉大模型重新检查

# 暂时搁置

# 注意

- 使用nix develop --command poetry run python -m ether_ghost --no-browser启动API服务器，不要自动带起浏览器
- 测试前端时，先在一个终端中启动API服务器，再进入frontend/在另一个终端启动npm run dev
- 缺少public/时: 使用nix develop --command poetry run build-frontend构建前端
- 需要在浏览器中右键元素时：使用event而非.click函数
- 使用浏览器时避免使用verbose查看html

