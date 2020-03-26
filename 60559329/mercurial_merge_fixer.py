import codecs
import sys
from shutil import move

def merge_line_fix(line):
    return line.replace("=======", "\n=======").replace(">>>>>>>", "\n>>>>>>>")

def main():
    file_path = sys.argv[1]
    with codecs.open(file_path, "r", "utf-8") as in_fh:
        with codecs.open(file_path + ".mergeconflict", "w", "utf-8") as out_fh:
            for line in in_fh:
                out_fh.write(merge_line_fix(line))
    move(file_path + ".mergeconflict", file_path)

if __name__ == '__main__':
    main()