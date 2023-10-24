#!/usr/bin/bash
# Auth： oldxu.net


# 定义语雀的Token（自行修改）
Token="d5mYnSV0EReiwmNS0PkEqa"


# 1、执行脚本获取所有文档ID的表格
python3 ./00-yuque_getid.py ${Token} > /tmp/doc

while read line
do
	doc_id=$(echo $line |awk -F ':' '{print $1}')
	doc_name=$(echo $line |awk -F ':' '{print $2}')
	echo 备份的文档ID是：$doc_id , 备份对应的知识库是 $doc_name

	# 循环备份对应知识库的内容
	python3 01_yuque_exporter.py ${Token} $doc_id
done < /tmp/doc

# 2、删除对应的文件
rm -f /tmp/doc
