import os
import datetime
import argparse


def set_posts_root_folder() -> bool:
    """
    For now let's just return true
    :return: true, when every ok, false other wise, and will print errmsg this func self.
    """
    return True


def get_posts_foot_folder() -> str:
    return "F:"


def create():
    print('create called')
    meta = """
    #+BEGIN_COMMENT\n.. title: %s\n.. slug: %s\n.. date: %s\n.. tags:
.. category:
.. link:
.. description:
.. type: text
#+END_COMMENT             

    """
    file_part_path = input("Please input the post(need .org)")
    base_name = os.path.basename(file_part_path)
    slug = file_part_path.replace(os.path.sep, '_').replace(' ', '_')
    # how to format time?
    date = datetime.datetime.now().isoformat()
    meta = meta % (base_name, slug, date)
    file_full_path = os.path.join(get_posts_foot_folder(), file_part_path)
    if os.path.exists(file_full_path):
        exit('already exists: {}'.format(file_full_path))
    open(file_full_path, encoding='utf-8', mode='w').write(meta)


def open_in_emacs(path):
    pass


def fix_meta():
    pass


def main():
    parser = argparse.ArgumentParser(description='It\'s a posts util, for now only I use,'
                                                 ' because only I use the posts folder struct')
    subparsers = parser.add_subparsers()

    parser_create = subparsers.add_parser("create")
    parser_fix_meta = subparsers.add_parser("fix_meta")

    parser_create.set_defaults(func=create)
    parser_fix_meta.set_defaults(func=fix_meta)


if __name__ == "__main__":
    main()
