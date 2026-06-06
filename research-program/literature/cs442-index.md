# CS 442 — Adversarial ML Course Index

**Instructor:** Bo Li (UIUC)
**Course path:** ~/Documents/cs442-aisecure/
**Total PDFs indexed:** 23 (1 syllabus + 22 papers)

## Syllabus

CS 442 *Trustworthy Machine Learning* (Bo Li, UIUC; TA Zijian Huang). Course objective is to make students fluent in the security and privacy vulnerabilities of ML models and the techniques for hardening them. Grading is exam-heavy (35% final / 25% midterm) with three implementation homeworks requiring TensorFlow/PyTorch and one prerequisite intro-ML class. The reading list lives at aisecure.github.io/TEACHING/CS442/CS442.html; the corpus in this directory is the reading set Bo Li ships with the course and tracks her own publication line — Berkeley/Song-collaboration era through her UIUC certified-robustness program (CARE, KEMLP, CRFL, statistical-learning-with-reasoning).

## Papers / lectures

### arxiv_1412.6572.pdf

**Title:** Explaining and Harnessing Adversarial Examples
**Authors:** Goodfellow, Shlens, Szegedy (Google)
**Year:** 2015 (ICLR)
**Topic tag:** adversarial
**Summary:** Argues neural net vulnerability to adversarial examples is caused by their *linear* behavior in high dimensions, not nonlinearity; introduces the Fast Gradient Sign Method (FGSM) for cheap perturbation generation and uses it for adversarial training.
**Relevance to NuClide research program:** Foundational threat-class definition — every downstream attack we catalog inherits FGSM's gradient-sign primitive as the baseline against which detection/robustness in deployed AI infra is measured.

### arxiv_1607.00133.pdf

**Title:** Deep Learning with Differential Privacy
**Authors:** Abadi, Chu, Goodfellow, McMahan, Mironov, Talwar, Zhang (Google)
**Year:** 2016 (CCS)
**Topic tag:** privacy
**Summary:** Trains deep nets under differential privacy via DP-SGD (clipped per-example gradients + Gaussian noise) and introduces the moments accountant for tighter privacy-budget tracking; demonstrates manageable utility loss on MNIST/CIFAR-10.
**Relevance to NuClide research program:** Defines the canonical privacy-preserving training primitive; relevant when fingerprinting model-training pipelines that claim DP guarantees and verifying whether exposed MLflow/W&B runs actually log epsilon.

### arxiv_1706.03762.pdf

**Title:** Attention Is All You Need
**Authors:** Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin (Google Brain / Research)
**Year:** 2017 (NeurIPS)
**Topic tag:** foundations
**Summary:** Introduces the Transformer, an encoder-decoder architecture built entirely from self-attention with no recurrence or convolution; sets new BLEU SOTA on WMT'14 with a fraction of prior training cost.
**Relevance to NuClide research program:** Architectural substrate for every LLM in our target population — fingerprints, tokenizer leakage, and KV-cache side-channels all assume Transformer-shaped inference.

### arxiv_1707.08945.pdf

**Title:** Robust Physical-World Attacks on Deep Learning Visual Classification
**Authors:** Eykholt, Evtimov, Fernandes, Bo Li, Rahmati, Xiao, Prakash, Kohno, Song
**Year:** 2018 (CVPR)
**Topic tag:** physical-attack
**Summary:** Introduces Robust Physical Perturbations (RP2) to generate adversarial road-sign stickers/posters that survive viewpoint, distance, and lighting variation; the stop-sign-to-speed-limit-45 attack in lab + drive-by field tests.
**Relevance to NuClide research program:** Class-defining physical-world adversarial example; relevant when assessing AI infra deployed in CPS / autonomous-vehicle / industrial-vision pipelines exposed via our recon.

### arxiv_1712.05526.pdf

**Title:** Targeted Backdoor Attacks on Deep Learning Systems Using Data Poisoning
**Authors:** Chen, Liu, Bo Li, Lu, Song (UC Berkeley)
**Year:** 2017
**Topic tag:** backdoor
**Summary:** Shows that injecting as few as ~50 poisoned samples (black-box, no model knowledge, no clean-data access) implants a target-label backdoor in face-recognition systems, including via physical-key triggers like glasses.
**Relevance to NuClide research program:** Defines the weak-threat-model backdoor canon; when surveying exposed training-data buckets or label-store APIs, this is the attack class that makes write-access on the dataset side a critical-path finding.

