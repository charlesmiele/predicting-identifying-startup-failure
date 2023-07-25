import os


def count_files_recursively(directory):
    file_count = 0

    for root, _, files in os.walk(directory):
        file_count += len(files)

    return file_count


# Example usage:
directory_path = '/path/to/your/directory'
num_files = count_files_recursively(directory_path)
