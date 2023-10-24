import sys
import re
import os
from urllib import parse
from pyuque.client import Yuque
import requests
import time
from huepy import *
from prettytable import PrettyTable
from datetime import datetime

# 语雀对应的Token (自行修改)
Token = "d5mYnSV0EReiQ7XQkkEqa"

# 备份的目录
current_date = datetime.now()
formatted_date = current_date.strftime("backup_%Y_%m_%d")
time_dir = "/YuqueExport"
Base_Dir = os.path.join(time_dir, formatted_date)
# 确保目录存在，如果不存在则创建
if not os.path.exists(Base_Dir):
    os.makedirs(Base_Dir)




headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "X-Auth-Token": Token
    }

used_uuids = []
created_dir = {}

# 获取仓库列表
def get_repos(user_id):
    repos = {}
    for repo in yuque.user_list_repos(user_id)['data']:
        repo_id = str(repo['id'])
        repo_name = repo['name']
        repos[repo_id] = repo_name
    return repos

# 获取文档Markdown代码
def get_body(repo_id, doc_id):
    doc = yuque.doc_get(repo_id, doc_id)
    body = doc['data']['body']
    body = re.sub("<a name=\"(\w.*)\"></a>", "", body)                 # 正则去除语雀导出的<a>标签
    body = re.sub(r'\<br \/\>', "\n", body)                            # 正则去除语雀导出的
    body = re.sub(r'\<br \/\>!\[image.png\]', "\n![image.png]", body)  # 正则去除语雀导出的图片后紧跟的
    body = re.sub(r'\)\<br \/\>', ")\n", body)                         # 正则去除语雀导出的图片后紧跟的
    body = re.sub(r'png[#?](.*)+', 'png)', body)                       # 正则去除语雀图片链接特殊符号后的字符串
    body = re.sub(r'jpeg[#?](.*)+', 'jpeg)', body)                     # 正则去除语雀图片链接特殊符号后的字符串
    return body

# 解析文档Markdown代码
def download_md(repo_id, doc_id, doc_title, repo_dir, assets_dir):
    body = get_body(repo_id[0], doc_id)

    # 保存图片
    pattern_images = r'(\!\[(.*)\]\((https:\/\/cdn\.nlark\.com\/yuque.*\/(\d+)\/(.*?\.[a-zA-z]+)).*\))'
    images = [index for index in re.findall(pattern_images, body)]
    if images:
        for index, image in enumerate(images):
            image_body = image[0]                                # 图片完整代码
            image_url = image[2]                                 # 图片链接
            image_suffix = image_url.split(".")[-1]              # 图片后缀
            local_abs_path = f"{assets_dir}/{doc_title}-{str(index)}.{image_suffix}"                # 保存图片的绝对路径
            doc_title_temp = doc_title.replace(" ", "%20").replace("(", "%28").replace(")", "%29").replace("<", "%3C").replace(">", "%3E")  # 对特殊符号进行编码
            local_md_path = f"![{doc_title_temp}-{str(index)}](assets/{doc_title_temp}-{str(index)}.{image_suffix})"  # 
            local_abs_path = local_abs_path.replace("<", "%3C").replace(">", "%3E")  # 对特殊符号进行编码
            download_images(image_url, local_abs_path)     # 下载图片
            body = body.replace(image_body, local_md_path)       # 替换链接

    # 保存附件
    pattern_annexes = r'(\[(.*)\]\((https:\/\/www\.yuque\.com\/attachments\/yuque.*\/(\d+)\/(.*?\.[a-zA-z]+)).*\))'
    annexes = [index for index in re.findall(pattern_annexes, body)]
    if annexes:
        for index, annex in enumerate(annexes):
            annex_body = annex[0]                                # 附件完整代码 [xxx.zip](https://www.yuque.com/attachments/yuque/.../xxx.zip)
            annex_name = annex[1]                                # 附件名称 xxx.zip
            annex_url = re.findall(r'\((https:\/\/.*?)\)', annex_body)                # 从附件代码中提取附件链接
            annex_url = annex_url[0].replace("/attachments/", "/api/v2/attachments/") # 替换为附件API
            local_abs_path = f"{assets_dir}/{annex_name}"           # 保存附件的绝对路径
            local_md_path = f"[{annex_name}](assets/{annex_name})"  # 附件相对路径完整代码
            download_annex(annex_url, local_abs_path)         # 下载附件
            body = body.replace(annex_body, local_md_path)          # 替换链接

    # 保存文档
    markdown_path = f"{repo_dir}/{doc_title}.md"
    markdown_path = markdown_path.replace("<", "%3C").replace(">", "%3E")
    with open(markdown_path, "w", encoding="utf-8",errors="ignore") as f:
        f.write(body)

