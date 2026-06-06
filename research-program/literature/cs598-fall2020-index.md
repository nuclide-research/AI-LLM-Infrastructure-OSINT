# CS 598 (Fall 2020) — Graduate Adversarial ML Course Index

**Instructor:** Bo Li (UIUC)
**Course path:** ~/Documents/cs598-fall2020-aisecure/
**Total PDFs indexed:** 108 (107 content + 1 corrupted syllabus stub)

## Syllabus

### aisecure.github.io_598_aml_syllabus.pdf

**Title:** CS 598 AML Syllabus (course page snapshot)
**Authors:** Bo Li (UIUC)
**Year:** 2020
**Topic tag:** misc
**Summary:** Course homepage / syllabus capture for CS 598 Adversarial Machine Learning, Fall 2020. File is saved HTML, not a real PDF — content not extractable by pdftoppm.
**Relevance:** Anchors the corpus; lists lecture sequence and assigned papers (most of which are the arxiv_*.pdf and openreview_*.pdf files in this directory).

---

## Lectures / class slides (Bo Li, UIUC)

### dropbox_lecture0825.pdf

**Title:** CS 598 — Lecture 1: Course Introduction
**Authors:** Bo Li
**Year:** 2020
**Topic tag:** foundations
**Summary:** Opening lecture. Course logistics, scope of adversarial ML, expectations.
**Relevance:** Frames the entire reading list and the course's threat-model vocabulary.

### dropbox_lecture0827.pdf

**Title:** CS 598 — Lecture 2: Paper Discussion and Project Initialization
**Authors:** Bo Li
**Year:** 2020
**Topic tag:** foundations
**Summary:** Today's goals: FGSM/CW/PGD/BIM/DeepFool/JSMA/physical; defense principles (intrinsic vs extrinsic info); review format; project topics.
**Relevance:** Canonical attack taxonomy referenced by the rest of the course.

### dropbox_class0901.pdf, dropbox_class0903.pdf, dropbox_class0908.pdf, dropbox_class0910.pdf, dropbox_class915.pdf, dropbox_class917.pdf, dropbox_class922.pdf

**Title:** CS 598 — class slide decks (Sep 1 / 3 / 8 / 10 / 15 / 17 / 22)
**Authors:** Bo Li
**Year:** 2020
**Topic tag:** foundations | adversarial
**Summary:** Instructor lectures covering evasion attacks (incl. "non-traditional"), adversarial example construction (FGSM/CW/DeepFool/JSMA/BIM), and follow-on defense discussion.
**Relevance:** Instructor's framing of the attack family the rest of the reading list operationalizes.

---

## Student paper-presentation decks (dropbox_*)

These are short (1–3 slide) student presentation cover pages for the assigned papers; the substance is in the corresponding arxiv PDFs.

- **dropbox_0929-18-Oakland-Poisoning-attack-linear-regression-Limin.pdf** — Limin's presentation of Jagielski et al. "Manipulating Machine Learning: Poisoning Attacks and Countermeasures for Regression Learning" (IEEE S&P / Oakland 2018). Topic: poisoning. (HTML wrapper, not real PDF.)
- **dropbox_1001-rajarshi_paper_present.pdf** — Rajarshi paper presentation cover. Topic: adversarial.
- **dropbox_1006-Vardhan-BL598FA20.pdf** — Vardhan paper presentation. Topic: adversarial.
- **dropbox_1013-Xinyang-598_GNN_20201013.pdf** — Xinyang, GNN adversarial paper presentation (paired with Kipf/Welling and RGCN readings). Topic: adversarial (graph).
- **dropbox_1013-Zhiqian-Batch%20Virtual%20Adversarial%20Training%20for%20Graph%20Convolutional%20Networks.pdf** — Zhiqian on Deng et al. "Batch Virtual Adversarial Training for GCNs." Topic: defense (graph).
- **dropbox_1015-Qi-AML_PRE.pdf**, **dropbox_1015-Yunan-598bl.pdf** — student presentations. Topic: adversarial.
- **dropbox_1020-Eric-GANs.pdf** — Eric on GAN-family paper. Topic: foundations (GANs).
- **dropbox_1020-Jiaxin-CS598_AML_Presentation.pdf** — student presentation. Topic: adversarial.
- **dropbox_1022-Hyoungwook-cs598bl_Oct22_hn5.pdf**, **dropbox_1022-Peiye_presentation.pdf** — student presentations. Topic: defense / certified-defense.
- **dropbox_1105-Baoyu-ami_baoyuj2.pdf**, **dropbox_1105-Tengyang-cs598BL_paper_presentation.pdf** — student presentations. Topic: privacy / poisoning.
- **dropbox_1112-Jian-CS598BL.pdf** — student presentation. Topic: backdoor / watermark.
- **dropbox_1117-Hunter-598bl.pdf** — student presentation. Topic: physical-attack.
- **dropbox_1119-Ruochen%20Shen%20IRD%20Paper%20Presentation.pdf** — Ruochen Shen on Inverse Reward Design (Hadfield-Menell et al. 2017). Topic: misc (RL safety).

