import logging
import math
import os
import re
import shutil
import time

import requests

# Replace the token here with your GitHub access token
token = ''

screct_dic = {
    'slack_incoming_web_hook_url': r"https:\/\/hooks.slack.com\/services\/[A-Za-z0-9+\/]{44,46}",
    'alibabacloud': r"LTAI[a-zA-Z0-9]{20}",
    'tencent_cloud_secret_id': r"AKID[0-9a-zA-Z]{32}",
    'google_api_key': r"AIza[0-9A-Za-z\-_]{35}",
    'google_oauth_client_id': r"[0-9]{12}-[a-z0-9]{32}\.apps\.googleusercontent\.com",
    'stripe_test': r"sk_test_[0-9a-zA-Z]{24}",
}

# screct_dic = {
#     'aws_access_key_id': r"AKIA[0-9A-Z]{16}",
#     'google_oauth_client_secret': r"GOCSPX-[a-zA-Z0-9]{28}",
#     'midtrans_sandbox_server_key': r"SB-Mid-server-[0-9a-zA-Z_-]{24}",
#     'flutterwave_live_api_secret_key': r"FLWPUBK_TEST-[0-9a-f]{32}-X",
#     'flutterwave_test_api_secret_key': r"FLWSECK_TEST-[0-9a-f]{32}-X",
#     'stripe_live_secret_key': r"sk_live_[0-9a-zA-Z]{24}",
#     'ebay_production_client_id': r"[a-zA-Z0-9_\-]{8}-[a-zA-Z0-9_\-]{8}-PRD-[a-z0-9]{9}-[a-z0-9]{8}",
#     'github_personal_access_token': r"ghp_[0-9a-zA-Z]{36}",
#     'github_oauth_access_token': r"gho_[0-9a-zA-Z]{36}"
# }

true_key_set = set()
false_key_set = set()
error_file_set = set()
new_error_file_set = set()


def copy_file_matches(sourcefile_path, correct_path):
    """
    Copy the file to correct_path.
    """
    folder_path = os.path.dirname(correct_path)
    os.makedirs(folder_path, exist_ok=True)

    try:
        dest_path = correct_path
        # shutil.copy(sourcefile_path, dest_path)
        shutil.move(sourcefile_path, dest_path)
        print(f"Copied '{sourcefile_path}' to '{correct_path}'")

    except Exception as e:
        print(f"Error processing {sourcefile_path}: {e}")




def calculate_shannon_entropy(s):
    char_count = {}
    for char in s:
        char_count[char] = char_count.get(char, 0) + 1
    entropy = 0
    for count in char_count.values():
        probability = count / len(s)
        entropy -= probability * math.log2(probability)
    return entropy


def verify_true_key(key, sourcefile_path, correct_folder):
    headers = {'Authorization': f'token {token}'}
    url = 'https://api.github.com/search/code'
    # If the current key exists in the real key set, move the file directly to the correct folder
    if key in true_key_set:
        print("True key:", key)
        copy_file_matches(sourcefile_path, correct_folder)
        return 1
    elif key in false_key_set:
        return 0
    # For newly encountered keys
    else:
        # if calculate_shannon_entropy(key) <= base_entropy:
        #     false_key_set.add(key)
        #     return 0
        params = {'q': key}
        time.sleep(6)
        logging.info(f"Verifying：{key}\n")
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            result = response.json()
            if result['total_count'] != 0:
                true_key_set.add(key)
                print("True key:", key)
                copy_file_matches(sourcefile_path, correct_folder)
                return 1
            else:
                false_key_set.add(key)
                return 0
        else:
            error_file_set.add(sourcefile_path)
            print("Error:", response.status_code, response.text)
            return 0


def rate_limit_handler():
    headers = {'Authorization': f'token {token}'}
    response = requests.get('https://api.github.com/rate_limit', headers=headers)

    # Print rate limit information
    print(response.json())



def copy_file_if_content_matches(file_path, pattern, root_folder):
    """
    Read the contents of the specified file. If the contents have real secret,
    Copy the file to result_folder.
    """

    # folder_path = os.path.dirname(file_path)
    relative_path = os.path.relpath(file_path, root_folder)
    result_path = os.path.join(correct_folder, relative_path)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        match = re.search(pattern, content)
        if match:
            # logging.info(f"Validating secret in {file_path}:")
            # Check whether it is real secret
            i = verify_true_key(match.group(0), file_path, result_path)
            return i
        else:
            return 0
    except Exception as e:
        print(f"error in {file_path}: {e}")
        return 0


if __name__ == "__main__":

    model = "starcoder2"
    # models = ["stablecode", "codeGen", "deepseek", "codellama", "starcoder"]


    secret = "google_api_key"
    # secret = "stripe_test"
    # secret = "google_oauth_client_id"
    # secret = "tencent_cloud_secret_id"
    # secret = "alibabacloud"
    # secret = "slack_incoming_web_hook_url"

    # secret = 'aws_access_key_id'
    # secret = 'google_oauth_client_secret'
    # secret = 'midtrans_sandbox_server_key'
    # secret = 'flutterwave_live_api_secret_key'
    # secret = 'flutterwave_test_api_secret_key'
    # secret = 'stripe_live_secret_key'
    # secret = 'ebay_production_client_id'
    # secret = 'github_personal_access_token'
    # secret = 'github_oauth_access_token'

    # false_key_set.add("AKIAIOSFODNN7EXAMPLE")


    # type = "HCR"
    # type = "beam5"
    type = "DESEC"

    # Results of all keys in a single model, you can modify it yourself
    folder = f"{model}/{type}"
    # Results of one key in a single model, such as google_api_key, you can modify it yourself
    root_folder = f"{folder}/{secret}_{model}_{type}"

    correct_folder = f"{folder}/correct_{secret}"

    os.makedirs(correct_folder, exist_ok=True)
    logging.basicConfig(filename=f"{correct_folder}/githubsearch_infotest.log",
                        level=logging.INFO, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

    pattern = screct_dic[secret]

    # files record the verified secrets to avoid repeated queries
    true_key_file = f""
    false_key_file = f""
    error_file = f""

    i = 0

    if os.path.exists(true_key_file):
        with open(true_key_file, 'r', encoding='utf-8') as f1:
            for line in f1:
                true_key_set.add(line.strip())

    if os.path.exists(false_key_file):
        with open(false_key_file, 'r', encoding='utf-8') as f2:
            for line in f2:
                false_key_set.add(line.strip())

    # verify
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                try:
                    i = i + copy_file_if_content_matches(file_path, pattern, correct_folder, root_folder)
                except Exception as e:
                    continue

    # Record the verified secrets to avoid repeated queries
    with open(true_key_file, 'w', encoding='utf-8')as f4:
        for true_key in true_key_set:
            f4.write(true_key + "\n")
    with open(false_key_file, 'w', encoding='utf-8')as f5:
        for false_key in false_key_set:
            f5.write(false_key + "\n")

    with open(error_file, 'w', encoding='utf-8')as f6:
        for error_file_item in error_file_set:
            f6.write(error_file_item + "\n")
    print(f"Number of real secret files:{i}")

    # rate_limit_handler()

