#!/usr/bin/env python3

import os
import sys


def parse_header_line(header_line):
    level = len(header_line.split(" ")[0])
    title = header_line[level + 1 :].rstrip()
    anchor_title = title.lower().replace(" ", "-")
    ignored_chars = [":", "+", ",", "!", '"', "(", ")"]
    for ignored_char in ignored_chars:
        anchor_title = anchor_title.replace(ignored_char, "")
    return level, title, anchor_title


def repeat(s, nb):
    r = ""
    for i in range(nb):
        r = r + s
    return r


def toc_link():
    toc_image = "docs/toc.png"
    # <div style="text-align: right"> your-text-here </div>
    image_link = f"[![TOC]({toc_image})](#TOC)"
    r = f"{image_link}\n"
    return r


def is_header_line(line):
    return line.startswith("#") and not (line.startswith("#include"))


def make_toc(file):
    with open(file, "r") as f:
        lines = f.readlines()
    header_lines = [line[:-1] for line in lines if is_header_line(line)]
    toc = '<span id="TOC"/></span>\n\n'
    for header_line in header_lines:
        level, title, anchor_title = parse_header_line(header_line)
        toc = toc + "{}* [{}]({})\n".format(repeat("  ", level - 1), title, "#" + anchor_title)
    return toc


def is_md_block_start(line, md_id):
    # @@md#DockingParams
    result = line.strip().startswith(f"@@md#{md_id}")
    return result


def is_md_block_end(line):
    result = line.strip().startswith("@@md")
    return result


def extract_md_block(file, md_id):
    with open(file, "r") as f:
        lines = f.readlines()
    result = ""
    md_block_started = False
    for line in lines:
        if md_block_started:
            if is_md_block_end(line):
                md_block_started = False
            else:
                result = result + line
        if is_md_block_start(line, md_id):
            md_block_started = True
    return result


def parse_import_line(line):
    """
    @import "app_window_params.h" {md_id=DockingParams}
    """

    def get_string_between(s, after_what, before_what):
        end = s[s.index(after_what) + len(after_what) :]
        middle = end[0 : end.index(before_what)]
        return middle

    imported_file = get_string_between(line, '@import "', '"')
    md_id = get_string_between(line, "md_id=", "}")
    return imported_file, md_id


def process_md_file(input_file, output_file):
    with open(input_file, "r") as f:
        lines = f.readlines()

    content = ""
    for line in lines:
        if line.startswith("@import"):
            imported_file, md_id = parse_import_line(line)
            imported_file = os.path.dirname(input_file) + "/" + imported_file
            content = content + extract_md_block(imported_file, md_id)
        elif line.startswith("[TOC]"):
            content = content + make_toc(input_file)
        elif is_header_line(line):
            # content = content + line + toc_link() # too ugly
            content = content + line
        else:
            content = content + line

    with open(output_file, "w") as f:
        f.write(content)


if __name__ == "__main__":
    this_dir = os.path.dirname(os.path.realpath(__file__)) + "/"
    repo_dir = this_dir + "/../../"
    hello_imgui_dir = repo_dir + "/src/hello_imgui/"

    process_md_file(repo_dir + "README.src.md", repo_dir + "README.md")
    process_md_file(hello_imgui_dir + "hello_imgui_api.src.md", hello_imgui_dir + "hello_imgui_api.md")
