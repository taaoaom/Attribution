import os
import hashlib

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