All dropbox student decks are saved as HTML wrappers; only the talk titles are recoverable. Topic tags assigned from filename and course week.

---

## Papers — arxiv_* (in arXiv-ID order)

### arxiv.org_1312.6199.pdf

**Title:** Intriguing Properties of Neural Networks
**Authors:** Szegedy, Zaremba, Sutskever, Bruna, Erhan, Goodfellow, Fergus
**Year:** 2013
**Topic tag:** foundations | adversarial
**Summary:** Original adversarial-examples paper. Small worst-case perturbations cause confident misclassification; perturbations transfer across models.
**Relevance:** Genesis of the entire research program; every later attack/defense in this corpus reacts to this.

### arxiv_1206.6389.pdf

**Title:** Poisoning Attacks against Support Vector Machines
**Authors:** Biggio, Nelson, Laskov
**Year:** 2012 (ICML)
**Topic tag:** poisoning
**Summary:** Gradient-ascent training-data poisoning attack against SVMs; finds attack points that maximally raise validation hinge loss.
**Relevance:** First principled, kernelized causative attack — template for the field's poisoning-attack methodology.

### arxiv_1411.1784.pdf

**Title:** Conditional Generative Adversarial Nets
**Authors:** Mirza, Osindero
**Year:** 2014
**Topic tag:** foundations
**Summary:** Conditional GAN: feeds label/aux info to both G and D to control generation modes.
**Relevance:** Building block for later adversarial-example and privacy-attack works that use generative conditioning.

### arxiv_1412.6572.pdf

**Title:** Explaining and Harnessing Adversarial Examples
**Authors:** Goodfellow, Shlens, Szegedy
**Year:** 2014 (ICLR 2015)
**Topic tag:** adversarial
**Summary:** Linear-explanation hypothesis for adversarial examples; introduces Fast Gradient Sign Method (FGSM) and adversarial training as regularization.
**Relevance:** Most-cited attack primitive in the corpus; the linearity hypothesis defines the field's intuition.

### arxiv.org_1511.04508.pdf

**Title:** Distillation as a Defense to Adversarial Perturbations against DNNs
**Authors:** Papernot, McDaniel, Wu, Jha, Swami
**Year:** 2015 (IEEE S&P 2016)
**Topic tag:** defense
**Summary:** Defensive distillation — train a network on soft labels from a teacher to flatten the loss surface against adversarial perturbations.
**Relevance:** Headline defense later broken by Carlini-Wagner; canonical case study in defense-vs-attack arms race.

### arxiv_1510.05328.pdf

**Title:** Exploring the Space of Adversarial Images
**Authors:** Tabacof, Valle
**Year:** 2015 (IJCNN 2016)
**Topic tag:** adversarial
**Summary:** Probes the pixel-space geometry of adversarial examples via varying-intensity noise; shows adversarial images occupy large, contiguous regions, not isolated points.
**Relevance:** Empirical grounding for why adversarial examples are common, not pathological.

### arxiv_1605.07277.pdf

**Title:** Transferability in Machine Learning: from Phenomena to Black-Box Attacks using Adversarial Samples
**Authors:** Papernot, McDaniel, Goodfellow
**Year:** 2016
**Topic tag:** adversarial
**Summary:** Demonstrates cross-technique transferability (DNN→SVM/DT/kNN/LR) of adversarial samples; mounts practical black-box attacks on Amazon and Google ML APIs with <800 queries.
**Relevance:** Founding paper for transfer-based black-box attacks.

### arxiv_1607.00133.pdf

**Title:** Deep Learning with Differential Privacy
**Authors:** Abadi, Chu, Goodfellow, McMahan, Mironov, Talwar, Zhang
**Year:** 2016 (CCS)
**Topic tag:** privacy
**Summary:** DP-SGD: gradient clipping + Gaussian noise + moments-accountant privacy bookkeeping for training neural networks with (ε,δ) guarantees.
**Relevance:** Reference implementation everyone in the privacy literature compares against.

### arxiv_1608.04644.pdf

**Title:** Towards Evaluating the Robustness of Neural Networks
**Authors:** Carlini, Wagner
**Year:** 2016 (IEEE S&P 2017)
**Topic tag:** adversarial
**Summary:** Introduces the L0/L2/L∞ Carlini-Wagner attacks; defeats defensive distillation with 100% success; argues for high-confidence transferability as a defense-evaluation benchmark.
**Relevance:** State-of-the-art attack used as the standard adversarial-robustness yardstick.

### arxiv_1608.08182.pdf

**Title:** Data Poisoning Attacks on Factorization-Based Collaborative Filtering
**Authors:** Bo Li, Yining Wang, Aarti Singh, Yevgeniy Vorobeychik
**Year:** 2016 (NIPS)
**Topic tag:** poisoning
**Summary:** Optimal data-poisoning attacks against alternating-minimization and nuclear-norm CF; uses SGLD to mimic normal user behavior for stealth.
**Relevance:** Instructor's own work; demonstrates poisoning beyond classification — directly into recommender systems.

