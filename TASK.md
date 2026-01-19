# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 使用浏览器MCP探索当前主页功能，报告当前session-icon-others菜单有什么功能，输出到/tmp规划文件夹中的HOMEPAGE.md中
- [ ] 完成主页多选webshell功能
  - session左上角的小圆点
    - 有以下状态：红色，绿色，黄色闪烁（周期0.5秒）
    - 在未使用时不显示
  - 退出多选模式的按钮
    - 在进入多选模式时显示在右下角
    - 用于退出多选模式或者强行退出批量操作
  - 多选功能
    - 点击session-icon-others可以在选项中找到“多选webshell”功能
    - 选择“多选webshell”后进入多选模式，当前webshell小圆点出现，显示绿色表示选中
    - 在多选模式中可以点击webshell选中，小圆点变绿，再点击一次取消选择，小圆点消失
    - 在多选模式右键点击已经选择的webshell弹出多选模式的右键菜单，可以对选择的webshell进行批量操作
    - 当前没有选择任何webshell时退出多选模式
  - 批量操作
    - 批量对选择的webshell执行操作
      - 同时在对应webshell的左上角显示对应颜色的小圆点
        - 黄色闪烁：正在处理
        - 绿色：成功
        - 红色：失败
      - 当所有webshell都成功或者失败时暂留三秒小圆点状态，然后退出
      - 如果因为某些原因（如网络卡死）用户想打断批量操作，则可以点击退出按钮
    - 功能 - 打印到console: 为了测试多选功能添加的dummy功能，等待0.5秒并打印当前webshell的名字到console
  - 调整CSS并询问视觉大模型
    - 颜色和大小是否和界面风格相同且不突兀，如果突兀则请求视觉大模型提出修改建议，例如“太大了，改小一点”
    - 退出多选模式的按钮是否正常显示，位置是否合适（和添加按钮水平且不贴合边缘），如果不合适则给出建议，例如“贴着边缘，不好看，建议远离边缘”
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

