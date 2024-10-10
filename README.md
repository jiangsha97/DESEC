This repository contains a preliminary version of this paper. We propose DESEC, a two-stage method that leverages token-level features derived fromthe identified characteristics to guide the decoding process.
## Structure
|         **Folder**         |                        **Description**                        |
|:--------------------------:|:-------------------------------------------------------:|
|            Data            |             Feature data used for training LDA models                |
|       Decoding       |        Guide Code LLM decoding       |
|         Evaluation          | Evaluate the secrets  |
|         imgs          | Supplementary scatter plot supporting the conclusion of Section III. C  |
|         LDA_Models          | Trained LDA model  |
|         ScoringModelConstruction          | Script for training LDA model  |
## Usage
1. Collect prompt files for experiments using the method described in the paper and store them in a folder.
2. For the LDA model that guides the decoding process, you can directly use the models in `LDA_madels`, which are trained from feature data in `Data`.
You can also collect data on your own according to the methods in the paper, and use `LDA_Model_Training.py` in `ScoringModelConstruction` to train LDA models.
3. With the prompts and LDA scoring model in place, you can use `DESEC_TestWithCodeLLM.py` in `Decoding`.
Fill in the locations of your Code LLM, prompt dataset, and model output text, and then perform DESEC decoding under the guidance of the scoring model.
4. Due to user privacy concerns, we only provide `Plausible_Secrets.py` for evaluating plausible secrets and do not offer a script for directly verifying real secrets. 
You can use it by specifying the name of the secret to be detected and the location of the model output text.
## Ethics
Following the current code of ethics of ACM and IEEE, to respect privacy, we only provide the feature data used for training the LDA model, 
which does not involve actual secret text. For the same reason, the prompt dataset used in the experiments has also not been provided.