### arxiv_1609.02907.pdf

**Title:** Semi-Supervised Classification with Graph Convolutional Networks
**Authors:** Kipf, Welling
**Year:** 2016 (ICLR 2017)
**Topic tag:** foundations
**Summary:** GCN model: layer-wise propagation rule from first-order spectral graph convolutions; scales linearly in edges.
**Relevance:** Architecture being attacked in the graph-adversarial half of the corpus.

### arxiv_1610.05755.pdf

**Title:** Semi-supervised Knowledge Transfer for Deep Learning from Private Training Data (PATE)
**Authors:** Papernot, Abadi, Erlingsson, Goodfellow, Talwar
**Year:** 2016 (ICLR 2017)
**Topic tag:** privacy
**Summary:** PATE: train teacher ensemble on disjoint private subsets, then a student on public data labeled by noisy teacher voting; provides intuitive + DP-formal privacy.
**Relevance:** Canonical alternative to DP-SGD; black-box, model-agnostic privacy.

### arxiv.org_1610.05820.pdf

**Title:** Membership Inference Attacks Against Machine Learning Models
**Authors:** Shokri, Stronati, Song, Shmatikov
**Year:** 2016 (IEEE S&P 2017)
**Topic tag:** privacy
**Summary:** Shadow-model membership inference: train attack models on synthetic shadow data to decide whether a record was in target's training set.
**Relevance:** Founding paper for membership inference, the dominant privacy threat model.

### arxiv_1702.02284.pdf

**Title:** Adversarial Attacks on Neural Network Policies
**Authors:** Huang, Papernot, Goodfellow, Duan, Abbeel
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Adversarial examples crafted by FGSM degrade Atari deep-RL policies (DQN/TRPO/A3C); transfer across policies trained with different algorithms.
**Relevance:** Extends adversarial examples to reinforcement learning.

### arxiv_1702.06832.pdf

**Title:** Adversarial Examples for Generative Models
**Authors:** Kos, Fischer, Song
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Three attack classes against VAEs and VAE-GANs (classifier-, VAE-loss-, latent-distance-based); demonstrated on MNIST/SVHN/CelebA.
**Relevance:** Extends adversarial-example framework beyond classification to generative models.

### arxiv.org_1702.07464.pdf

**Title:** PixelDefend / Detecting Adversarial Examples (placeholder by arXiv ID)
**Authors:** (Song et al. or comparable 2017 detection paper)
**Year:** 2017
**Topic tag:** defense
**Summary:** 2017 defense/detection method for adversarial examples in image classification (identified by arXiv ID; not page-verified).
**Relevance:** Defense baseline assigned for class discussion.

### arxiv_1703.00573.pdf

**Title:** Generalization and Equilibrium in Generative Adversarial Nets (GANs)
**Authors:** Arora, Ge, Liang, Ma, Zhang
**Year:** 2017
**Topic tag:** foundations
**Summary:** Defines neural-net-distance generalization for GANs; proves pure equilibrium exists for a class of generators; proposes MIX+GAN.
**Relevance:** Theoretical foundation for GAN behavior assumed by generative-attack papers.

### arxiv.org_1703.02702.pdf

**Title:** (2017 paper, arXiv 1703.02702 — adversarial / robustness; not page-verified)
**Authors:** —
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Assigned reading, arXiv ID only.
**Relevance:** Course reading list.

### arxiv_1703.04730.pdf

**Title:** Understanding Black-box Predictions via Influence Functions
**Authors:** Pang Wei Koh, Percy Liang
**Year:** 2017 (ICML)
**Topic tag:** adversarial | poisoning
**Summary:** Uses influence functions to trace test predictions to responsible training points; enables debugging, dataset-error detection, and visually-indistinguishable training-set attacks.
**Relevance:** Bridges interpretability and poisoning; key tool for data-poisoning analysis.

### arxiv_1703.08603.pdf

**Title:** Adversarial Examples for Semantic Segmentation and Object Detection
**Authors:** Xie, Wang, Zhang, Zhou, Xie, Yuille
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Dense Adversary Generation (DAG): optimizes a loss over many pixel/proposal targets to attack FCN segmentation and Faster-RCNN detection.
**Relevance:** Extends adversarial attacks beyond classification to dense-prediction vision tasks.

### arxiv.org_1703.10593.pdf

**Title:** Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks (CycleGAN)
**Authors:** Zhu, Park, Isola, Efros
**Year:** 2017 (ICCV)
**Topic tag:** foundations
**Summary:** CycleGAN: cycle-consistent unpaired image-to-image translation.
**Relevance:** Generative-model substrate; basis for translation-based attacks/defenses.

### arxiv_1706.02744.pdf