### arxiv_1712.09491.pdf

**Title:** Exploring the Space of Black-box Attacks on Deep Neural Networks
**Authors:** Bhagoji, He, Bo Li, Song
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Proposes Gradient Estimation black-box attacks that match white-box success rates using only query access to class probabilities, with PCA / random-feature-grouping query reduction; demonstrated against Clarifai's content-moderation API.
**Relevance to NuClide research program:** Operational template for attacking hosted classifier endpoints we discover — query-budget math directly applies to rate-limited public ML APIs.

### arxiv_1801.02610.pdf

**Title:** Generating Adversarial Examples with Adversarial Networks (AdvGAN)
**Authors:** Xiao, Bo Li, Zhu, He, Liu, Song
**Year:** 2018 (IJCAI)
**Topic tag:** adversarial
**Summary:** Trains a GAN whose generator emits perceptually realistic adversarial perturbations in a single forward pass; achieves 92.76% on the MNIST black-box challenge and high transfer against defended models.
**Relevance to NuClide research program:** Generative attacks dominate where defenders rely on L_p bounded adversarial training — relevant baseline when evaluating any model-serving endpoint that claims robustness certifications.

### arxiv_1801.02612.pdf

**Title:** Spatially Transformed Adversarial Examples (stAdv)
**Authors:** Xiao, Zhu, Bo Li, He, Liu, Song
**Year:** 2018 (ICLR)
**Topic tag:** adversarial
**Summary:** Generates adversarial examples by spatially deforming pixels (flow field) rather than perturbing pixel values; produces perceptually smooth attacks that bypass L_p-norm defenses and adversarial training.
**Relevance to NuClide research program:** Demonstrates that the L_p threat model is incomplete; when reading vendor "robust model" claims during target classification, defaults to assuming non-L_p attacks (stAdv, semantic) are unhandled.

### arxiv_1810.05162.pdf

**Title:** Characterizing Adversarial Examples Based on Spatial Consistency Information for Semantic Segmentation
**Authors:** Xiao, Deng, Bo Li, Yu, Liu, Song
**Year:** 2018 (ECCV)
**Topic tag:** defense
**Summary:** Uses spatial-consistency checking across overlapping image patches as a detection signal for adversarial examples in semantic segmentation, robust even against adaptive attackers with full model and detector knowledge.
**Relevance to NuClide research program:** Detection primitive for segmentation pipelines (medical imaging, satellite, autonomous driving) — relevant when assessing whether discovered vision endpoints expose any consistency-based guardrails.

### arxiv_1904.02144.pdf

**Title:** HopSkipJumpAttack: A Query-Efficient Decision-Based Attack
**Authors:** Chen, Jordan, Wainwright (Berkeley / Voleon)
**Year:** 2020 (S&P)
**Topic tag:** adversarial
**Summary:** Decision-based (label-only) black-box attack using a novel gradient-direction estimate at the decision boundary; matches white-box C&W quality with far fewer queries, hyperparameter-free.
**Relevance to NuClide research program:** The realistic threat model for hosted classifiers — label-only access matches most public AI/ML inference endpoints; benchmark for evaluating query-rate-limit defenses.

### arxiv_1904.06347.pdf

**Title:** Unrestricted Adversarial Examples via Semantic Manipulation (cAdv / tAdv)
**Authors:** Bhattad, Chong, Liang, Bo Li, Forsyth (UIUC)
**Year:** 2020 (ICLR)
**Topic tag:** adversarial
**Summary:** Drops the L_p constraint entirely and instead perturbs semantic descriptors (colorization, texture transfer) to produce photorealistic adversarial examples that defeat JPEG/feature-squeezing/adv-training defenses on classification and captioning.
**Relevance to NuClide research program:** Same class as stAdv (semantic > L_p) but proves it scales to ImageNet/MSCOCO and captioning — relevant when assessing multimodal endpoints (vision-language models) we find.

### arxiv_2003.00120.pdf

