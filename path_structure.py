#pylint: disable= missing-module-docstring, missing-function-docstring, missing-final-newline
#pylint: disable= line-too-long, redefined-outer-name
import os

def print_files_in_dir(path, indent, file_to_write):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)) and 'input' not in path and 'output' not in path:
            file_to_write.write(' ' * indent + file + '\n')   # Запись в файл вместо print

def print_dir_structure(startpath, file_to_write):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = 4 * (level)
        file_to_write.write('{}{}/\n'.format(' ' * indent, os.path.basename(root)))   # Запись в файл вместо print
        if 'input' not in root and 'output' not in root and 'statistic' not in root:
            print_files_in_dir(root, indent + 4, file_to_write)                # Передаем файл в функцию

file_to_write = open('directory_structure.txt', 'w', encoding='utf-8')
print_dir_structure('./', file_to_write)
file_to_write.close()