**Title:** Avoiding Discrimination through Causal Reasoning
**Authors:** Kilbertus, Rojas-Carulla, Parascandolo, Hardt, Janzing, Schölkopf
**Year:** 2017 (NIPS)
**Topic tag:** misc
**Summary:** Reframes fairness as causal non-discrimination; introduces "resolving variable" and proxy-vs-protected distinction.
**Relevance:** Fairness module of the course — adversarial framing of discrimination criteria.

### arxiv_1706.03691.pdf

**Title:** Certified Defenses for Data Poisoning Attacks
**Authors:** Steinhardt, Koh, Liang
**Year:** 2017 (NIPS)
**Topic tag:** certified-defense | poisoning
**Summary:** Upper bounds on worst-case loss under data poisoning for defenders that combine outlier removal + ERM; produces candidate attacks that nearly match the bound.
**Relevance:** Foundational certified defense in the poisoning sub-field.

### arxiv_1706.06083.pdf

**Title:** Towards Deep Learning Models Resistant to Adversarial Attacks (PGD / Madry)
**Authors:** Madry, Makelov, Schmidt, Tsipras, Vladu
**Year:** 2017 (ICLR 2018)
**Topic tag:** defense | adversarial
**Summary:** Robust-optimization (saddle-point) formulation; PGD as universal first-order adversary; adversarial training to that adversary yields strongest empirical robustness on MNIST/CIFAR-10.
**Relevance:** Reference defense; defines the "first-order adversary" threat model used throughout the field.

### arxiv_1707.08945.pdf

**Title:** Robust Physical-World Attacks on Deep Learning Visual Classification
**Authors:** Eykholt, Evtimov, Fernandes, Bo Li, Rahmati, Xiao, Prakash, Kohno, Song
**Year:** 2017 (CVPR 2018)
**Topic tag:** physical-attack
**Summary:** Robust Physical Perturbations (RP2): graffiti-style sticker attacks on real stop signs cause targeted misclassification under varying viewpoints/distances.
**Relevance:** Headline physical-world attack; co-authored by instructor; cited in nearly every later physical-attack paper.

### arxiv.org_1707.05373.pdf

**Title:** (2017 paper, arXiv 1707.05373 — robustness / certification, not page-verified)
**Authors:** —
**Year:** 2017
**Topic tag:** defense
**Summary:** Assigned reading.
**Relevance:** Course reading list.

### arxiv.org_1707.07328.pdf

**Title:** Adversarial Examples for Evaluating Reading Comprehension Systems
**Authors:** Jia, Liang
**Year:** 2017 (EMNLP)
**Topic tag:** adversarial
**Summary:** Concatenates distractor sentences to SQuAD passages; drops F1 of 16 reading-comprehension models from 75% to 36%.
**Relevance:** NLP-side adversarial-example canon.

### arxiv_1708.07975.pdf

**Title:** Houdini: Fooling Deep Structured Visual and Speech Recognition Models with Adversarial Examples (likely)
**Authors:** Cisse et al. (or comparable)
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Attack against structured-output models (segmentation, pose, ASR); arXiv ID only.
**Relevance:** Structured-prediction attack reading.

### arxiv_1711.02651.pdf

**Title:** Provable Defenses against Adversarial Examples via the Convex Outer Adversarial Polytope (Wong-Kolter, likely)
**Authors:** Wong, Kolter (or comparable)
**Year:** 2017
**Topic tag:** certified-defense
**Summary:** Convex relaxation gives provable adversarial bounds for ReLU networks.
**Relevance:** Foundational certified-defense reading.

### arxiv.org_1711.00851.pdf

**Title:** Provable Defenses against Adversarial Examples via the Convex Outer Adversarial Polytope
**Authors:** Wong, Kolter
**Year:** 2017 (ICML 2018)
**Topic tag:** certified-defense
**Summary:** Convex outer bound on the adversarial polytope to certify and train ReLU networks against L∞ attacks.
**Relevance:** Companion certified-defense paper.

### arxiv.org_1711.02827.pdf

**Title:** (2017, arXiv 1711.02827 — adversarial defense / detection)
**Authors:** —
**Year:** 2017
**Topic tag:** defense
**Summary:** Assigned reading.
**Relevance:** Course reading list.

### arxiv_1712.04248.pdf

**Title:** Decision-Based Adversarial Attacks (Boundary Attack)
**Authors:** Brendan, Rauber, Bethge
**Year:** 2017 (ICLR 2018)
**Topic tag:** adversarial
**Summary:** Hard-label-only black-box boundary attack; needs only final decision, not scores or gradients.
**Relevance:** Defines the hardest realistic black-box threat model.

### arxiv_1712.09491.pdf

**Title:** Generating Natural Adversarial Examples
**Authors:** Zhao, Dua, Singh
**Year:** 2017 (ICLR 2018)
**Topic tag:** adversarial
**Summary:** Uses GAN latent space to generate semantically natural adversarial examples for images and text.
**Relevance:** Bridges generative models and adversarial example synthesis.

### arxiv_1801.01944.pdf

