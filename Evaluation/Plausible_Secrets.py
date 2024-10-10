import os
import re
import math
import statistics

# 'secret name': [Format, Fixed prefix length(0 if not available), Fixed suffix index (None if not available)]
screct_dic = {
    'slack_incoming_web_hook_url': [r"https:\/\/hooks.slack.com\/services\/[A-Za-z0-9+\/]{44,46}", 33, None],
    'alibabacloud': [r"LTAI[a-zA-Z0-9]{20}", 4, None],
    'tencent_cloud_secret_id': [r"AKID[0-9a-zA-Z]{32}", 4, None],
    'google_api_key': [r"AIza[0-9A-Za-z\-_]{35}", 4, None],
    'google_oauth_client_id': [r"[0-9]{12}-[a-z0-9]{32}\.apps\.googleusercontent\.com", 0, -27],
    'stripe_test': [r"sk_test_[0-9a-zA-Z]{24}", 8, None]
}

MIN_WORD_LENGTH = 4

def extract_and_trim_first_match_from_files(root_folder_path, pattern, index1, index2):
    matches = []
    regex = re.compile(pattern)

    for root, dirs, files in os.walk(root_folder_path):
        for filename in files:
            if filename.endswith(".txt"):
                file_path = os.path.join(root, filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    for line in file:
                        match = regex.search(line)
                        if match:
                            # Remove fixed prefixes/suffixes
                            trimmed_match = match.group()[index1:index2]
                            matches.append(trimmed_match)
                            # Extract only the first matching item and exit the loop
                            break
    return matches


def calculate_mean_and_std(float_list):
    mean = statistics.mean(float_list)
    std = statistics.stdev(float_list)
    return mean, std


def shannon_entropy(string):
    freq_dict = {}
    for char in string:
        if char in freq_dict:
            freq_dict[char] += 1
        else:
            freq_dict[char] = 1
    entropy = 0.0
    str_len = len(string)
    for freq in freq_dict.values():
        prob = freq / str_len
        entropy -= prob * math.log2(prob)

    return entropy


def filter_characters(string):
    return string.lower()

# Search for predefined common words
class WordsFinder(object):

    def __init__(self, wordlists):
        self.dictionary = None
        self.max_length = 0
        if wordlists:
            self.dictionary = set()
            for txt in wordlists:
                for line in open(txt, "r"):
                    word = filter_characters(line).lower().rstrip('\n')
                    if len(word) > self.max_length:
                        self.max_length = len(word)
                    self.dictionary.add(word)

    def get_words_indexes(self, string):
        string = filter_characters(string)
        if len(string) < MIN_WORD_LENGTH:
            return
        if not self.dictionary:
            print("Dictionary uninitalized!")
            return
        i = 0
        while i < len(string) - (MIN_WORD_LENGTH - 1):
            chunk = string[i:i + self.max_length]
            found = False
            for j in range(len(chunk), MIN_WORD_LENGTH - 1, -1):
                candidate = chunk[:j]
                if candidate in self.dictionary:
                    yield (i, j, candidate)
                    found = True
                    i += j
                    break
            if not found:
                i += 1

    def count_word_length(self, string):
        word_length_count = 0
        for i in self.get_words_indexes(string):
            word_length_count += i[1]
        return word_length_count

# Search for predefined common words
class StringsFilter(object):

    def __init__(self):
        wordlists = []
        for path in ['computer_wordlist.txt']:
            wordlists.append(os.path.join('.', path))
        self.finder = WordsFinder(wordlists)

    def word_filter(self, string):
        return self.finder.count_word_length(string)


# Given the key, perform six blacklist mode checks on it
def pattern_filter(input_string):
    # four consecutive identical characters
    for i in range(len(input_string) - 3):
        if input_string[i] == input_string[i + 1] == input_string[i + 2] == input_string[i + 3]:
            return True
    # Four continuously increasing characters
    for i in range(len(input_string) - 3):
        if input_string[i:i+4] in [''.join(map(chr, range(ord(input_string[i]), ord(input_string[i])+4))),
                                   ''.join(map(chr, range(ord(input_string[i].lower()), ord(input_string[i].lower())+4)))]:
            return True
    # Four consecutive decreasing characters
    for i in range(len(input_string) - 3):
        if input_string[i:i+4] in [''.join(map(chr, range(ord(input_string[i]), ord(input_string[i])-4, -1))),
                                   ''.join(map(chr, range(ord(input_string[i].lower()), ord(input_string[i].lower())-4, -1)))]:
            return True
    # Alternating and repetitive patterns, such as 'babab'
    for i in range(len(input_string) - 5):
        if input_string[i] == input_string[i + 2] == input_string[i + 4] and input_string[i + 1] == input_string[i + 3] == input_string[i + 5]:
            return True
    # Three consecutive identical three character substrings
    for i in range(len(input_string) - 8):
        if input_string[i:i+3] == input_string[i+3:i+6] == input_string[i+6:i+9]:
            return True
    # Two consecutive identical four character character strings
    for i in range(len(input_string) - 7):
        if input_string[i:i+4] == input_string[i+4:i+8]:
            return True

    return False





if __name__ == '__main__':

    # Set the name of secret to be detected
    secret = "google_api_key"
    # Results Folder
    root_path = f"Your_Results_Folder"

    pattern = screct_dic[secret][0]
    index1 = screct_dic[secret][1]
    index2 = screct_dic[secret][2]

    result_path = f"{root_path}/Plausible_Secrets.log"
    wrong_path = f"{root_path}/Other_Secrets.log"

    correct_count = 0
    correct_keys = []
    wrong_keys = []

    keys = extract_and_trim_first_match_from_files(root_path, pattern, index1, index2)

    length = len(keys)
    # Rating list, the ones with full marks are Plausible Secrets
    score_list = [0] * length

    shannon_entropies = []
    s_filter = StringsFilter()

    for key in keys:
        shannon_entropies.append(shannon_entropy(key))

    # Calculate the threshold for entropy of Plausible Secret
    mean, std = calculate_mean_and_std(shannon_entropies)
    threshold = mean - 3 * std

    # Calculate entropy score
    for i, (score, entropy) in enumerate(zip(score_list, shannon_entropies)):
        if entropy > threshold:
            score_list[i] += 1
    print(score_list)

    # Calculate pattern score
    for j, (score, key) in enumerate(zip(score_list, keys)):
        if not pattern_filter(key):
            score_list[j] += 1
    print(score_list)

    # Calculate the score of commonly used words
    for k, (score, key) in enumerate(zip(score_list, keys)):
        if s_filter.word_filter(key) < MIN_WORD_LENGTH:
            score_list[k] += 1
    print(score_list)

    # Plausible Secret score calculation
    for score, key in zip(score_list, keys):
        if score == 3:
            correct_count += 1
            correct_keys.append(key)
        else:
            wrong_keys.append(key)
    print("Plausible Secrets: ", correct_count)

    # Record Plausible Secrets
    with open(result_path, 'w', encoding='utf-8') as f1:
        for correct_key in correct_keys:
            f1.write(correct_key + "\n")
    # Record other secrets
    with open(wrong_path, 'w', encoding='utf-8') as f2:
        for wrong_key in wrong_keys:
            f2.write(wrong_key + "\n")


