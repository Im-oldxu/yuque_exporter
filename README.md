
# 初始化项目

- 1、建议使用RockyLinux系统
- 2、安装项目依赖模块： `pip3 install huepy pyuque prettytable`


# 循环备份语雀的所有知识库

修改while_backup_yuque.sh文件中的Token，然后执行脚本即可。

- 00-yuque_getid.py    	用来获取对应语雀中各个知识库的ID
- 01_yuque_exporter.py 	用来备份每一个语雀的知识库文章，但需要传递对应的知识库ID
- while_backup_yuque.sh	获取语雀知识库所有的ID，循环传递给 01_yuque_exporter 进行循环备份所有知识库


# 备份单个知识库

yuque_exporter.py		用来备份语雀单个知识库，需要修改文件中的Token变量，（备份单个知识库时使用）



# 备份的内容会出现在/YuqueExport 目录下