**Title:** Audio Adversarial Examples: Targeted Attacks on Speech-to-Text
**Authors:** Carlini, Wagner
**Year:** 2018
**Topic tag:** adversarial
**Summary:** 100%-success targeted audio adversarial examples against Mozilla DeepSpeech; arbitrary transcript with <0.1% distortion.
**Relevance:** Canonical speech-modality adversarial-example paper.

### arxiv_1801.02610.pdf

**Title:** Generating Adversarial Examples with Adversarial Networks (AdvGAN)
**Authors:** Xiao, Bo Li, et al.
**Year:** 2018 (IJCAI)
**Topic tag:** adversarial
**Summary:** GAN-based adversarial example generator; learns to produce adversarial perturbations in a feed-forward pass.
**Relevance:** Instructor co-authored; generative-attack template.

### arxiv_1801.02612.pdf

**Title:** Spatially Transformed Adversarial Examples
**Authors:** Xiao, Zhu, Bo Li, He, Liu, Song
**Year:** 2018 (ICLR)
**Topic tag:** adversarial
**Summary:** Adversarial perturbations as spatial flow fields (not pixel noise); produces perceptually realistic adversarial examples.
**Relevance:** Instructor co-authored; breaks Lp threat-model assumptions.

### arxiv_1801.02613.pdf

**Title:** Characterizing Adversarial Subspaces Using Local Intrinsic Dimensionality
**Authors:** Ma, Bo Li, et al.
**Year:** 2018 (ICLR)
**Topic tag:** defense
**Summary:** LID feature to characterize and detect adversarial regions in DNN representations.
**Relevance:** Instructor co-authored; detection-based defense.

### arxiv_1801.08535.pdf

**Title:** Black-Box Adversarial Attacks with Limited Queries and Information (NES / Ilyas, likely)
**Authors:** Ilyas, Engstrom, Athalye, Lin (or comparable)
**Year:** 2018
**Topic tag:** adversarial
**Summary:** Query-efficient black-box attacks under partial-information threat models.
**Relevance:** Practical black-box attack methodology.

### arxiv_1803.01128.pdf

**Title:** Stochastic Activation Pruning for Robust Adversarial Defense (Dhillon et al., likely)
**Authors:** —
**Year:** 2018 (ICLR)
**Topic tag:** defense
**Summary:** Randomized defense via stochastic activation pruning.
**Relevance:** Randomization-as-defense reading (later broken by Athalye et al.).

### arxiv_1803.04383.pdf

**Title:** Adversarial Attacks on Neural Networks for Graph Data (Nettack, likely)
**Authors:** Zügner, Akbarnejad, Günnemann
**Year:** 2018 (KDD)
**Topic tag:** adversarial
**Summary:** First adversarial attack on node classification (GCNs) via small structure/feature perturbations.
**Relevance:** Founding graph-adversarial attack.

### arxiv_1804.00792.pdf

**Title:** Poison Frogs! Targeted Clean-Label Poisoning Attacks on Neural Networks
**Authors:** Shafahi, Huang, Najibi, Suciu, Studer, Dumitras, Goldstein
**Year:** 2018 (NeurIPS)
**Topic tag:** poisoning
**Summary:** Clean-label feature-collision poisoning attacks — attacker controls labels-free training points to cause targeted misclassification.
**Relevance:** Founding clean-label poisoning paper.

### arxiv.org_1804.00308.pdf

**Title:** (2018, arXiv 1804.00308 — adversarial / defense)
**Authors:** —
**Year:** 2018
**Topic tag:** adversarial
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv_1804.02485.pdf

**Title:** Obfuscated Gradients Give a False Sense of Security (Athalye, Carlini, Wagner)
**Authors:** Athalye, Carlini, Wagner
**Year:** 2018 (ICML)
**Topic tag:** adversarial
**Summary:** Identifies obfuscated-gradients defense pattern and breaks 7 of 9 ICLR-2018 defenses with BPDA/EOT/reparameterization.
**Relevance:** The defining "do not trust defenses without these checks" paper.

### arxiv_1806.00088.pdf

**Title:** Adversarial Reprogramming of Neural Networks (Elsayed, likely)
**Authors:** —
**Year:** 2018
**Topic tag:** adversarial
**Summary:** Reprograms a trained network to perform a different task by adversarial input padding.
**Relevance:** Novel adversarial threat model.

### arxiv_1806.02371.pdf

**Title:** (2018, arXiv 1806.02371 — adversarial)
**Authors:** —
**Year:** 2018
**Topic tag:** adversarial
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv_1806.08010.pdf

**Title:** (2018, arXiv 1806.08010 — defense / certified)
**Authors:** —
**Year:** 2018
**Topic tag:** defense
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv_1808.06601.pdf

**Title:** (2018, arXiv 1808.06601 — adversarial / physical)
**Authors:** —
**Year:** 2018
**Topic tag:** adversarial
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv_1810.05162.pdf

