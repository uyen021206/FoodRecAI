SVM MODEL EXPERIMENTATION & EVALUATION GUIDE

1. Hyperparameter Tuning and Results (Validation Accuracy)
The hyperparameter tuning process for parameter C was conducted manually on the Validation dataset to discover the optimal configuration:
- Experiment with C = 5.0 (--version C5.0) -> Accuracy: 73.49%
- Experiment with C = 1.0 (--version C1.0) -> Accuracy: 74.23%
- Experiment with C = 0.01 (--version C0.01) -> Accuracy: 73.96%
- Experiment with C = 0.1 (--version C0.1) -> Accuracy: 74.69% (Best Performance)

Conclusion: Parameter C = 0.1 yields the highest accuracy on the Validation set. Thus, it is selected as the optimal configuration for the final model deployment (svm_pipeline_C0.1.pkl).

2. Execution Commands

Step 1: Train the Optimal Model (Train and Re-train)
Run the following command to execute the training process with the optimal parameter C=0.1. The system will automatically combine the Train and Validation sets for a final re-training phase before exporting the .pkl model file into the outputs/ directory:

python train.py --c 0.1 --version C0.1

Step 2: Final Evaluation on the Test Set
Once the model file is generated from Step 1, run the following command to evaluate its performance independently on the Test set and export all visual results into the result/ directory:

python evaluate.py --model-name svm_pipeline_C0.1.pkl

Outputs generated in the result/ directory:
- svm_evaluation_report.txt: A detailed report containing performance metrics (Precision, Recall, F1-score).
- matrix_svm_pipeline_C0.1.png: The confusion matrix plot using a clean, professional blue color palette, containing only raw data counts as requested.