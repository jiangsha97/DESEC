# get prompts like Fig. 1


import os
import re

import os
import re
import shutil


# secret_dic = {
#     'aws access key id': (r"AKIA[0-9A-Z]{16}", 4),
#     'google oauth client secret': (r"GOCSPX-[a-zA-Z0-9]{28}", 7),
#     'midtrans sandbox server key': (r"SB-Mid-server-[0-9a-zA-Z_-]{24}", 14),
#     'flutterwave live api secret key': (r"FLWPUBK_TEST-[0-9a-f]{32}-X", 13),
#     'flutterwave test api secret key': (r"FLWSECK_TEST-[0-9a-f]{32}-X", 13),
#     'stripe live secret key': (r"sk_live_[0-9a-zA-Z]{24}", 8),
#     'ebay production client id': (r"[a-zA-Z0-9_\-]{8}-[a-zA-Z0-9_\-]{8}-PRD-[a-z0-9]{9}-[a-z0-9]{8}", 0),
#     'github personal access token': (r"ghp_[0-9a-zA-Z]{36}", 4),
#     'github oauth access token': (r"gho_[0-9a-zA-Z]{36}", 4)
# }

secret_dic = {
    'slack incoming web hook url': (r"https:\/\/hooks.slack.com\/services\/[A-Za-z0-9+\/]{44,46}", 33),
    'alibabacloud': (r"LTAI[a-zA-Z0-9]{20}", 4),
    'tencent cloud secret id': (r"AKID[0-9a-zA-Z]{32}", 4),
    'google api key': (r"AIza[0-9A-Za-z\-_]{35}", 4),
    'google oauth client id': (r"[0-9]{12}-[a-z0-9]{32}\.apps\.googleusercontent\.com", 0),
    'stripe test': (r"sk_test_[0-9a-zA-Z]{24}", 8)
}



def process_file(file_path, regex_pattern, n_chars_to_keep, output_dir, subfolder):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception as e:
        print(f"Error in reading {file_path} : {e}")
        return  # Skip current file

    # Find the first matching string and its line number with regular expression
    match = None
    for i, line in enumerate(lines):
        match = re.search(regex_pattern, line)
        if match:
            match_line_idx = i
            break

    if match is None:
        print(f"can not find in {file_path}.")
        return  # Skip current file

    # Get the line on which the match is located and the 7 lines above it (if the top is less than 7 lines, get all)
    start_idx = max(0, match_line_idx - 7)
    end_idx = match_line_idx + 1  # Include current line

    # Keep required lines
    selected_lines = lines[start_idx:end_idx]

    matched_string = match.group(0)
    truncated_matched_string = matched_string[:n_chars_to_keep]
    # Retrieve the first half of the current line (excluding matching string parts)
    start_of_line = lines[match_line_idx][:match.start()]
    # Update the matching line using truncated strings
    truncated_line = start_of_line + truncated_matched_string


    subfolder_output_dir = os.path.join(output_dir, subfolder)
    if not os.path.exists(subfolder_output_dir):
        os.makedirs(subfolder_output_dir)

    output_file_path = os.path.join(subfolder_output_dir, os.path.basename(file_path).replace('.txt', '_prompt.txt'))

    # Write the processed content into a new file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # write kept lines
        output_file.writelines(selected_lines[:-1])
        output_file.write(truncated_line)




def process_files_in_root_directory(root_dir, output_dir, folder_dict):
    for subfolder, (regex_pattern, n_chars_to_keep) in folder_dict.items():
        subfolder_path = os.path.join(root_dir, subfolder)

        if not os.path.exists(subfolder_path):
            print(f"{subfolder} do not exist.")
            continue

        for filename in os.listdir(subfolder_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(subfolder_path, filename)
                process_file(file_path, regex_pattern, n_chars_to_keep, output_dir, subfolder)

if __name__ == '__main__':

    # root_dir/google api key
    root_dir = r''
    output_dir = r''

    process_files_in_root_directory(root_dir, output_dir, secret_dic)

