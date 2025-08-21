import os
import tarfile
import re
import logging
from collections import defaultdict
import pandas as pd
from tqdm import tqdm

# Constants
INPUT_CSV_DIR = "../../res/src-arch"
INPUT_TXT_DIR = "../../res/names"
EXTRACTED_CSV_DIR = "../../res/src-ext"
OUTPUT_DIR = "../../res/submissions"
LOG_FILE = "script_execution.log"

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_progress(message):
    """Log progress message to both file and console"""
    logging.info(message)
    print(message)

def sanitize_username(username):
    return re.sub(r'[^\w\-_]', '_', username)

def extract_tar_bz2(file_path, extract_dir):
    try:
        with tarfile.open(file_path, "r:bz2") as tar:
            tar.extractall(path=extract_dir)
        log_progress(f"Successfully extracted {file_path}")
        return os.path.join(extract_dir, os.path.splitext(os.path.basename(file_path))[0])
    except tarfile.TarError as e:
        logging.error(f"Failed to extract {file_path}: {str(e)}")
        raise

def read_names_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            names = [line.strip() for line in f]
        log_progress(f"Read {len(names)} names from {file_path}")
        return names
    except IOError as e:
        logging.error(f"Failed to read {file_path}: {str(e)}")
        raise

def read_csv_with_pandas(csv_file):
    try:
        df = pd.read_csv(csv_file, low_memory=False)
        log_progress(f"Successfully read CSV file: {csv_file}")
        log_progress(f"CSV file shape: {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Failed to read CSV file {csv_file}: {str(e)}")
        raise

def get_file_info(year):
    if year in ['2018', '2019']:
        return 'file', 'CPP'
    elif year == '2020':
        return 'full_path', 'CPP'
    else:
        return 'file', 'cpp'

def save_cpp_file(row, year, cpp_count):
    username = row['username']
    sanitized_username = sanitize_username(username)
    cpp_count[username] += 1
    output_path = os.path.join(OUTPUT_DIR, sanitized_username, year)
    os.makedirs(output_path, exist_ok=True)
    
    _, file_extension = get_file_info(year)
    output_file = f"{sanitized_username}-{year}-{cpp_count[username]}.{file_extension.lower()}"
    
    try:
        with open(os.path.join(output_path, output_file), 'w', encoding='utf-8') as cpp_file:
            cpp_file.write(row['flines'])
        return 1
    except UnicodeEncodeError as e:
        logging.warning(f"Skipped file due to encoding error: {output_file}")
        return 0

def process_csv_and_save_cpp(df, names, year):
    cpp_count = defaultdict(int)
    skipped_count = 0
    try:
        file_column, file_extension = get_file_info(year)
        
        filtered_df = df[df['username'].isin(names) & df[file_column].str.endswith(file_extension)]
        
        processed_count = 0
        for _, row in filtered_df.iterrows():
            result = save_cpp_file(row, year, cpp_count)
            if result == 1:
                processed_count += 1
            else:
                skipped_count += 1
        
        log_progress(f"Processed {processed_count} {file_extension} files for year {year}")
        if skipped_count > 0:
            log_progress(f"Skipped {skipped_count} files due to encoding errors for year {year}")
    except Exception as e:
        logging.error(f"Failed to process CSV data for year {year}: {str(e)}")
        raise

def main():
    log_progress("Starting script execution")
    
    try:
        os.makedirs(EXTRACTED_CSV_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        log_progress("Created necessary directories")

        # Extract all tar.bz2 files (commented out as in the original script)
        # for file in os.listdir(INPUT_CSV_DIR):
        #     if file.endswith('.tar.bz2'):
        #         extract_tar_bz2(os.path.join(INPUT_CSV_DIR, file), EXTRACTED_CSV_DIR)

        for file in os.listdir(INPUT_TXT_DIR):
            if file.endswith('.txt'):
                year = file[3:7]
                names = read_names_from_txt(os.path.join(INPUT_TXT_DIR, file))
                csv_file = os.path.join(EXTRACTED_CSV_DIR, f"gcj{year}.csv")
                if os.path.exists(csv_file):
                    df = read_csv_with_pandas(csv_file)
                    process_csv_and_save_cpp(df, names, year)
                else:
                    logging.warning(f"CSV file for year {year} not found.")

        log_progress("Script execution completed successfully")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        print(f"An error occurred. Please check the log file {LOG_FILE} for details.")

if __name__ == "__main__":
    main()