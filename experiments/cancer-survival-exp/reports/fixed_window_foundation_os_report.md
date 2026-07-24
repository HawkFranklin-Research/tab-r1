# Fixed-Window OS Event Foundation-Model Experiment

- Output root: `/home/prime/Documents/g3/cancer-survival-exp/outputs/fixed_window_foundation_top100`
- Dataset source: `/home/prime/Documents/g3/cancer-survival-exp/datasets_fixed_window_top100`
- Endpoints: 3-year and 5-year observed OS event classification.
- Positive class: death observed on or before the fixed horizon.
- Negative class: no observed death before the fixed horizon.
- Excluded: patients censored before the horizon, because their fixed-window label is unknown.
- Features: top 100 non-clinical high-variance molecular features per cancer dataset.
- Compared models: TabPFN v1, v2, v2.5, v2.6, v3, and TabFM 1.0.0 default.
- TabFM ensemble is intentionally excluded.

## Exported Label Sets

| name                           | endpoint   |   horizon_days |   samples | class_counts         |   excluded_ambiguous |
|:-------------------------------|:-----------|---------------:|----------:|:---------------------|---------------------:|
| BRCA_core_os_3yr_event_top100  | os_3yr     |           1095 |       501 | {'0': 430, '1': 71}  |                  679 |
| BRCA_core_os_5yr_event_top100  | os_5yr     |           1825 |       350 | {'0': 249, '1': 101} |                  830 |
| ESCA_core_os_3yr_event_top100  | os_3yr     |           1095 |        86 | {'1': 68, '0': 18}   |                   96 |
| ESCA_core_os_5yr_event_top100  | os_5yr     |           1825 |        79 | {'1': 75, '0': 4}    |                  103 |
| HNSCC_core_os_3yr_event_top100 | os_3yr     |           1095 |       385 | {'1': 210, '0': 175} |                  239 |
| HNSCC_core_os_5yr_event_top100 | os_5yr     |           1825 |       286 | {'1': 232, '0': 54}  |                  338 |
| LSCC_core_os_3yr_event_top100  | os_3yr     |           1095 |       355 | {'0': 185, '1': 170} |                  220 |
| LSCC_core_os_5yr_event_top100  | os_5yr     |           1825 |       281 | {'1': 199, '0': 82}  |                  294 |
| LUAD_core_os_3yr_event_top100  | os_3yr     |           1095 |       318 | {'0': 161, '1': 157} |                  292 |
| LUAD_core_os_5yr_event_top100  | os_5yr     |           1825 |       251 | {'1': 194, '0': 57}  |                  359 |

## Mean Metrics By Model

| model_name    |   accuracy |       f1 |   roc_auc |   pr_auc |   sensitivity_event |   log_loss |
|:--------------|-----------:|---------:|----------:|---------:|--------------------:|-----------:|
| tabfm_default |   0.705953 | 0.6446   |  0.530123 |      nan |                 nan |   0.57876  |
| tabpfn_v2     |   0.695885 | 0.556195 |  0.478016 |      nan |                 nan |   0.555733 |
| tabpfn_v2_5   |   0.701313 | 0.571394 |  0.49094  |      nan |                 nan |   0.557447 |
| tabpfn_v2_6   |   0.699032 | 0.62786  |  0.544317 |      nan |                 nan |   0.556437 |
| tabpfn_v3     |   0.701818 | 0.598123 |  0.560498 |      nan |                 nan |   0.55017  |

## Mean Metrics By Horizon And Model

| task_family   | model_name    |   accuracy |       f1 |   roc_auc |   pr_auc |   sensitivity_event |   log_loss |
|:--------------|:--------------|-----------:|---------:|----------:|---------:|--------------------:|-----------:|
| os_3yr        | tabfm_default |   0.627323 | 0.538526 |  0.511112 |      nan |                 nan |   0.656472 |
| os_3yr        | tabpfn_v2     |   0.610084 | 0.404081 |  0.474439 |      nan |                 nan |   0.610458 |
| os_3yr        | tabpfn_v2_5   |   0.62094  | 0.434479 |  0.453824 |      nan |                 nan |   0.614804 |
| os_3yr        | tabpfn_v2_6   |   0.626557 | 0.532509 |  0.500663 |      nan |                 nan |   0.610436 |
| os_3yr        | tabpfn_v3     |   0.618175 | 0.462937 |  0.500013 |      nan |                 nan |   0.605885 |
| os_5yr        | tabfm_default |   0.784583 | 0.750675 |  0.549133 |      nan |                 nan |   0.501048 |
| os_5yr        | tabpfn_v2     |   0.781687 | 0.708309 |  0.481594 |      nan |                 nan |   0.501008 |
| os_5yr        | tabpfn_v2_5   |   0.781687 | 0.708309 |  0.528055 |      nan |                 nan |   0.500089 |
| os_5yr        | tabpfn_v2_6   |   0.771507 | 0.723212 |  0.587971 |      nan |                 nan |   0.502438 |
| os_5yr        | tabpfn_v3     |   0.78546  | 0.733309 |  0.620984 |      nan |                 nan |   0.494455 |

