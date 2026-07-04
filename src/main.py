import os
import shutil
import sys
from textnode import * 

base_path = "/"

def main():
    args = sys.argv
    if len(args) == 2:
        base_path = args[1]

    copy_static()

def copy_static():

    path = "content"
    stat = "static"
    dest = "docs"

    if os.path.exists(path) == False or os.path.exists(path) == False:
        raise Exception("path do not exist!")

    #clean old staff
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.mkdir(dest)

    #copy new 
    copy_file(path, dest)
    copy_file(stat, dest)

    #generate HTML
    generate_files(path, dest)

def copy_file(path, dest):
    files = os.listdir(path)

    for file in files: 
        f_path = f"{path}/{file}"
        f_dest = f"{dest}/{file}"

        if os.path.isfile(f_path):
            shutil.copy(f_path, f_dest)
        else:
            os.mkdir(f_dest)
            copy_file(f_path, f_dest)

def generate_files(path, dest):
    files = os.listdir(path)

    for file in files: 
        f_path = f"{path}/{file}"
        f_dest = f"{dest}/{file}"

        if os.path.isfile(f_path):
            generate_page(f_path, "template.html", f_dest.replace("md", "html"))
        else:
            if os.path.isdir(f_dest) == False:
                os.mkdir(f_dest)
            generate_files(f_path, f_dest)

def generate_page(path, template, dest):
    print(f"Generating page from {path} to {dest} using {template}")

    with open(path, "r") as f:
        text = f.read()

    with open(template, "r") as f:
        temp = f.read()

    if text == "":
        raise Exception("Marckdown file is empty")
        
    if temp == "":
        raise Exception("Template file is empty")

    title = extract_title(text)

    node = markdown_to_html_node(text)
    html = node.to_html().replace('src="/', f'src="{base_path}').replace('href="/', f'href="{base_path}')

    rez = temp.replace("{{ Content }}", html).replace("{{ Title }}", title) 

    with open(dest, "w") as f:
        des_f = f.write(rez)


if __name__ == "__main__":
    main()
