import math
import numpy as np

epsilon = 1e-10

# Calculate the probability that the token belongs to category 0
def calculate_probability(x, lda_model):
    probabilities = lda_model.predict_proba(x)
    prob_class_0 = probabilities[0][0]
    return prob_class_0


def calculate_shannon_entropy(s):
    char_count = {}
    for char in s:
        char_count[char] = char_count.get(char, 0) + 1
    entropy = 0
    for count in char_count.values():
        probability = count / len(s)
        entropy -= probability * math.log2(probability)
    return entropy


# Calculate entropy based on tokens, take the average of multi character tokens
def entropy_by_token(tokens):
    step_entropies = []
    current_string = ""

    for token in tokens:
        # If the token is multi character, calculate the average Shannon entropy corresponding to each character
        if len(token) > 1:
            s_entropy = 0
            for char in token:
                current_string = current_string + char
                s_entropy = s_entropy + calculate_shannon_entropy(current_string)
            average_entropy = s_entropy / len(token)
            step_entropies.append(average_entropy)
        else:
            current_string += token
            step_entropies.append(calculate_shannon_entropy(current_string))
    return step_entropies


def calculate_entropy_percent(entropies):
    percents = []
    last_entropy = None
    for entropy in entropies:
        # entropy ratio
        if last_entropy is not None and last_entropy != 0:
            percents.append(entropy / last_entropy)
        else:
            # The entropy ratio of the first token is 1
            percents.append(1)
        last_entropy = entropy
    return percents


#  Calculate the Average Probability of each token
def avg_by_token(probabilities):
    step_averages = [np.mean(probabilities[:i + 1]) for i in range(len(probabilities))]
    return step_averages

# Scoring
def check_entropy_prob(en_checks, avg_checks, index, prob_distance, lda_model):
    # features: index、prob_avg、entropy_percent、prob_distance
    new_sample = [index, avg_checks[-1], en_checks[-1], prob_distance]
    new_sample_array = np.array([new_sample])
    score = calculate_probability(new_sample_array, lda_model)

    return math.log(score + epsilon)


# Overall Scoring
def check_entropy_average_all(tokens, probabilities, prob1, prob2, index, lda_model):
    # Calculate the Average Probability of each token
    step_prob_avgs = avg_by_token(probabilities)
    prob_avg_checks = step_prob_avgs

    # Calculate entropy for the current token
    step_entropies = entropy_by_token(tokens)

    # Request for the Entropy Ratio of the newly added token
    en_percents = calculate_entropy_percent(step_entropies)
    en_checks = en_percents

    # Scoring
    score = check_entropy_prob(en_checks, prob_avg_checks, index, prob1 - prob2, lda_model)

    return score

