# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 当前项目在打包时直接使用git仓库自带的public构建结果，但是public文件夹是当前文件夹中的frontend这个子项目的构建结果，这不合理
  - 删除当前仓库的ether_ghost/public文件夹
  - 调整frontend子项目的构建脚本build.sh，使其不要将public文件夹直接输出到ether_ghost文件夹下，而是输出到合适的目录
  - 新建script/文件夹，将build.sh移动到script/文件夹
  - 调整pyproject.toml使其包含构建脚本
  - 调整.gitignore使其不包含这个public文件夹
  - 测试poetry打包并调整
  - 测试nix打包并调整
  - 启动服务器并尝试访问index.html等打包进来的文件，查看服务器是否可以正常返回


# 暂时搁置

- [ ] 重构当前的右键菜单系统
- [ ] 添加批量测试webshell的功能 - 得先重构当前的右键菜单系统
