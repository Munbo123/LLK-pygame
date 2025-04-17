# 输出src文件夹结构的树

import os

def print_directory_tree(startpath, prefix=""):
    for item in os.listdir(startpath):
        item_path = os.path.join(startpath, item)
        if os.path.isdir(item_path):
            print(f"{prefix}├── {item}/")
            print_directory_tree(item_path, prefix + "│   ")
        else:
            print(f"{prefix}├── {item}")

if __name__ == "__main__":
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
    print_directory_tree(src_path)