**Title:** Improving Certified Robustness via Statistical Learning with Logical Reasoning
**Authors:** Yang, Zhao, Wang, Zhang, L. Li, Pei, Karlas, Liu, Guo, C. Zhang, Bo Li
**Year:** 2022 (NeurIPS)
**Topic tag:** certified-defense
**Summary:** Couples DNN sensing components with a Markov Logic Network reasoning component; proves certifying MLN robustness is #P-hard but derives the first certified bound for the joint pipeline, beating SOTA on image + text.
**Relevance to NuClide research program:** Bo Li's UIUC certified-robustness line; relevant as the SOTA defense that any "robust by design" vendor claim should be benchmarked against.

### arxiv_2005.14137.pdf

**Title:** QEBA: Query-Efficient Boundary-Based Blackbox Attack
**Authors:** H. Li, Xu, X. Zhang, Yang, Bo Li (UIUC / Ant Financial)
**Year:** 2020 (CVPR)
**Topic tag:** adversarial
**Summary:** Decision-based black-box attack that estimates the boundary gradient inside a low-dimensional representative subspace (spatial / frequency / PCA); 100% success against Face++ and Azure with far fewer queries than baselines.
**Relevance to NuClide research program:** Operational against deployed face-recognition / content-moderation APIs we discover; the subspace trick is the practical path past per-second query budgets.

### arxiv_2011.13456.pdf

**Title:** Score-Based Generative Modeling through Stochastic Differential Equations
**Authors:** Song, Sohl-Dickstein, Kingma, Kumar, Ermon, Poole (Stanford / Google Brain)
**Year:** 2021 (ICLR)
**Topic tag:** foundations
**Summary:** Unifies score-matching Langevin dynamics and denoising diffusion under a continuous-time SDE framework; introduces predictor-corrector sampling and probability-flow ODE for exact likelihoods, sets CIFAR-10 SOTA.
**Relevance to NuClide research program:** Substrate for the diffusion-model generation ecosystem (Stable Diffusion, AUTOMATIC1111, ComfyUI) we routinely fingerprint — provides the math behind the model files exposed.

### arxiv_2106.06235.pdf

**Title:** Knowledge Enhanced Machine Learning Pipeline against Diverse Adversarial Attacks (KEMLP)
**Authors:** Gürel, Qi, Rimanic, C. Zhang, Bo Li
**Year:** 2021 (ICML)
**Topic tag:** defense
**Summary:** Integrates first-order logic domain knowledge (e.g., "stop signs are octagonal") with weak auxiliary classifiers in a probabilistic factor graph; proves and shows robustness against L_p, physical, unforeseen, and corruption attacks simultaneously.
**Relevance to NuClide research program:** Reference design for layered-defense systems; useful frame when explaining why single-model robustness claims by vendors are insufficient.

### arxiv_2209.05055.pdf

**Title:** CARE: Certifiably Robust Learning with Reasoning via Variational Inference
**Authors:** J. Zhang, L. Li, C. Zhang, Bo Li (UIUC / ETH)
**Year:** 2022
**Topic tag:** certified-defense
**Summary:** Scales the learning+reasoning certified-robustness pipeline to large datasets by approximating MLN inference with GCN-based variational EM; large certified-accuracy gains on AwA2 / Word50 / GTSRB / PDF-malware.
**Relevance to NuClide research program:** Successor to insight_2003.00120; relevant when reviewing PDF-malware detection endpoints and any reasoning-augmented model serving we encounter.

### arxiv.org_1610.05820.pdf

**Title:** Membership Inference Attacks Against Machine Learning Models
**Authors:** Shokri, Stronati, Song, Shmatikov (Cornell / INRIA)
**Year:** 2017 (S&P)
**Topic tag:** privacy
**Summary:** Shadow-model training technique to decide whether a record was in a target model's training set via black-box query access; demonstrated up to 94% inference accuracy against Google and Amazon MLaaS classifiers.
**Relevance to NuClide research program:** Canonical training-set privacy leak; relevant when a hosted-model endpoint is the only attack surface and the question is whether the training data class (PHI/PII) can be inferred without the data itself.

### arxiv.org_1706.04599.pdf

