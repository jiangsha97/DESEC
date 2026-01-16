import pandas as pd
import requests
from urllib.parse import urlparse
from pathlib import Path
from collections import defaultdict
import os




def download(csv_file_path, save_path):
    df = pd.read_csv(csv_file_path)

    # Check that all URLs are in the 'File URL' column
    urls = df['File URL'].tolist()

    # Used to track file names and their frequency of occurrence
    filename_counts = defaultdict(int)

    root_directory = save_path

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()

            path = urlparse(url).path
            basename = Path(path).name

            subdir = root_directory

            os.makedirs(subdir, exist_ok=True)

            # If the file name already exists, add a number
            if filename_counts[(subdir, basename)] > 0:
                name, ext = basename.rsplit('.', 1)
                filename = f"{name}-{filename_counts[(subdir, basename)]}.{ext}"
            else:
                filename = basename

            filename_counts[(subdir, basename)] += 1

            full_path = os.path.join(subdir, filename)

            with open(full_path, 'wb') as file:
                file.write(response.content)

            print(f'File {filename} saved in {subdir}.')

        except Exception as e:
            print(f"Error in {url}: {e}")
            with open(error_file, 'a') as file:
                file.write(url + '\n')
            continue

    print("Complete file processing for one language")


if __name__ == "__main__":

    # You need to replace the "/-/blob/" column in the File URL column of the exported CSV file with "/-/raw/" first,
    # otherwise it cannot be downloaded (you can directly replace it globally)

    # result code folder
    result_root = ""
    # csv file
    search_root = ""

    for root, dirs, files in os.walk(search_root):
        if root != search_root:
            print(f"processing: {root}")

            # The root_dic contains exported CSV files (which can be multiple). Download the code contained in all CSV files in this directory
            root_dic = root
            subfolder_name = os.path.basename(root_dic)
            # Save_root is the root directory where code is saved,
            # and subdirectories are created based on the CSV file name in the root directory.
            # Each subdirectories stores the code contained in the CSV file
            save_root = f"{result_root}/{subfolder_name}"

            error_file = f"{root_dic}/error_urls.log"

            files = os.listdir(root_dic)

            csv_files = [file for file in files if file.endswith('.csv')]


            for csv_file in csv_files:
                csv_file_path = os.path.join(root_dic, csv_file)
                # Retrieve the CSV file name as the sub directory name for save_root
                csv_name = os.path.splitext(csv_file)[0]

                # Create save path: root directory/csv file name.
                # This folder will store all code files contained in the csv file
                save_path = f"{save_root}/{csv_name}/"
                download(csv_file_path, save_path)

    print("finished")
