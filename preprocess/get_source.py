import os
import pandas as pd
import tarfile
import logging
import hashlib

logging.basicConfig(filename='../../error.txt', level=logging.ERROR)

src_folder = "../../src-arch"
ext_folder = "../../res/src-ext"
names_folder = "../../res/names"
source_code_folder = "../../res/submissions"
user_file_count = {}

def remove_empty_folders(directory):
    for subdir in os.listdir(directory):
        path = os.path.join(directory, subdir)

        if os.path.isdir(path):
            remove_empty_folders(path)
            
            if not os.listdir(path):
                os.rmdir(path)
                print(f"Deleted empty directory: {path}")

def print_file_counts(base_path):
    for name_dir in os.listdir(base_path):
        name_path = os.path.join(base_path, name_dir)
        if os.path.isdir(name_path):
            count = sum([1 for _ in os.listdir(name_path) if os.path.isfile(os.path.join(name_path, _))])
            print(f"{name_dir}: {count}")

def clean_name(name):
    return ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in name)

def extract_tar_bz2(filename, dest_folder):
    with tarfile.open(filename, 'r:bz2') as archive:
        archive.extractall(dest_folder)

def process_files(file_list):
    if not os.path.exists(source_code_folder):
        os.makedirs(source_code_folder)

    for src_file in file_list:
        if src_file.endswith(".csv.tar.bz2"):
            base_name = src_file.split('.')[0]

            extract_tar_bz2(os.path.join(src_folder, src_file), ext_folder)

            csv_file = os.path.join(ext_folder, f"{base_name}.csv")
            if not os.path.exists(csv_file):
                logging.error(f"Expected CSV file {csv_file} not found after extraction.")
                continue

            print("\n============== Extracted csv ==================\n")

            try:
                data = pd.read_csv(csv_file, encoding='utf-8', dtype={'round': str})
            except Exception as e:
                logging.error(f"Read CSV Failed for {csv_file}. Error: {e}")
                continue

            file_col = 'full_path' if base_name == 'gcj2020' else 'file'

            if not all(col in data.columns for col in ['username', file_col, 'flines']):
                logging.error(f"Expected columns not found in {csv_file}")
                continue

            names_txt_file = os.path.join(names_folder, f"{base_name}.txt")
            if not os.path.exists(names_txt_file):
                logging.error(f"Expected names file {names_txt_file} not found.")
                continue

            with open(names_txt_file, 'r', encoding='utf-8') as f:
                names = [name.strip() for name in f.readlines()]

            for name in names:
                clean_username = clean_name(name)
                user_data = data[data['username'] == name]
                cpp_files = user_data[user_data[file_col].str.lower().str.endswith('.cpp')]

                user_folder = os.path.join(source_code_folder, clean_username)
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)

                user_file_count.setdefault(clean_username, 0)
                for _, record_data in cpp_files.iterrows():
                    user_file_count[clean_username] += 1
                    file_name = f"{clean_username}-{user_file_count[clean_username]}.cpp"

                    try:
                        with open(os.path.join(user_folder, file_name), 'w', encoding='utf-8') as cpp_file:
                            cpp_file.write(record_data['flines'])
                    except Exception as e:
                        logging.error(f"Write CPP Failed for {file_name}. Error: {e}")

                print(f"Processed {len(cpp_files)} cpp files for {name}. Total: {user_file_count[clean_username]}")

            # os.remove(csv_file)


# selected_files = os.listdir(src_folder)
# # selected_files = ['gcj2008.csv.tar.bz2']
# process_files(selected_files)


class MD5Checker:
    def __init__(self, base_path):
        self.base_path = base_path
        self.md5_dict = {}

    def calculate_md5(self, file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read()
            md5 = hashlib.md5(file_data).hexdigest()
        return md5

    def process_file(self, file_path, user, file_name):
        md5_value = self.calculate_md5(file_path)

        if md5_value not in self.md5_dict:
            self.md5_dict[md5_value] = {'username': user, 'file_name': file_name}
        else:
            existing_record = self.md5_dict[md5_value]
            print(f"\nDuplicate MD5 value found: {md5_value}")
            print(f"Existing record: username: {existing_record['username']}, file_name: {existing_record['file_name']}")
            print(f"New record: username: {user}, file_name: {file_name}\n")

            os.remove(file_path)

    def process_files(self):
        for user in os.listdir(self.base_path):
            user_path = os.path.join(self.base_path, user)
            for file_name in os.listdir(user_path):
                file_path = os.path.join(user_path, file_name)
                if file_path.endswith('.cpp'):
                    self.process_file(file_path, user, file_name)

# checker = MD5Checker(source_code_folder)
# checker.process_files()