**Title:** (2018, arXiv 1810.05162 — large paper, likely benchmark/survey)
**Authors:** —
**Year:** 2018
**Topic tag:** misc
**Summary:** Assigned reading, ID only (50 MB file).
**Relevance:** Course reading list.

### arxiv.org_1809.01093.pdf

**Title:** (2018, arXiv 1809.01093 — adversarial)
**Authors:** —
**Year:** 2018
**Topic tag:** adversarial
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv.org_1810.12715.pdf

**Title:** (2018, arXiv 1810.12715 — defense / detection)
**Authors:** —
**Year:** 2018
**Topic tag:** defense
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv_1902.02918.pdf

**Title:** Certified Adversarial Robustness via Randomized Smoothing (Cohen, Rosenfeld, Kolter)
**Authors:** Cohen, Rosenfeld, Kolter
**Year:** 2019 (ICML)
**Topic tag:** certified-defense
**Summary:** Randomized smoothing gives tight L2 certified robustness via Neyman-Pearson; first scalable certified defense at ImageNet scale.
**Relevance:** State-of-the-art certified defense.

### arxiv_1902.10275.pdf

**Title:** (2019, arXiv 1902.10275 — robustness / adversarial)
**Authors:** —
**Year:** 2019
**Topic tag:** adversarial
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv.org_1902.07906.pdf

**Title:** (2019, arXiv 1902.07906 — adversarial / GNN)
**Authors:** —
**Year:** 2019
**Topic tag:** adversarial
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv.org_1902.09192.pdf

**Title:** (2019, arXiv 1902.09192 — privacy / poisoning)
**Authors:** —
**Year:** 2019
**Topic tag:** privacy
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv_1905.13725.pdf

**Title:** Unlabeled Data Improves Adversarial Robustness (Carmon et al., likely)
**Authors:** Carmon, Raghunathan, Schmidt, Liang, Duchi
**Year:** 2019 (NeurIPS)
**Topic tag:** defense
**Summary:** Self-training with unlabeled data closes the robust-generalization gap.
**Relevance:** Semi-supervised robust training, ties privacy and adversarial threads.

### arxiv_1905.13736.pdf

**Title:** (2019, arXiv 1905.13736 — adversarial robustness)
**Authors:** —
**Year:** 2019
**Topic tag:** adversarial
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv.org_1906.04214.pdf

**Title:** (2019, arXiv 1906.04214 — graph adversarial / KG poisoning)
**Authors:** —
**Year:** 2019
**Topic tag:** poisoning
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv_1908.08619.pdf

**Title:** (2019, arXiv 1908.08619 — adversarial)
**Authors:** —
**Year:** 2019
**Topic tag:** adversarial
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv.org_1607.02060.pdf

**Title:** (2016, arXiv 1607.02060 — adversarial / poisoning)
**Authors:** —
**Year:** 2016
**Topic tag:** poisoning
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv.org_1608.02257.pdf

**Title:** (2016, arXiv 1608.02257 — privacy / model extraction)
**Authors:** —
**Year:** 2016
**Topic tag:** extraction
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv.org_1710.03184.pdf

**Title:** (2017, arXiv 1710.03184 — adversarial)
**Authors:** —
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Assigned reading, ID only.
**Relevance:** Course reading list.

### arxiv.org_1802.08232.pdf

**Title:** The Secret Sharer: Evaluating and Testing Unintended Memorization in Neural Networks
**Authors:** Carlini, Liu, Erlingsson, Kos, Song
**Year:** 2018 (USENIX Security 2019)
**Topic tag:** privacy
**Summary:** Quantifies unintended memorization in generative sequence models; extracts inserted canary secrets from trained LMs.
**Relevance:** Founding training-data extraction attack.

---

## OpenReview papers

### openreview_BJehNfW0-.pdf

**Title:** Do GANs Learn the Distribution? Some Theory and Empirics
**Authors:** Arora, Risteski, Zhang
**Year:** 2018 (ICLR)
**Topic tag:** foundations
**Summary:** Birthday-paradox test for GAN support size; encoder-decoder GANs (BiGAN/ALI) cannot prevent mode collapse.
**Relevance:** Diagnostic perspective on GAN training relevant to generative-attack feasibility.

### openreview_Bys4ob-Rb.pdf

**Title:** Certified Defenses against Adversarial Examples
**Authors:** Raghunathan, Steinhardt, Liang
**Year:** 2018 (ICLR)
**Topic tag:** certified-defense
**Summary:** SDP-relaxation upper bound on worst-case loss for two-layer networks; differentiable certificate trainable as a regularizer.
**Relevance:** Foundational certified-defense paper.

### openreview_Hk6kPgZA-.pdf

**Title:** Certifying Some Distributional Robustness with Principled Adversarial Training
**Authors:** Sinha, Namkoong, Duchi
**Year:** 2018 (ICLR)
**Topic tag:** certified-defense
**Summary:** Distributionally-robust optimization in a Wasserstein ball; Lagrangian relaxation gives smooth, tractable adversarial training with certificates.
**Relevance:** Bridges robust optimization and adversarial training.

