import os
import asyncio

class Obfuscator:
    def __init__(self, config):
        self.base_path = config["base_path"]
        self.obfuscated_base_path = config["obfuscated_base_path"]

    async def obfuscate_files(self):
        for compiler in os.listdir(self.base_path):
            compiler_path = os.path.join(self.base_path, compiler)
            if os.path.isdir(compiler_path):
                for user in os.listdir(compiler_path):
                    user_path = os.path.join(compiler_path, user)
                    if os.path.isdir(user_path):
                        for year in os.listdir(user_path):
                            year_path = os.path.join(user_path, year)
                            if os.path.isdir(year_path):
                                for source_file in os.listdir(year_path):
                                    if source_file.endswith('.exe'):
                                        source_file_path = os.path.join(year_path, source_file)
                                        await self.obfuscate_file(source_file_path, compiler, user, year)

    async def obfuscate_file(self, source_file_path, compiler, user, year):
        source_file_name, source_file_extension = os.path.splitext(os.path.basename(source_file_path))
        packed_file_name = f"{source_file_name}-packed{source_file_extension}"

        obfuscated_user_path = os.path.join(self.obfuscated_base_path, compiler, user, year)
        os.makedirs(obfuscated_user_path, exist_ok=True)
        output_file_path = os.path.join(obfuscated_user_path, packed_file_name)

        # Compile using UPX
        upx_cmd = f'upx --best -k --le -o "{output_file_path}" "{source_file_path}"'
        print(f'Packing {source_file_path} with UPX...')
        try:
            proc = await asyncio.create_subprocess_shell(upx_cmd)
            await proc.communicate()
            if proc.returncode == 0:
                print(f'Successfully obfuscated {source_file_path} with UPX')
            else:
                print(f'Failed to obfuscated {source_file_path} with UPX')
        except Exception as e:
            print(f'Failed to obfuscated {source_file_path} with UPX: {e}')
