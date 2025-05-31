**Programmers' Visual Attention on Function Call Graphs During Code Summarization**

This repository includes the data and code necessary to replicate the work in the paper _Programmers' Visual Attention on Function Call Graphs During Code Summarization_.

**Study Procedure**

Our study follows the procedure outlined by [Wallace et al.](https://ieeexplore.ieee.org/abstract/document/10938844?casa_token=JCsNnZD8oMkAAAAA:0TxPe6HbhkV6x-GSBmOzGBMhHK0Yq-fI7dyUadcy93J99qdCKT4XFE1RiSgLlYxo0rdyBz5G7w>), and can be replicated with the same steps outlined [here](https://github.com/aakashba/EyeContext-TSE).

The Java projects used in the summarization tasks can be located here: https://drive.google.com/file/d/1-klGiDbqCbIgnEwpwnu0-rT1z-9LOmcK/view?usp=share_link. A list of summarized methods used in analysis can be found in ``constants.py``. The study instructions can be found in ``StudyInstructions.md``.


**Pre-Processing**

First, raw data was processed into fixation data using the [iTrace Toolkit](https://ieeexplore.ieee.org/document/10172570), and converted from database format to csv format with **``process_db3.py``**. The fixation data is located in the **``PreProcessedData_CallGraphVisualAttention``** folder, with subfolders corresponding to each participant. This folder includes both data from our study (Study 2, participant numbers above 20) and from the study done by Wallace et al (Study 1, participant numbers below 20). Raw data is too large to include, but may be obtained on request by emailing the authors.


The **``PreProcessedData_CallGraphVisualAttention``** folder also has a folder ``call_graphs`` which includes the .txt files with call graphs for all methods summarized in the study, generated using IntelliJ’s "Call Hierarchy" tool. The folder also includes files with participant summaries and reviewer ratings (``study1_summaries.csv`` and ``study2_summaries.csv``).

In **``constants.py``**, set ``DATA_DIR`` to the location of the ``PreProcessedData_CallGraphVisualAttention`` folder, and ``PROJECTS_DIR`` to the location of the folder with the Java projects used in the summarization tasks.


**Analysis Steps**

To replicate the analysis, run the following:

1. **``step_1_data_processing.py``** - This file combines summary and confidence ratings with fixation data and saves the resulting data to a folder called ``Processed Data``.

2. **``step_2_annotate_methods.py``** - This file annotates each fixation with the name of the method that is being fixated on (or no method, if the fixation occurs outside the bounds of a method).
  
3. **``step_3_generate_metrics.py``** - This file calculates relevant metrics for each trial and saves the resulting data to the ``output`` folder using helper methods from ``coverage_metrics.py`` and ``call_graph_builder.py``. The metrics calculated are: node coverage, weighted node coverage, edge coverage, weighted edge coverage, average fixation duration, number of fixations, and max depth.
   
4. **``step_4_analysis.py``** - This file performs the analysis of these metrics across both studies individually as well as the combined dataset. Specifically it:
   * Calculates the average proportion of methods in each project that are in the call graph of each summarized method
   * Calculates the average fixation position of each code category (e.g. callee graph method, non-call graph method, etc.)
   * Calculates the proportion of time spent fixating on each code category
   * Calculates statistics describing mean and average depth
   * Prepares data for regression analysis and saves the results as csv files
   
5. **``step_5_regression.Rmd``** - Mixed effect regression analyses are performed using R. This file reports results for all the mixed effect regression analyses related call graph coverage metrics (node coverage, weighted node coverage, edge coverage, and weighted edge coverage) to dependent variables (summary scores, confidence, absolute confidence difference).