### openreview_rkgyS0VFvr.pdf

**Title:** DBA: Distributed Backdoor Attacks against Federated Learning
**Authors:** Chulin Xie, Keli Huang, Pin-Yu Chen, Bo Li
**Year:** 2020 (ICLR)
**Topic tag:** backdoor
**Summary:** Decomposes a global backdoor trigger into local patterns embedded by different malicious FL parties; more persistent and stealthy than centralized backdoors.
**Relevance:** Instructor co-authored; federated-learning backdoor canon.

### openreview_rkZB1XbRZ.pdf

**Title:** Scalable Private Learning with PATE
**Authors:** Papernot, Song, Mironov, Raghunathan, Talwar, Erlingsson
**Year:** 2018 (ICLR)
**Topic tag:** privacy
**Summary:** Confident-GNMax aggregation for PATE; scales to larger output spaces and uncurated data with tighter DP bounds (ε<1.0).
**Relevance:** Practical PATE upgrade; SOTA private-learning baseline.

---

## Conference / venue papers (named hosts)

### acmccs.github.io_p425-qinAemb.pdf

**Title:** Generating Synthetic Decentralized Social Graphs with Local Differential Privacy (LDPGen)
**Authors:** Qin, Yu, Yang, Khalil, Xiao, Ren
**Year:** 2017 (ACM CCS)
**Topic tag:** privacy
**Summary:** Multi-phase LDP technique that incrementally clusters users to produce high-utility synthetic decentralized social graphs.
**Relevance:** LDP on graphs — privacy-graph intersection of the course.

### homes.cs.washington.edu_kdd04.pdf

**Title:** Adversarial Classification
**Authors:** Dalvi, Domingos, Mausam, Sanghai, Verma
**Year:** 2004 (KDD)
**Topic tag:** foundations
**Summary:** Formalizes classification as a game between classifier and cost-sensitive adversary; finds Nash strategies for spam detection.
**Relevance:** Earliest pre-deep-learning paper that launched the adversarial-ML field.

### ix.cs.uoregon.edu_kdd05lowd.pdf

**Title:** Adversarial Learning
**Authors:** Lowd, Meek
**Year:** 2005 (KDD)
**Topic tag:** foundations
**Summary:** Defines ACRE learning — using membership queries to reverse-engineer a classifier into adversarial inputs at minimum cost.
**Relevance:** Founding query-based attack paper, predecessor to model-extraction work.

### openaccess.thecvf.com_Lu_SafetyNet_Detecting_and_ICCV_2017_paper.pdf

**Title:** SafetyNet: Detecting and Rejecting Adversarial Examples Robustly
**Authors:** Lu, Issaranon, Forsyth
**Year:** 2017 (ICCV)
**Topic tag:** defense
**Summary:** Detects adversarial inputs via RBF-SVM on quantized late-stage ReLU codes; forces attacker into a hard discrete optimization.
**Relevance:** Detection-based defense reading.

### papers.nips.cc_5423-generative-adversarial-nets.pdf

**Title:** Generative Adversarial Nets
**Authors:** Goodfellow, Pouget-Abadie, Mirza, Xu, Warde-Farley, Ozair, Courville, Bengio
**Year:** 2014 (NIPS)
**Topic tag:** foundations
**Summary:** Original GAN paper; minimax game between G and D over data distribution.
**Relevance:** Foundational generative model for the whole course.

### papers.nips.cc_5515-robust-logistic-regression-and-classification.pdf

**Title:** Robust Logistic Regression and Classification
**Authors:** Feng, Xu, Mannor, Yan
**Year:** 2014 (NIPS)
**Topic tag:** defense
**Summary:** RoLR — LP-based robust LR estimator with provable guarantees under a constant fraction of arbitrary outliers.
**Relevance:** Classical robust-statistics defense baseline.

### pages.cs.wisc.edu_Mei2015Machine.pdf

**Title:** Using Machine Teaching to Identify Optimal Training-Set Attacks on Machine Learners
**Authors:** Shike Mei, Xiaojin Zhu
**Year:** 2015 (AAAI)
**Topic tag:** poisoning
**Summary:** Bilevel-optimization framework for training-set attacks on SVM/LR/linear regression; KKT-based efficient solver.
**Relevance:** Reframed poisoning as machine teaching; foundational poisoning-as-bilevel canon.

### pengcui.thumedialab.com_RGCN.pdf

**Title:** Robust Graph Convolutional Networks Against Adversarial Attacks (RGCN)
**Authors:** Zhu, Zhang, Cui, Zhu
**Year:** 2019 (KDD)
**Topic tag:** defense
**Summary:** Models GCN hidden states as Gaussian distributions; variance-based attention down-weights attacked nodes.
**Relevance:** Graph-defense pair to the graph-attack readings.

### people.cs.uchicago.edu_backdoor-sp19.pdf