**Title:** On Calibration of Modern Neural Networks
**Authors:** Guo, Pleiss, Sun, Weinberger (Cornell)
**Year:** 2017 (ICML)
**Topic tag:** foundations
**Summary:** Shows that modern deep nets (vs. older shallow ones) are systematically over-confident; identifies depth/width/weight-decay/BatchNorm as causes; demonstrates that single-parameter temperature scaling cures most miscalibration.
**Relevance to NuClide research program:** Calibration is a side-channel — confidence scores from inference endpoints leak information used in MIA and decision-based attacks; relevant background.

### arxiv.org_1902.02918.pdf

**Title:** Certified Adversarial Robustness via Randomized Smoothing
**Authors:** Cohen, Rosenfeld, Kolter (CMU / Bosch)
**Year:** 2019 (ICML)
**Topic tag:** certified-defense
**Summary:** Turns any classifier into a provably L_2-robust smoothed classifier by majority vote over Gaussian-noise corruptions; derives a tight robustness radius and gives the first feasible certified ImageNet defense (49% top-1 at radius 0.5).
**Relevance to NuClide research program:** The dominant scalable certified defense; baseline against which any vendor "provable robustness" claim should be compared.

### arxiv.org_2103.06624.pdf

**Title:** Beta-CROWN: Efficient Bound Propagation with Per-neuron Split Constraints for Neural Network Robustness Verification
**Authors:** S. Wang, H. Zhang, K. Xu, X. Lin, Jana, Hsieh, Kolter
**Year:** 2021 (NeurIPS)
**Topic tag:** certified-defense
**Summary:** Bound-propagation verifier that encodes branch-and-bound neuron-split constraints via optimizable beta parameters; up to 3 orders of magnitude faster than LP-based BaB, winning tool of VNN-COMP 2021.
**Relevance to NuClide research program:** SOTA formal-verification tool for the neural-network robustness problem; relevant when judging whether a deployed "verified" model claim is plausible.

### arxiv.org_2106.08283.pdf

**Title:** CRFL: Certifiably Robust Federated Learning against Backdoor Attacks
**Authors:** Xie, M. Chen, P.-Y. Chen, Bo Li (UIUC / Zhejiang / IBM)
**Year:** 2021 (ICML)
**Topic tag:** certified-defense
**Summary:** First certified-robustness framework for federated learning against backdoor attacks via parameter clipping + smoothing on the global model; provides sample-wise certificates parameterized by poisoning ratio / attacker count.
**Relevance to NuClide research program:** Directly relevant when surveying federated-learning platforms (FedML, NVFlare, Flower) we fingerprint — defines what their threat model should cover.

### oaklandsok.github.io_papernot2018.pdf

**Title:** SoK: Security and Privacy in Machine Learning
**Authors:** Papernot, McDaniel, Sinha, Wellman (Penn State / Michigan)
**Year:** 2018 (IEEE EuroS&P)
**Topic tag:** foundations
**Summary:** Systematization-of-knowledge paper that frames ML security in the CIA model, taxonomizes train-time vs. inference-time attacks on integrity, privacy, and availability, and surveys the corresponding defenses.
**Relevance to NuClide research program:** Reference taxonomy — when classifying a discovered AI/ML endpoint's threat class, this is the canonical lattice we map findings onto.

## Topic distribution

Of 22 papers: 8 adversarial (FGSM, AdvGAN, stAdv, semantic/cAdv-tAdv, HopSkipJump, QEBA, Gradient-Estimation black-box) — the dominant class, tracking Bo Li's own attack line. 5 certified-defense (randomized smoothing, beta-CROWN, statistical-learning-with-reasoning, CARE, CRFL) and 2 empirical defense (KEMLP, spatial-consistency segmentation detector) form a substantial robustness-defense block weighted toward Bo Li's UIUC program. 4 foundations (Transformer, score-based diffusion, calibration, Papernot SoK) supply the substrate. 2 privacy (DP-SGD, Shokri MIA) cover the train-time and inference-time privacy axes. 1 physical-attack (RP2 stop signs) and 1 backdoor / data-poisoning (Chen et al.) complete the threat-model coverage. The course's center of gravity sits at the intersection of adversarial examples and certified robustness, which mirrors the Berkeley→UIUC arc of the instructor's own research line.
