import os
import math

def count_submissions_with_stats(submissions_dir):
    user_files = {}  # Dictionary to store the number of files per user

    for root, dirs, files in os.walk(submissions_dir):
        # If at the root level, subdirectories are usernames
        if root == submissions_dir:
            for user in dirs:
                user_files[user] = 0  # Initialize file count for each user
        
        # If deeper in the directory structure, identify the username
        else:
            # Extract the username from the root path
            relative_path = os.path.relpath(root, submissions_dir)
            parts = relative_path.split(os.sep)
            
            if len(parts) >= 1:  # Ensure the path has at least a username
                user = parts[0]
                if user in user_files:  # Update only if it's a valid username
                    user_files[user] += len(files)
    
    # Debugging: Print the file counts for each user
    # print(f"File counts per user: {user_files}")

    # Calculate total files and stats
    total_files = sum(user_files.values())
    user_count = len(user_files)
    
    if user_count == 0:
        raise ValueError("No users detected. Please check the directory structure.")
    
    mean = total_files / user_count

    # Calculate the standard deviation
    squared_diffs = [(file_count - mean) ** 2 for file_count in user_files.values()]
    variance = sum(squared_diffs) / user_count
    std_dev = math.sqrt(variance)
    
    return user_count, total_files, mean, std_dev

# Path to the folder
folder_path = '../../res/compiled/normal/clang'

# Call the function and display results
username_count, file_count, mean, std_dev = count_submissions_with_stats(folder_path)
print(f"Total unique usernames: {username_count}")
print(f"Total number of files: {file_count}")
print(f"Average files per user: {mean:.2f}")
print(f"Standard deviation of files per user: {std_dev:.2f}")