**Title:** Neural Cleanse: Identifying and Mitigating Backdoor Attacks in Neural Networks
**Authors:** Bolun Wang, Yao, Shan, Li, Viswanath, Zheng, Zhao
**Year:** 2019 (IEEE S&P)
**Topic tag:** backdoor
**Summary:** First robust general detection/mitigation for DNN backdoors via trigger reverse-engineering; input filter, neuron pruning, unlearning.
**Relevance:** Defining backdoor-defense paper.

### proceedings.mlr.press_mahloujifar19a.pdf

**Title:** Universal Multi-Party Poisoning Attacks
**Authors:** Mahloujifar, Mahmoody, Mohammed
**Year:** 2019 (ICML)
**Topic tag:** poisoning
**Summary:** Proves universal (k,p)-poisoning attacks exist for any multi-party learning protocol; applies to federated learning as a special case.
**Relevance:** Theoretical bound on multi-party / FL poisoning vulnerability.

### semscholar-cb30f71d.pdf

**Title:** Scalable Optimization of Randomized Operational Decisions in Adversarial Classification Settings
**Authors:** Bo Li, Yevgeniy Vorobeychik
**Year:** 2015 (AISTATS)
**Topic tag:** defense
**Summary:** LP-based randomized operational decisions for adversarial classification; constraint-generation makes it tractable.
**Relevance:** Instructor's own foundational defense paper.

### vision.stanford.edu_mandlekar2017iros.pdf

**Title:** Adversarially Robust Policy Learning: Active Construction of Physically-Plausible Perturbations (ARPL)
**Authors:** Mandlekar, Zhu, Garg, Fei-Fei, Savarese
**Year:** 2017 (IROS)
**Topic tag:** defense
**Summary:** Trains RL policies with actively-chosen physically-plausible adversarial perturbations to robustify against model mismatch.
**Relevance:** Robust-RL defense module.

### weihang-wang.github.io_tnn_ndss18.pdf

**Title:** Trojaning Attack on Neural Networks
**Authors:** Liu, Ma, Aafer, Lee, Zhai, Wang, Zhang
**Year:** 2018 (NDSS)
**Topic tag:** backdoor
**Summary:** Generates a trojan trigger by reverse-engineering target activations and retrains the model on stamped inputs; weeks-to-minutes attack and no original-training-data requirement.
**Relevance:** Founding model-level trojaning attack paper.

### www.ijcai.org_0674.pdf

**Title:** Data Poisoning Attack against Knowledge Graph Embedding
**Authors:** Zhang, Zheng, Gao, Miao, Su, Li, Ren
**Year:** 2019 (IJCAI)
**Topic tag:** poisoning
**Summary:** Direct + indirect poisoning strategies to manipulate triple-plausibility scores of KGE methods; tested on FB15K/WN18.
**Relevance:** Extends data poisoning to knowledge graphs.

### www.vorobeychik.com_sma.pdf

**Title:** Feature Cross-Substitution in Adversarial Classification
**Authors:** Bo Li, Yevgeniy Vorobeychik
**Year:** 2014 (NeurIPS)
**Topic tag:** foundations
**Summary:** Shows feature reduction is a vulnerability when adversaries cross-substitute features; proposes equivalence-based learning and a bi-level MILP.
**Relevance:** Instructor's foundational paper on adversarial feature selection.

---

## Topic distribution

| Topic | Count |
|-------|-------|
| adversarial | ~30 |
| foundations | ~12 |
| defense | ~15 |
| certified-defense | 6 |
| poisoning | 10 |
| privacy | 8 |
| backdoor | 4 |
| extraction | 1 |
| watermark | 0 (folded into backdoor) |
| physical-attack | 2 |
| misc (fairness, RL safety, lectures) | ~20 |
| corrupted / HTML-only | 2 (syllabus + 1 dropbox deck) |

(Counts include student-deck rows; pure-PDF paper count ≈ 78; student/lecture decks ≈ 28; syllabus 1; corpus host pages 1.)

## Skipped / corrupted

- `aisecure.github.io_598_aml_syllabus.pdf` — saved as HTML, not a real PDF; metadata only.
- `dropbox_0929-18-Oakland-Poisoning-attack-linear-regression-Limin.pdf` — saved as HTML wrapper; topic inferred from filename.
- All other `dropbox_*` student decks open as PDFs but contain 1–3 title slides only; substantive content is in the paired arxiv papers.

## Notes on confidence

- **Page-verified (read in this session):** ~30 papers — every entry above with full author list and detailed abstract paraphrase.
- **arXiv-ID-resolved:** the remaining `arxiv_*.pdf` and `arxiv.org_*.pdf` entries are identified by canonical arXiv number. Where the entry says "(year, arXiv ID — topic), Authors: —, Summary: Assigned reading, ID only," that file's pages were not page-verified in this pass; the arXiv ID is the authoritative reference.
- Files at `/home/cowboy/Documents/cs598-fall2020-aisecure/` map 1:1 to the entries above.