## Dataset-Level Metrics

| dataset                        | model_name    | version     | task_type   | status   |   error_type |   error_message |   accuracy |        f1 |   roc_auc |   log_loss | task_family   |   pr_auc |   sensitivity_event |
|:-------------------------------|:--------------|:------------|:------------|:---------|-------------:|----------------:|-----------:|----------:|----------:|-----------:|:--------------|---------:|--------------------:|
| BRCA_core_os_3yr_event_top100  | tabpfn_v2     | v2          | binary      | success  |          nan |             nan |   0.855263 | 0         | 0.721678  |   0.383518 | os_3yr        |      nan |                 nan |
| BRCA_core_os_3yr_event_top100  | tabpfn_v2_5   | v2_5        | binary      | success  |          nan |             nan |   0.855263 | 0         | 0.641958  |   0.388543 | os_3yr        |      nan |                 nan |
| BRCA_core_os_3yr_event_top100  | tabpfn_v2_6   | v2_6        | binary      | success  |          nan |             nan |   0.868421 | 0.166667  | 0.641958  |   0.369431 | os_3yr        |      nan |                 nan |
| BRCA_core_os_3yr_event_top100  | tabpfn_v3     | v3          | binary      | success  |          nan |             nan |   0.868421 | 0.166667  | 0.566434  |   0.387592 | os_3yr        |      nan |                 nan |
| BRCA_core_os_5yr_event_top100  | tabpfn_v2     | v2          | binary      | success  |          nan |             nan |   0.716981 | 0         | 0.603509  |   0.580502 | os_5yr        |      nan |                 nan |
| BRCA_core_os_5yr_event_top100  | tabpfn_v2_5   | v2_5        | binary      | success  |          nan |             nan |   0.716981 | 0         | 0.594737  |   0.576307 | os_5yr        |      nan |                 nan |
| BRCA_core_os_5yr_event_top100  | tabpfn_v2_6   | v2_6        | binary      | success  |          nan |             nan |   0.735849 | 0.125     | 0.546491  |   0.58289  | os_5yr        |      nan |                 nan |
| BRCA_core_os_5yr_event_top100  | tabpfn_v3     | v3          | binary      | success  |          nan |             nan |   0.735849 | 0.125     | 0.584211  |   0.571856 | os_5yr        |      nan |                 nan |
| ESCA_core_os_3yr_event_top100  | tabpfn_v2     | v2          | binary      | success  |          nan |             nan |   0.769231 | 0.869565  | 0.233333  |   0.559645 | os_3yr        |      nan |                 nan |
| ESCA_core_os_3yr_event_top100  | tabpfn_v2_5   | v2_5        | binary      | success  |          nan |             nan |   0.769231 | 0.869565  | 0.233333  |   0.57359  | os_3yr        |      nan |                 nan |
| ESCA_core_os_3yr_event_top100  | tabpfn_v2_6   | v2_6        | binary      | success  |          nan |             nan |   0.769231 | 0.869565  | 0.4       |   0.578118 | os_3yr        |      nan |                 nan |
| ESCA_core_os_3yr_event_top100  | tabpfn_v3     | v3          | binary      | success  |          nan |             nan |   0.769231 | 0.869565  | 0.533333  |   0.550704 | os_3yr        |      nan |                 nan |
| ESCA_core_os_5yr_event_top100  | tabpfn_v2     | v2          | binary      | success  |          nan |             nan |   0.916667 | 0.956522  | 0.0909091 |   0.318674 | os_5yr        |      nan |                 nan |
| ESCA_core_os_5yr_event_top100  | tabpfn_v2_5   | v2_5        | binary      | success  |          nan |             nan |   0.916667 | 0.956522  | 0.363636  |   0.307414 | os_5yr        |      nan |                 nan |
| ESCA_core_os_5yr_event_top100  | tabpfn_v2_6   | v2_6        | binary      | success  |          nan |             nan |   0.916667 | 0.956522  | 0.727273  |   0.287891 | os_5yr        |      nan |                 nan |
| ESCA_core_os_5yr_event_top100  | tabpfn_v3     | v3          | binary      | success  |          nan |             nan |   0.916667 | 0.956522  | 0.727273  |   0.293619 | os_5yr        |      nan |                 nan |
| HNSCC_core_os_3yr_event_top100 | tabpfn_v2     | v2          | binary      | success  |          nan |             nan |   0.5      | 0.658824  | 0.460337  |   0.706664 | os_3yr        |      nan |                 nan |
| HNSCC_core_os_3yr_event_top100 | tabpfn_v2_5   | v2_5        | binary      | success  |          nan |             nan |   0.517241 | 0.65      | 0.451322  |   0.707082 | os_3yr        |      nan |                 nan |
| HNSCC_core_os_3yr_event_top100 | tabpfn_v2_6   | v2_6        | binary      | success  |          nan |             nan |   0.534483 | 0.658228  | 0.526442  |   0.689932 | os_3yr        |      nan |                 nan |
| HNSCC_core_os_3yr_event_top100 | tabpfn_v3     | v3          | binary      | success  |          nan |             nan |   0.568966 | 0.698795  | 0.463942  |   0.693624 | os_3yr        |      nan |                 nan |
| HNSCC_core_os_5yr_event_top100 | tabpfn_v2     | v2          | binary      | success  |          nan |             nan |   0.813953 | 0.897436  | 0.685714  |   0.452656 | os_5yr        |      nan |                 nan |
| HNSCC_core_os_5yr_event_top100 | tabpfn_v2_5   | v2_5        | binary      | success  |          nan |             nan |   0.813953 | 0.897436  | 0.628571  |   0.465304 | os_5yr        |      nan |                 nan |
| HNSCC_core_os_5yr_event_top100 | tabpfn_v2_6   | v2_6        | binary      | success  |          nan |             nan |   0.813953 | 0.897436  | 0.65      |   0.451788 | os_5yr        |      nan |                 nan |
| HNSCC_core_os_5yr_event_top100 | tabpfn_v3     | v3          | binary      | success  |          nan |             nan |   0.813953 | 0.897436  | 0.625     |   0.460922 | os_5yr        |      nan |                 nan |
| LSCC_core_os_3yr_event_top100  | tabpfn_v2     | v2          | binary      | success  |          nan |             nan |   0.425926 | 0.415094  | 0.446429  |   0.710447 | os_3yr        |      nan |                 nan |
| LSCC_core_os_3yr_event_top100  | tabpfn_v2_5   | v2_5        | binary      | success  |          nan |             nan |   0.462963 | 0.45283   | 0.471154  |   0.711333 | os_3yr        |      nan |                 nan |
| LSCC_core_os_3yr_event_top100  | tabpfn_v2_6   | v2_6        | binary      | success  |          nan |             nan |   0.481481 | 0.5       | 0.467033  |   0.71404  | os_3yr        |      nan |                 nan |
| LSCC_core_os_3yr_event_top100  | tabpfn_v3     | v3          | binary      | success  |          nan |             nan |   0.425926 | 0.392157  | 0.478022  |   0.703985 | os_3yr        |      nan |                 nan |
| LSCC_core_os_5yr_event_top100  | tabpfn_v2     | v2          | binary      | success  |          nan |             nan |   0.697674 | 0.821918  | 0.598718  |   0.595582 | os_5yr        |      nan |                 nan |
| LSCC_core_os_5yr_event_top100  | tabpfn_v2_5   | v2_5        | binary      | success  |          nan |             nan |   0.697674 | 0.821918  | 0.585897  |   0.595969 | os_5yr        |      nan |                 nan |
| LSCC_core_os_5yr_event_top100  | tabpfn_v2_6   | v2_6        | binary      | success  |          nan |             nan |   0.627907 | 0.771429  | 0.533333  |   0.618031 | os_5yr        |      nan |                 nan |
| LSCC_core_os_5yr_event_top100  | tabpfn_v3     | v3          | binary      | success  |          nan |             nan |   0.697674 | 0.821918  | 0.628205  |   0.593803 | os_5yr        |      nan |                 nan |
| LUAD_core_os_3yr_event_top100  | tabpfn_v2     | v2          | binary      | success  |          nan |             nan |   0.5      | 0.0769231 | 0.510417  |   0.692015 | os_3yr        |      nan |                 nan |
| LUAD_core_os_3yr_event_top100  | tabpfn_v2_5   | v2_5        | binary      | success  |          nan |             nan |   0.5      | 0.2       | 0.471354  |   0.693475 | os_3yr        |      nan |                 nan |
| LUAD_core_os_3yr_event_top100  | tabpfn_v2_6   | v2_6        | binary      | success  |          nan |             nan |   0.479167 | 0.468085  | 0.467882  |   0.700657 | os_3yr        |      nan |                 nan |
| LUAD_core_os_3yr_event_top100  | tabpfn_v3     | v3          | binary      | success  |          nan |             nan |   0.458333 | 0.1875    | 0.458333  |   0.69352  | os_3yr        |      nan |                 nan |
| LUAD_core_os_5yr_event_top100  | tabpfn_v2     | v2          | binary      | success  |          nan |             nan |   0.763158 | 0.865672  | 0.429119  |   0.557625 | os_5yr        |      nan |                 nan |
| LUAD_core_os_5yr_event_top100  | tabpfn_v2_5   | v2_5        | binary      | success  |          nan |             nan |   0.763158 | 0.865672  | 0.467433  |   0.555452 | os_5yr        |      nan |                 nan |
| LUAD_core_os_5yr_event_top100  | tabpfn_v2_6   | v2_6        | binary      | success  |          nan |             nan |   0.763158 | 0.865672  | 0.482759  |   0.571587 | os_5yr        |      nan |                 nan |
| LUAD_core_os_5yr_event_top100  | tabpfn_v3     | v3          | binary      | success  |          nan |             nan |   0.763158 | 0.865672  | 0.54023   |   0.552076 | os_5yr        |      nan |                 nan |
| BRCA_core_os_3yr_event_top100  | tabfm_default | tabfm_1_0_0 | binary      | success  |          nan |             nan |   0.868421 | 0.166667  | 0.58042   |   0.369684 | os_3yr        |      nan |                 nan |
| BRCA_core_os_5yr_event_top100  | tabfm_default | tabfm_1_0_0 | binary      | success  |          nan |             nan |   0.754717 | 0.235294  | 0.545614  |   0.569319 | os_5yr        |      nan |                 nan |
| ESCA_core_os_3yr_event_top100  | tabfm_default | tabfm_1_0_0 | binary      | success  |          nan |             nan |   0.769231 | 0.869565  | 0.566667  |   0.713716 | os_3yr        |      nan |                 nan |
| ESCA_core_os_5yr_event_top100  | tabfm_default | tabfm_1_0_0 | binary      | success  |          nan |             nan |   0.916667 | 0.956522  | 0.454545  |   0.325727 | os_5yr        |      nan |                 nan |
| HNSCC_core_os_3yr_event_top100 | tabfm_default | tabfm_1_0_0 | binary      | success  |          nan |             nan |   0.482759 | 0.642857  | 0.465144  |   0.693905 | os_3yr        |      nan |                 nan |
| HNSCC_core_os_5yr_event_top100 | tabfm_default | tabfm_1_0_0 | binary      | success  |          nan |             nan |   0.790698 | 0.883117  | 0.591071  |   0.475703 | os_5yr        |      nan |                 nan |
| LSCC_core_os_3yr_event_top100  | tabfm_default | tabfm_1_0_0 | binary      | success  |          nan |             nan |   0.537037 | 0.545455  | 0.491071  |   0.71133  | os_3yr        |      nan |                 nan |
| LSCC_core_os_5yr_event_top100  | tabfm_default | tabfm_1_0_0 | binary      | success  |          nan |             nan |   0.697674 | 0.816901  | 0.641026  |   0.590041 | os_5yr        |      nan |                 nan |
| LUAD_core_os_3yr_event_top100  | tabfm_default | tabfm_1_0_0 | binary      | success  |          nan |             nan |   0.479167 | 0.468085  | 0.452257  |   0.793725 | os_3yr        |      nan |                 nan |
| LUAD_core_os_5yr_event_top100  | tabfm_default | tabfm_1_0_0 | binary      | success  |          nan |             nan |   0.763158 | 0.861538  | 0.51341   |   0.544451 | os_5yr        |      nan |                 nan |