# 下载图片
def download_images(image, local_name):
    print(good(f"Download {local_name} ..."))
    re = requests.get(image,headers=headers)
    with open(local_name, "wb") as f:
        for chunk in re.iter_content(chunk_size=128):
                f.write(chunk)


# 下载附件
def download_annex(annex, local_name):
    print(good(f"Download {local_name} ..."))
    re = requests.get(annex,headers=headers)
    with open(local_name, "wb") as f:
        for chunk in re.iter_content(chunk_size=128):
                f.write(chunk)  

# 目录创建
def create_dir(name, parent_dir):
    # 创建一个新目录并返回其完整路径
    directory = os.path.join(parent_dir, name)
    os.makedirs(directory, exist_ok=True)
    return directory

# 整体处理
def process_data(repo_id,data,current_dir,current_assets_dir):
    for uuid, item in data.items():
            # 判断该uuids是否已经索引过
        if uuid in used_uuids:
            continue

            # 获取根目录doc
        if item["type"] == "DOC" and item["depth"] == 1:
            # 获取文档内容,将不能作为文件名的字符进行编码
            for char in r'/\<>?:"|*':
                doc_title = item["title"].replace(char, parse.quote_plus(char))
            print(run(cyan(f"Get Doc {doc_title} ...")))
            download_md(repo_id, item["doc_id"], doc_title, current_dir, current_assets_dir)
            used_uuids.append(uuid)

            # 处理一级目录及assets目录
        elif item["type"] == "TITLE" and item["depth"] == 1:
            root_dir = create_dir(item["title"], current_dir)
            root_assets_dir = create_dir("assets",root_dir)
            created_dir[uuid] = root_dir
            used_uuids.append(uuid)
        
            # 创建子目录
        elif item["type"] == "TITLE" and item["parent_uuid"] is not None:
            current_uuid = uuid
            path = []
            while current_uuid != "":
                for key, value in data.items():
                    if key == current_uuid:
                        parent_uuid = value["parent_uuid"]
                        title = value["title"]
                        if parent_uuid == "":
                            current_uuid = ""
                            path.append(title)
                        else:
                            current_uuid = parent_uuid
                            path.append(title)
            path.reverse()
            result = "/".join(path)
            if result[-1] == " ":  # 检测最后一位是否为空格
                result = result.rstrip()  # 删除末尾的空格
            parent_dir = create_dir(result, current_dir)
            parent_assets_dir = create_dir("assets", parent_dir)
            created_dir[uuid] = parent_dir
            used_uuids.append(uuid)

            # 下载子目录文件至子目录下
        elif item["type"] == "DOC" and item["depth"] > 1:            
            if item["parent_uuid"] in created_dir:
                for char in r'/\<>?:"|*':
                    doc_title = item["title"].replace(char, parse.quote_plus(char))
                print(run(cyan(f"Get Doc {doc_title} ...")))
                tmp_assets_dir = created_dir[item["parent_uuid"]] + "/" + "assets"
                download_md(repo_id, item["doc_id"], doc_title, created_dir[item["parent_uuid"]], tmp_assets_dir)
                used_uuids.append(uuid)
                time.sleep(1)
            else:
                break

def main():
    # 获取用户ID
    user_id = yuque.user.get()['data']['id']

    # 获取知识库列表
    all_repos = get_repos(user_id)
    repos_table = PrettyTable(["ID", "Name"])
    for repo_id, repo_name in all_repos.items():
        repos_table.add_row([repo_id, repo_name])
    print(repos_table)

    # 输入知识库ID,可输入多个,以逗号分隔
    input_ids = input(lcyan("Repo ID (Example: 111,222): "))
    temp_ids = [ temp.strip() for temp in input_ids.split(",") ]

    # 检查全部知识库id
    for temp_id in temp_ids:
        if temp_id not in all_repos:
            print(bad(red(f"Repo ID {temp_id} Not Found !")))
            sys.exit(0)
    
    # 获取知识库目录结构
    uuid_dict = {}
    for item in yuque.repo_toc(temp_id)['data']:
        uuid_dict[item['uuid']] = item

    # 创建知识库目录及存放资源的子目录
    parent_dir = create_dir(all_repos[temp_id],base_dir)
    parent_assets_dir = create_dir("assets",parent_dir)

    # 综合处理
    process_data(temp_ids,uuid_dict,parent_dir,parent_assets_dir)
        

if __name__ == '__main__':
    token = Token
    yuque = Yuque(token)
    base_dir = Base_Dir
    main()
