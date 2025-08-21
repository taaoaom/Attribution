import asyncio
import logging
import os
import random
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from tqdm import tqdm

logging.basicConfig(filename='compilation_obf.log', level=logging.ERROR)

def load_config(config_file: str):
    with open(config_file, "r") as f:
        return yaml.safe_load(f)

def sanitize_path(path: str) -> str:
    """Sanitize the input path to prevent directory traversal."""
    return os.path.normpath(path).lstrip(os.sep)

def generate_compiler_cmd(compiler: str, source_file: str, output_file: str, obfuscate: bool) -> List[str]:
    """Generate compiler command based on the compiler type and obfuscation flag."""
    if not obfuscate:
        if compiler == 'clang++':
            return ["clang++", source_file, "-o", output_file]
        elif compiler == 'g++':
            return ["g++", source_file, "-o", output_file]
    
    if compiler == 'clang++':
        return generate_clang_cmd(source_file, output_file)
    elif compiler == 'g++':
        return generate_gcc_cmd(source_file, output_file)
    else:
        raise ValueError(f"Unsupported compiler: {compiler}")

def generate_clang_cmd(source_file: str, output_file: str) -> List[str]:
    """Generate Clang++ compilation command with obfuscation options."""
    cmd = ["clang++", source_file, "-o", output_file]
    new_cmd = False
    
    options = config["clang_options"]
    
    if random.choice([True, False]):
        cmd.append("-s")
        new_cmd = True

    for option, params in options.items():
        if random.choice([True, False]):
            cmd.append("-mllvm")
            cmd.append(f'-{option}')
            new_cmd = True
            if params:
                if random.choice([True, False]):
                    for key, value in params.items():
                        cmd.append("-mllvm")
                        cmd.append(f"-{option}_{key}={random.choice(value)}")

    if not new_cmd:
        return ["clang++", source_file, "-o", output_file, "-s", "-mllvm", "-sub", "-mllvm", "-fla", "-mllvm", "-bcf"]

    return cmd

def generate_gcc_cmd(source_file: str, output_file: str) -> List[str]:
    """Generate G++ compilation command with random optimization options."""
    cmd = ["g++", source_file, "-o", output_file]
    new_cmd = False

    # Randomly add -s (strip symbols)
    if random.choice([True, False]):
        cmd.append("-s")
        new_cmd = True
    
    # Randomly choose between -O2 and -O3, or neither
    optimization = random.choice(["-O2", "-O3", None])
    if optimization:
        cmd.append(optimization)
        new_cmd = True

    if not new_cmd:
        return ["g++", source_file, "-o", output_file, "-s", "-O2"]
    
    return cmd

async def compile_file_async(compiler: str, src_file: Path, output_file: Path, semaphore: asyncio.Semaphore, pbar: tqdm, obfuscate: bool):
    """Compile a single file asynchronously."""
    async with semaphore:
        cmd = generate_compiler_cmd(compiler, str(src_file), str(output_file), obfuscate)
        try:
            logging.info(f'Starting compilation of {src_file} with {compiler}: {cmd}')
            process = await asyncio.create_subprocess_exec(
                *cmd, 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_message = stderr.decode() if stderr else "Unknown error"
                logging.error(f'Error compiling {src_file}, {compiler}')   
            else:
                logging.info(f'Successfully compiled {src_file}')
        except Exception as e:
            logging.error(f'Unexpected error compiling {src_file}: {str(e)}')
        finally:
            pbar.update(1)
            logging.info(f'Completed compilation attempt of {src_file} with {compiler}')

async def run_compilation(config, obfuscate: bool):
    """Run the compilation process with given configuration and obfuscation flag."""
    SRC_DIR = Path(config["src_dir_obf"]) if obfuscate else Path(config["src_dir_nor"])
    COMPILED_DIR = Path(config["compiled_dir"])
    COMPILERS = config["compilers"]

    cpp_files = list(SRC_DIR.rglob('*.cpp'))
    total_compilations = len(cpp_files) * len(COMPILERS)
    
    semaphore = asyncio.Semaphore(os.cpu_count() or 1)
    
    with tqdm(total=total_compilations, desc=f"Compiling files ({'obfuscated' if obfuscate else 'normal'})") as pbar:
        tasks = []
        for src_file in cpp_files:
            rel_path = src_file.relative_to(SRC_DIR)
            parts = rel_path.parts
            if len(parts) >= 3:
                username, year, filename = parts[:3]
                
                for compiler_name, compiler_path in COMPILERS.items():
                    output_dir = COMPILED_DIR / ('obfuscated' if obfuscate else 'normal') / compiler_name / username / year
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    output_file = output_dir / (src_file.stem + ".exe")
                    task = asyncio.create_task(compile_file_async(compiler_path, src_file, output_file, semaphore, pbar, obfuscate))
                    tasks.append(task)
            else:
                logging.warning(f"Skipping file with unexpected path structure: {src_file}")
        
        await asyncio.gather(*tasks)

async def main():
    """Main function to run compilation processes."""
    # Run normal compilation
    await run_compilation(config, obfuscate=False)
    
    # Run obfuscated compilation
    await run_compilation(config, obfuscate=True)

if __name__ == "__main__":
    config = load_config("config.yaml")
    asyncio.run(main())