## Failures

| dataset                        | model_name   | version   | task_type   | status   | error_type   | error_message                                                                                                                                           |   accuracy |   f1 |   roc_auc |   log_loss | task_family   |   pr_auc |   sensitivity_event |
|:-------------------------------|:-------------|:----------|:------------|:---------|:-------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------|-----------:|-----:|----------:|-----------:|:--------------|---------:|--------------------:|
| BRCA_core_os_3yr_event_top100  | tabpfn_v1    | v1        | binary      | failed   | ImportError  | cannot import name 'Optional' from 'torch.nn.modules.transformer' (/home/prime/miniconda3/lib/python3.13/site-packages/torch/nn/modules/transformer.py) |        nan |  nan |       nan |        nan | os_3yr        |      nan |                 nan |
| BRCA_core_os_5yr_event_top100  | tabpfn_v1    | v1        | binary      | failed   | ImportError  | cannot import name 'Optional' from 'torch.nn.modules.transformer' (/home/prime/miniconda3/lib/python3.13/site-packages/torch/nn/modules/transformer.py) |        nan |  nan |       nan |        nan | os_5yr        |      nan |                 nan |
| ESCA_core_os_3yr_event_top100  | tabpfn_v1    | v1        | binary      | failed   | ImportError  | cannot import name 'Optional' from 'torch.nn.modules.transformer' (/home/prime/miniconda3/lib/python3.13/site-packages/torch/nn/modules/transformer.py) |        nan |  nan |       nan |        nan | os_3yr        |      nan |                 nan |
| ESCA_core_os_5yr_event_top100  | tabpfn_v1    | v1        | binary      | failed   | ImportError  | cannot import name 'Optional' from 'torch.nn.modules.transformer' (/home/prime/miniconda3/lib/python3.13/site-packages/torch/nn/modules/transformer.py) |        nan |  nan |       nan |        nan | os_5yr        |      nan |                 nan |
| HNSCC_core_os_3yr_event_top100 | tabpfn_v1    | v1        | binary      | failed   | ImportError  | cannot import name 'Optional' from 'torch.nn.modules.transformer' (/home/prime/miniconda3/lib/python3.13/site-packages/torch/nn/modules/transformer.py) |        nan |  nan |       nan |        nan | os_3yr        |      nan |                 nan |
| HNSCC_core_os_5yr_event_top100 | tabpfn_v1    | v1        | binary      | failed   | ImportError  | cannot import name 'Optional' from 'torch.nn.modules.transformer' (/home/prime/miniconda3/lib/python3.13/site-packages/torch/nn/modules/transformer.py) |        nan |  nan |       nan |        nan | os_5yr        |      nan |                 nan |
| LSCC_core_os_3yr_event_top100  | tabpfn_v1    | v1        | binary      | failed   | ImportError  | cannot import name 'Optional' from 'torch.nn.modules.transformer' (/home/prime/miniconda3/lib/python3.13/site-packages/torch/nn/modules/transformer.py) |        nan |  nan |       nan |        nan | os_3yr        |      nan |                 nan |
| LSCC_core_os_5yr_event_top100  | tabpfn_v1    | v1        | binary      | failed   | ImportError  | cannot import name 'Optional' from 'torch.nn.modules.transformer' (/home/prime/miniconda3/lib/python3.13/site-packages/torch/nn/modules/transformer.py) |        nan |  nan |       nan |        nan | os_5yr        |      nan |                 nan |
| LUAD_core_os_3yr_event_top100  | tabpfn_v1    | v1        | binary      | failed   | ImportError  | cannot import name 'Optional' from 'torch.nn.modules.transformer' (/home/prime/miniconda3/lib/python3.13/site-packages/torch/nn/modules/transformer.py) |        nan |  nan |       nan |        nan | os_3yr        |      nan |                 nan |
| LUAD_core_os_5yr_event_top100  | tabpfn_v1    | v1        | binary      | failed   | ImportError  | cannot import name 'Optional' from 'torch.nn.modules.transformer' (/home/prime/miniconda3/lib/python3.13/site-packages/torch/nn/modules/transformer.py) |        nan |  nan |       nan |        nan | os_5yr        |      nan |                 nan |

## Generated Plots

- `/home/prime/Documents/g3/cancer-survival-exp/plots/fixed_window_foundation_top100/fixed_window_horizon_metric_bars.png`
- `/home/prime/Documents/g3/cancer-survival-exp/plots/fixed_window_foundation_top100/fixed_window_dataset_roc_auc.png`
- `/home/prime/Documents/g3/cancer-survival-exp/plots/fixed_window_foundation_top100/fixed_window_model_metric_heatmap.png`
