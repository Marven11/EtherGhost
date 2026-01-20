# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 使用浏览器MCP探索当前主页功能，报告当前session-icon-others菜单有什么功能，输出到/tmp规划文件夹中的HOMEPAGE.md中
- [ ] 你在commit 0028586完成了批量选择并测试webshell的功能，查看这个commit的git diff以及其中的TASK.md，有这些问题需要修复
  - 大量无用注释
  - 在计算html中包含selectedSessionIds.has(session.id) && !batchOperationStatus[session.id],等复杂逻辑
    - class应该直接通过ref指定
    - 是否显示应该通过v-if+外部ref变量表示
    - html仅通过读取这两个ref计算
  - 鼠标悬浮在exit-multiselect-button按钮上时的描边没有动画
  - 批量测试等功能的实现没有提取到独立的函数中而是全部集中在HomeMain.vue中
  - 批量测试的功能没有并发测试，而是悲观地认为“不应该给服务器造成压力”而一个个测试
- [ ] 添加批量测试webshell的功能
  - 对选择的webshell进行测试，测试成功后通过小圆点显示状态
- [ ] 打开浏览器MCP，测试以上功能，截图并询问视觉大模型是否存在相关组件

# 暂时搁置

# 注意

- 使用nix develop --command poetry run python -m ether_ghost --no-browser启动API服务器，不要自动带起浏览器
- 测试前端时，先在一个终端中启动API服务器，再进入frontend/在另一个终端启动npm run dev
- 缺少frontend/时: 使用nix develop --command poetry run build-frontend构建前端
- 需要在浏览器中右键元素时：使用event而非.click函数
- 使用浏览器时避免使用verbose查看html

