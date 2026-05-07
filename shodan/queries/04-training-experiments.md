# 4. Training, Fine-Tuning & Experiments

_Section verified: April 22, 2026 11:38_

Tooling for model training, hyperparameter sweeps, dataset annotation, and experiment tracking. Exposed instances frequently disclose proprietary training data, custom model weights, evaluation prompts, and HuggingFace tokens stored as secrets.

## Fine-Tuning / Training

| Shodan Query | Notes |
|---|---|
| `"clearml"` | 170 hits, bare-string form, catches any ClearML banner regardless of port |
| `http.title:"ClearML"` | 112 hits, ClearML UI title match |
| `http.html:"clearml"` | 126 hits, ClearML in HTML body |
| `"Axolotl"` | 55 hits, bare form; port:8080 variant returns 0 (not exposed on that port) |
| `http.html:"axolotl"` | 45 hits, Axolotl fine-tuning framework in HTML body |
| `http.html:"unsloth"` | 55 hits, best Unsloth fingerprint; port:7860 returns 0 |
| `"unsloth"` | 49 hits, bare banner match |
| `http.title:"Axolotl"` | 26 hits, Axolotl UI title form |
| `http.html:"openllm"` | 8 hits, OpenLLM in HTML body |
| `"OpenLLM"` | 3 hits, bare banner |
| `"bentoml"` | 2 hits, bare-string form, catches BentoML regardless of port |
| `http.html:"bentoml"` | 90 hits, BentoML in HTML body (best form) |
| `"BentoML"` | 2 hits, bare banner match |
| `http.html:"ray dashboard"` | 54 hits, tightest live Ray fingerprint; see note below |
| `"Ray" "dashboard"` | 1,385 hits, ⚠️ "ray" is common English; use `http.html:"ray dashboard"` instead |
| `http.html:"ray serve"` | 13 hits, Ray Serve in HTML body |
| `"Ray Serve"` | 13 hits, Ray Serve banner match |
| `http.title:"Determined"` | 60 hits, Determined AI (HPE) platform; best live form |
| `http.title:"LLaMA Factory"` | 12 hits, LLaMA-Factory WebUI title |
| `http.html:"llama-factory"` | 2 hits, LLaMA-Factory in HTML body |
| `"LLaMA-Factory"` | 2 hits, bare banner |
| `http.html:"lightning.ai"` | 3 hits, Lightning AI reference in HTML body |
| `"SageMaker" "notebook"` | 449 hits, SageMaker notebook (no port) |
| `http.title:"SageMaker"` | 315 hits, SageMaker UI title |
| `http.html:"sagemaker"` | 391 hits, SageMaker in HTML body |
| `"feast"` | 112 hits, ⚠️ bare "feast" is food/event noise; `"feast" "feature"` → 4 hits, confirming collision |
| `"tecton"` | 11 hits, ⚠️ narrow but check manually; no domain-specific narrower term narrows further |
| `"feature platform"` | 83 hits, ⚠️ generic phrase, likely marketing/docs noise; no Tecton-specific narrowing term |

**Ray dashboard is the single highest-severity query in this reference.** CVE-2023-48022 (ShadowRay) is unauthenticated RCE via the job submission API, actively exploited since disclosure, and the patch requires operator action (not automatic). A Ray dashboard on the public internet should be treated as already-compromised infrastructure until proven otherwise.

## ML Experiment / Pipeline Tools

| Shodan Query | Notes |
|---|---|
| `http.title:"Kubeflow Central Dashboard"` | 617 hits, tightest Kubeflow fingerprint; catches non-default ports |
| `http.title:"Airflow"` | 48,445 hits, ⚠️ massive pollution; `http.title:"Airflow" "DAG"` = 0, confirming collision |
| `http.html:"streamlit"` | 26,023 hits, Streamlit in HTML body; high but specific (branded JS token) |
| `"Streamlit"` | 780 hits, Streamlit bare banner |
| `http.title:"Jupyter"` | 11,712 hits, Jupyter UI title; broadest real Jupyter surface |
| `http.html:"jupyter"` | 15,893 hits, Jupyter in HTML body |
| `"Jupyter"` | 5,355 hits, Jupyter bare banner |
| `"Jupyter" "notebook"` | 85 hits, Jupyter notebook banner (no port) |
| `http.html:"gradio"` | 2,500 hits, Gradio in HTML body |
| `"Gradio"` | 236 hits, Gradio bare banner |
| `http.html:"apache airflow"` | 346 hits, best Airflow fingerprint (product-specific phrase) |
| `"Airflow"` | 664 hits, Airflow bare banner (reasonably specific) |
| `http.title:"Dagster"` | 470 hits, Dagster UI title |
| `http.html:"dagster"` | 488 hits, Dagster in HTML body |
| `"Dagster"` | 687 hits, Dagster bare banner |
| `http.title:"MLflow"` | 1,481 hits, MLflow UI title (best MLflow form) |
| `http.html:"mlflow"` | 708 hits, MLflow in HTML body |
| `"MLflow"` | 95 hits, MLflow bare banner |
| `http.html:"kubeflow"` | 1,033 hits, Kubeflow in HTML body |
| `"kubernetes" "ml-pipeline"` | 1 hit, Kubeflow Pipelines API on k8s |
| `"ml-pipeline"` | 8 hits, bare-string form; catches Kubeflow Pipelines API containers on any port |
| `http.html:"wandb"` | 96 hits, W&B in HTML body |
| `"wandb-local"` | 1 hit, W&B local container (no port restriction) |
| `http.title:"Weights & Biases" -site:wandb.ai` | 1 hit, self-hosted W&B; almost entirely SaaS, self-hosted is rare |
| `"Dagster" port:3000` | 157 hits, Dagster on default port |
| `"Jupyter" port:8888 "notebook"` | 1 hit, original query; port filter over-restrictive |

## Annotation / RLHF / Eval

| Shodan Query | Notes |
|---|---|
| `http.title:"Label Studio"` | 1,728 hits, Label Studio UI title; best form |
| `http.html:"label-studio"` | 1,815 hits, hyphenated form in HTML; highest-yield Label Studio fingerprint |
| `http.html:"label studio"` | 1,815 hits, same corpus as hyphenated (same count) |
| `http.html:"cvat"` | 552 hits, CVAT computer-vision annotation in HTML body |
| `http.title:"CVAT"` | 6 hits, CVAT title (most deploys use path prefix, not root) |
| `http.html:"argilla"` | 51 hits, Argilla in HTML body |
| `http.title:"Argilla"` | 43 hits, Argilla UI title |
| `"argilla"` | 21 hits, bare-string form, catches Argilla regardless of port |
| `http.html:"doccano"` | 187 hits, Doccano text/NLP annotation in HTML |
| `http.title:"Doccano"` | 177 hits, Doccano title match |
| `http.html:"promptfoo"` | 19 hits, Promptfoo eval dashboards in HTML body (best form) |
| `http.html:"deepeval"` | 4 hits, DeepEval in HTML body |
| `"humanloop" -site:humanloop.com` | 1 hit, self-hosted Humanloop; almost entirely SaaS |
