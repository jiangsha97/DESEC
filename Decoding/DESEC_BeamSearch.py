import math

import torch

from Scoring_With_lDA_Model import check_entropy_average_all, entropy_by_token, avg_by_token, calculate_entropy_percent

epsilon = 1e-10


# Score the token
def token_score(probabilities, de_tokens, prob1, prob2, step, lda_model):
    score = check_entropy_average_all(de_tokens, probabilities, prob1, prob2, step, lda_model)
    return score


def predict_next_token(input_ids, model):
    with torch.no_grad():
        outputs = model(input_ids=input_ids)
        predictions = outputs.logits[:, -1, :]
        probs = torch.softmax(predictions, dim=-1)
    return probs


def beam_search(input_text, model, tokenizer, pattern, lda_model, num_beams=3, max_length=35, num_candidates=10, max_text_length=35):
    input_ids = tokenizer.encode(input_text, return_tensors='pt').to('cuda')
    # beams: (input_ids, score, token_seqs, prob_seqs, current_string, entropy_percent, de_tokens, entropies, prob_avgs, prob_distance, self_score)
    # de_tokens is the decoded text token sequence.
    beams = [(input_ids, 0, [], [], "", [], [], [], [], [], 0)]
    finished_beams = []

    for step in range(max_length):
        new_beams = []
        for input_ids, score, token_seqs, prob_seqs, current_string, entropy_percent, de_tokens, entropies, prob_avgs, prob_distance, self_score in beams:
            # If the current beam has already ended, it will be added directly to new-beams without further expansion
            if input_ids[0][-1].item() == tokenizer.eos_token_id:
                finished_beams.append((input_ids, score, token_seqs, prob_seqs, current_string, entropy_percent, de_tokens, entropies, prob_avgs, prob_distance, self_score))
                continue
            # If the current beam has reached its maximum text length, it will be added directly to new-beams without further expansion
            elif len(''.join(current_string)) >= max_text_length:
                finished_beams.append((input_ids, score, token_seqs, prob_seqs, current_string, entropy_percent, de_tokens, entropies, prob_avgs, prob_distance, self_score))
                continue

            probs = predict_next_token(input_ids, model)
            # Consider num_candidates as candidates to replace tokens that do not match the pattern
            top_probs, top_idx = probs.topk(num_candidates + 1)

            added_beams = 0

            for j in range(num_candidates):
                if added_beams >= num_beams:
                    # Sufficient beams have been added
                    break

                next_token_id = top_idx[0][j].unsqueeze(0)
                # Decoding this candidate token
                token = tokenizer.decode(next_token_id)
                # Discard tokens that do not match the pattern
                if not pattern.match(token):
                    continue
                # Obtain the current token probability
                prob1 = top_probs[0][j].item()
                # The next token in the probability distributio
                prob2 = top_probs[0][j + 1].item()


                new_input_ids = torch.cat([input_ids, next_token_id.unsqueeze(0).to(input_ids.device)], dim=-1)
                new_score = score + math.log(prob1 + epsilon)
                new_token_seqs = token_seqs + [next_token_id]
                new_prob_seqs = prob_seqs + [prob1]
                new_string = current_string + token
                new_de_tokens = de_tokens + [token]
                # Entropy after adding this token
                new_entropies = entropy_by_token(new_de_tokens)
                # The Average Probability after adding this token
                new_prob_avgs = avg_by_token(new_prob_seqs)
                # The Entropy Ratio after adding this token
                new_entropy_percent = calculate_entropy_percent(new_entropies)
                # Probability Advantage
                new_prob_distance = prob_distance + [prob1 - prob2]
                # Scoring
                if step <= 3:
                    new_self_score = self_score + math.log(prob1 + epsilon) * 0.75
                else:
                    new_self_score = self_score + math.log(prob1 + epsilon) * 0.75 + token_score(new_prob_seqs, new_de_tokens, prob1, prob2, step, lda_model)

                # Check the length of the generated text
                if len(''.join(current_string)) <= max_text_length:
                    new_beams.append((new_input_ids, new_score, new_token_seqs, new_prob_seqs, new_string, new_entropy_percent, new_de_tokens, new_entropies, new_prob_avgs, new_prob_distance, new_self_score))
                    added_beams += 1

        # Retain the highest scoring num_ceams beams
        new_beams.sort(key=lambda x: x[-1], reverse=True)

        if step > 3:
            beams = new_beams[:num_beams]
        else:
            beams = new_beams[:]

        if len(finished_beams) >= num_beams:
            break


    # Select the sequence with the highest score from the completed beams (normalized)
    if finished_beams:
        best_beam = max(finished_beams, key=lambda x: x[-1]/(len(x[2]) ** 0.7))
    else:
        best_beam = beams[0]

    # return: (input_ids, score, token_seqs, prob_seqs, current_string, entropy_percent, de_tokens, entropies, prob_avgs,
    #   prob_distance, self_score, de_tokens)
    return best_beam[3], best_beam[7], best_beam[8], best_beam[5], ''.join(best_beam[4]), best_beam[9], best_beam[-1], best_beam[6]