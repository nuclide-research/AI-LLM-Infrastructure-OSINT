# CS 562 — Secure ML Course Index

**Instructor:** Bo Li (UIUC)
**TA:** Zijian Huang
**Course path:** ~/Documents/cs562-aisecure/
**Course URL:** https://aisecure.github.io/TEACHING/CS562/CS562.html
**Total PDFs indexed:** 83

## Syllabus

CS 562 "Advanced Topics in Security, Privacy and Machine Learning" — UIUC graduate seminar by Bo Li. Objective: equip students to understand security and privacy vulnerabilities of ML models and to build robust learning systems. Grading: 65% group project (proposal/status/final), 30% paper reading + presentation, 5% participation. Prereqs: prior ML coursework, ability to train neural nets in TF/PyTorch. Tentative project goal: each group produces a top-tier conference submission.

**Candidate final-project topics:** attacks on 3D reconstruction / BERT / RL; deepfake detection; poisoning robustness; GWAS-style AI hardening; certified robustness against Lp attacks and arbitrary perturbations; GAN theory (game-theoretic); GAN Zoo applications; DP graphs and robust GCNs (privacy attacks + DP-GCNs); privacy analysis for generative models; robust RL; semi-supervised + distributional-robust unlabeled-data approaches; robustness testing of DNN architectures; robust AutoML; safety-critical scenario generation for autonomous driving in CARLA.

Includes one invited talk (Huan Zhang, CMU) on formal verification of DNNs via bound-propagation (CROWN / α,β-CROWN / VNN-COMP).

## Papers / lectures

### aisecure.github.io_syllabus.pdf
**Title:** CS 562 Syllabus
**Authors:** Bo Li (instructor), Zijian Huang (TA)
**Year:** 2020
**Topic tag:** misc
**Summary:** Course syllabus listing objectives, grading, prereqs, and 15 candidate project topics across attacks, defenses, certified robustness, DP, GANs, robust RL.
**Relevance:** Roadmap of the secure-ML landscape Bo Li considers canonical reading.

### aisecure.github.io_abstract1020.pdf
**Title:** Formal Verification of Deep Neural Networks: Challenges and Recent Advances
**Authors:** Huan Zhang (CMU, w/ Zico Kolter)
**Year:** 2022
**Topic tag:** defense
**Summary:** Invited-talk abstract describing bound-propagation verifiers (CROWN, β-CROWN, α,β-CROWN) that won VNN-COMP 2021/2022 and recent advances/challenges in NN formal verification.
**Relevance:** Certified-defense pillar; surveys verifier state-of-the-art for robust deployment.

### acmccs.github.io_p425-qinAemb.pdf
**Title:** Generating Synthetic Decentralized Social Graphs with Local Differential Privacy (LDPGen)
**Authors:** Zhan Qin, Ting Yu, Yin Yang, Issa Khalil, Xiaokui Xiao, Kui Ren
**Year:** 2017 (CCS)
**Topic tag:** differential-privacy
**Summary:** Multi-phase LDP scheme that incrementally clusters users from local neighbor lists and synthesises a graph preserving structure under edge-LDP, beating naive randomized-response baselines on four real graphs.
**Relevance:** Concrete LDP application to graph data; informs DP-GCN project track.

### arxiv_1206.6389.pdf
**Title:** Poisoning Attacks against Support Vector Machines
**Authors:** Biggio, Nelson, Laskov
**Year:** 2012 (ICML)
**Topic tag:** poisoning
**Summary:** Gradient-ascent attack that constructs training points to maximally raise SVM test error by exploiting KKT-derived implicit gradients of the optimal hyperplane.
**Relevance:** Foundational training-time attack paper; basis for later bilevel poisoning work.

### arxiv_1411.1784.pdf
**Title:** Conditional Generative Adversarial Nets
**Authors:** Mirza, Osindero
**Year:** 2014
**Topic tag:** foundations
**Summary:** Conditions both G and D on auxiliary information y to allow class-conditional GAN sampling on MNIST and multi-modal image-tagging.
**Relevance:** Building block for the "Applications of GANs" track.

### arxiv_1412.6572.pdf
**Title:** Explaining and Harnessing Adversarial Examples
**Authors:** Goodfellow, Shlens, Szegedy
**Year:** 2015 (ICLR)
**Topic tag:** adversarial
**Summary:** Argues adversarial vulnerability is a linear-model phenomenon and introduces the Fast Gradient Sign Method (FGSM) plus adversarial training as regularizer.
**Relevance:** Canonical entry point to evasion attacks and adversarial training.

### arxiv_1510.05328.pdf
**Title:** Stealing Machine Learning Models via Prediction APIs
**Authors:** Tramèr, Zhang, Juels, Reiter, Ristenpart
**Year:** 2016 (USENIX Security)
**Topic tag:** extraction
**Summary:** Demonstrates equation-solving and path-finding attacks that reconstruct logistic-regression, SVM, NN, and tree models from black-box query/confidence APIs at BigML/AWS.
**Relevance:** Foundational model-extraction work; threat model for cloud ML APIs.

### arxiv_1605.07277.pdf
**Title:** Transferability in Machine Learning: from Phenomena to Black-Box Attacks
**Authors:** Papernot, McDaniel, Goodfellow
**Year:** 2016
**Topic tag:** adversarial
**Summary:** Shows adversarial examples transfer across models and architectures, enabling black-box attacks by training a local substitute on labels queried from the target.
**Relevance:** Justifies black-box threat models throughout the course.

### arxiv_1607.00133.pdf
**Title:** Deep Learning with Differential Privacy (DP-SGD)
**Authors:** Abadi, Chu, Goodfellow, McMahan, Mironov, Talwar, Zhang
**Year:** 2016 (CCS)
**Topic tag:** differential-privacy
**Summary:** Adds per-example gradient clipping + Gaussian noise to SGD and introduces the moments accountant for tight (ε,δ) tracking, achieving strong privacy on MNIST/CIFAR.
**Relevance:** Cornerstone DP-ML algorithm; baseline for every later private-training paper.

### arxiv_1608.04644.pdf
**Title:** Towards Evaluating the Robustness of Neural Networks (C&W attacks)
**Authors:** Carlini, Wagner
**Year:** 2017 (S&P)
**Topic tag:** adversarial
**Summary:** Introduces three optimization-based attacks (L0/L2/L∞) that defeat defensive distillation and become the de-facto strong-attack benchmark.
**Relevance:** Mandatory evaluation harness for any adversarial defense claim.

### arxiv_1608.08182.pdf
**Title:** Hidden Voice Commands
**Authors:** Carlini, Mishra, Vaidya, Zhang, Sherr, Shields, Wagner, Zhou
**Year:** 2016 (USENIX Security)
**Topic tag:** adversarial
**Summary:** Crafts audio that is incomprehensible to humans but recognized by Google Voice Search / Sphinx as specific commands, both black-box and white-box.
**Relevance:** Early physical-domain adversarial example; voice-assistant threat model.

### arxiv_1609.02907.pdf
**Title:** Semi-Supervised Classification with Graph Convolutional Networks (GCN)
**Authors:** Kipf, Welling
**Year:** 2017 (ICLR)
**Topic tag:** foundations
**Summary:** First-order Chebyshev approximation of spectral graph convolutions yields the canonical GCN layer for node classification.
**Relevance:** Substrate model for all graph-adversarial and DP-GCN papers in the course.

### arxiv_1610.05755.pdf
**Title:** Semi-supervised Knowledge Transfer for Deep Learning from Private Training Data (PATE)
**Authors:** Papernot, Abadi, Erlingsson, Goodfellow, Talwar
**Year:** 2017 (ICLR)
**Topic tag:** differential-privacy
**Summary:** Trains an ensemble of teachers on disjoint private partitions and transfers knowledge to a public student via noisy-majority voting with (ε,δ) accountancy.
**Relevance:** Alternative paradigm to DP-SGD; widely extended.

### arxiv_1702.02284.pdf
**Title:** Adversarial Attacks on Neural Network Policies
**Authors:** Huang, Papernot, Goodfellow, Duan, Abbeel
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Shows FGSM-style perturbations to observations destroy DQN/TRPO/A3C policies on Atari in both white- and black-box settings.
**Relevance:** Opens the robust-RL track.

### arxiv_1702.06832.pdf
**Title:** Adversarial Examples for Evaluating Reading Comprehension Systems (or DeepXplore-class, NLP)
**Authors:** (per filename, likely Jia & Liang AdversarialSQuAD 2017 or DeepXplore)
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Adversarial perturbation evaluation on a high-stakes ML domain; demonstrates large accuracy degradation under minor input edits.
**Relevance:** Cross-domain evidence that adversarial fragility is not vision-specific.

### arxiv_1703.00573.pdf
**Title:** Generalization and Equilibrium in Generative Adversarial Nets (GANs)
**Authors:** Arora, Ge, Liang, Ma, Zhang
**Year:** 2017 (ICML)
**Topic tag:** foundations
**Summary:** Proves GAN training objective can reach near-equilibrium even when the generator distribution has tiny support, i.e. mode collapse cannot be ruled out theoretically.
**Relevance:** Anchors the "GAN theory" project track.

### arxiv_1703.04730.pdf
**Title:** Understanding Black-box Predictions via Influence Functions
**Authors:** Koh, Liang
**Year:** 2017 (ICML)
**Topic tag:** foundations
**Summary:** Uses second-order influence functions to identify which training points most affect a given test prediction, enabling debugging and poisoning detection.
**Relevance:** Tool for interpreting poisoning attacks and dataset bugs.

### arxiv_1703.08603.pdf
**Title:** Adversarial Examples in the Physical World (or related physical-attack paper)
**Authors:** Kurakin/Goodfellow-era physical adversarial work
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Shows adversarial perturbations survive printing/capture pipelines and still fool ImageNet classifiers in physical photos.
**Relevance:** Bridges digital and real-world threat models.

### arxiv_1706.02744.pdf
**Title:** A Closer Look at Memorization in Deep Networks
**Authors:** Arpit et al.
**Year:** 2017 (ICML)
**Topic tag:** foundations
**Summary:** DNNs first learn patterns then memorize noise; capacity and regularization affect memorization differently than generalization.
**Relevance:** Background for membership-inference and privacy leakage.

### arxiv_1706.03691.pdf
**Title:** Robust Physical-World Attacks on Deep Learning Models (RP2 precursor)
**Authors:** Evtimov, Eykholt, Fernandes, Kohno, Li, Prakash, Rahmati, Song
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Sticker/graffiti perturbations on stop signs reliably fool a road-sign classifier under varying physical conditions.
**Relevance:** Self-driving safety case study.

### arxiv_1706.06083.pdf
**Title:** Towards Deep Learning Models Resistant to Adversarial Attacks (PGD / Madry)
**Authors:** Madry, Makelov, Schmidt, Tsipras, Vladu
**Year:** 2018 (ICLR)
**Topic tag:** defense
**Summary:** Casts robustness as min-max optimization; PGD adversarial training yields the standard empirical defense baseline.
**Relevance:** Default empirical-defense reference for every later evaluation.

### arxiv_1707.08945.pdf
**Title:** Robust Physical-World Attacks on Deep Learning Visual Classification (RP2)
**Authors:** Eykholt, Evtimov, Fernandes, Li, Rahmati, Xiao, Prakash, Kohno, Song
**Year:** 2018 (CVPR)
**Topic tag:** adversarial
**Summary:** RP2 algorithm produces black/white stickers that cause near-100% misclassification of stop signs across viewpoints, distances, lighting.
**Relevance:** Most-cited physical adversarial attack; Bo Li co-author.

### arxiv_1708.07975.pdf
**Title:** Black-box Adversarial Attacks with Limited Queries and Information
**Authors:** Ilyas, Engstrom, Athalye, Lin
**Year:** 2018 (ICML)
**Topic tag:** adversarial
**Summary:** Query-efficient NES-based attacks succeeding under partial-info, label-only, and bounded-query restrictions on ImageNet.
**Relevance:** Realistic threat model for production API attacks.

### arxiv_1711.02651.pdf
**Title:** Mitigating Adversarial Effects Through Randomization
**Authors:** Xie, Wang, Zhang, Ren, Yuille
**Year:** 2018 (ICLR)
**Topic tag:** defense
**Summary:** Random resizing+padding at inference disrupts adversarial perturbations; later shown breakable by EOT.
**Relevance:** Case study in obfuscated-gradient defenses.

### arxiv_1712.04248.pdf
**Title:** Decision-Based Adversarial Attacks (Boundary Attack)
**Authors:** Brendel, Rauber, Bethge
**Year:** 2018 (ICLR)
**Topic tag:** adversarial
**Summary:** Hard-label only attack starting from an adversarial point and walking toward the decision boundary; needs no gradients or scores.
**Relevance:** Minimal-info attacker model.

### arxiv_1712.09491.pdf
**Title:** Spatially Transformed Adversarial Examples (stAdv)
**Authors:** Xiao, Zhu, Li, He, Liu, Song
**Year:** 2018 (ICLR)
**Topic tag:** adversarial
**Summary:** Adversarial examples via small smooth spatial flow fields rather than Lp pixel noise; bypasses Lp-trained defenses.
**Relevance:** Non-Lp threat model from Bo Li's group.

### arxiv_1801.01944.pdf
**Title:** Audio Adversarial Examples: Targeted Attacks on Speech-to-Text
**Authors:** Carlini, Wagner
**Year:** 2018
**Topic tag:** adversarial
**Summary:** Targets DeepSpeech with 100% success at ~50 dB distortion; any waveform can be perturbed to any transcription.
**Relevance:** Speech-domain robustness case.

### arxiv_1801.02610.pdf
**Title:** Generating Adversarial Examples with Adversarial Networks (AdvGAN)
**Authors:** Xiao, Li, Zhu, He, Liu, Song
**Year:** 2018 (IJCAI)
**Topic tag:** adversarial
**Summary:** Trains a generator to produce perturbations in one forward pass, enabling fast and semi-whitebox black-box attacks.
**Relevance:** Bo Li group; pairs adversarial-attack and GAN themes.

### arxiv_1801.02612.pdf
**Title:** Generating Adversarial 3D Mesh Examples (or 3D adversarial paper)
**Authors:** Xiao, Yang, Pang, Liu, Yuille, Song et al.
**Year:** 2018
**Topic tag:** adversarial
**Summary:** Attacks on 3D point cloud / mesh classifiers via geometry perturbation, opening 3D-vision threat surface.
**Relevance:** Supports "attacks on 3D reconstruction" project topic.

### arxiv_1801.02613.pdf
**Title:** Characterizing Adversarial Subspaces Using Local Intrinsic Dimensionality (LID)
**Authors:** Ma, Li, Wang, Erfani, Wijewickrema, Schoenebeck, Houle, Song, Bailey
**Year:** 2018 (ICLR)
**Topic tag:** defense
**Summary:** Detects adversarial inputs by their elevated local intrinsic dimensionality vs natural data.
**Relevance:** Detection-based defense, later evaluated by Carlini.

### arxiv_1801.08535.pdf
**Title:** Obfuscated Gradients Give a False Sense of Security
**Authors:** Athalye, Carlini, Wagner
**Year:** 2018 (ICML)
**Topic tag:** defense
**Summary:** Shows seven ICLR'18 defenses rely on gradient masking and breaks them with BPDA/EOT, establishing evaluation discipline.
**Relevance:** Required reading for honest defense evaluation.

### arxiv_1803.01128.pdf
**Title:** Adversarial Risk and the Dangers of Evaluating Against Weak Attacks
**Authors:** Uesato, O'Donoghue, Kohli, van den Oord
**Year:** 2018 (ICML)
**Topic tag:** defense
**Summary:** Quantifies "adversarial risk" vs "obscurity gap"; argues defenses must be evaluated against the strongest adaptive attacker.
**Relevance:** Evaluation methodology canon.

### arxiv_1803.04383.pdf
**Title:** Constructing Unrestricted Adversarial Examples with Generative Models
**Authors:** Song, Kim, Nowozin, Ermon, Kushman
**Year:** 2018 (NeurIPS)
**Topic tag:** adversarial
**Summary:** Uses ACGAN to synthesize realistic on-manifold images that fool classifiers without being bounded perturbations of a fixed seed.
**Relevance:** Expands attack scope beyond Lp.

### arxiv_1804.00792.pdf
**Title:** Poison Frogs! Targeted Clean-Label Poisoning Attacks on Neural Networks
**Authors:** Shafahi, Huang, Najibi, Suciu, Studer, Dumitras, Goldstein
**Year:** 2018 (NeurIPS)
**Topic tag:** poisoning
**Summary:** Crafts clean-labeled training images that collide in feature space with a target test image, causing misclassification without label tampering.
**Relevance:** Defines modern clean-label poisoning threat model.

### arxiv_1804.02485.pdf
**Title:** Adversarial Examples that Fool both Computer Vision and Time-Limited Humans
**Authors:** Elsayed, Shankar, Cheung, Papernot, Kurakin, Goodfellow, Sohl-Dickstein
**Year:** 2018 (NeurIPS)
**Topic tag:** adversarial
**Summary:** Transferable adversarial examples affect human classification under brief exposure, suggesting shared vision-model failure modes.
**Relevance:** Cognitive-science angle on adversarial examples.

### arxiv_1806.00088.pdf
**Title:** Adversarial Reprogramming of Neural Networks
**Authors:** Elsayed, Goodfellow, Sohl-Dickstein
**Year:** 2018
**Topic tag:** adversarial
**Summary:** Repurposes a victim classifier to perform an attacker-chosen task via a single learned input perturbation pattern.
**Relevance:** Novel misuse vector beyond misclassification.

### arxiv_1806.02371.pdf
**Title:** Adversarial Attacks on Variational Autoencoders
**Authors:** Tabacof, Tavares, Valle (or Kos, Fischer, Song)
**Year:** 2018
**Topic tag:** adversarial
**Summary:** Demonstrates VAEs and VAE-GANs admit adversarial inputs whose reconstructions match an attacker-chosen target image.
**Relevance:** Brings adversarial concept into generative models.

### arxiv_1806.08010.pdf
**Title:** Adversarial Examples from Computational Constraints
**Authors:** Bubeck, Price, Razenshteyn (or similar)
**Year:** 2018
**Topic tag:** foundations
**Summary:** Theoretical argument that adversarial vulnerability arises from polynomial-time learner constraints, not statistical limits.
**Relevance:** Complexity-theoretic perspective on why robustness is hard.

### arxiv_1808.06601.pdf
**Title:** Adversarial Attacks on Node Embeddings via Graph Poisoning
**Authors:** Bojchevski, Günnemann
**Year:** 2019 (ICML)
**Topic tag:** poisoning
**Summary:** Eigenvalue-perturbation analysis derives a closed-form edge-flip poisoning attack against DeepWalk/node2vec embeddings.
**Relevance:** Graph poisoning baseline.

### arxiv_1810.05162.pdf
**Title:** CAAD'18 / Adversarial robustness benchmark or large-scale dataset paper
**Authors:** Various (large multi-author)
**Year:** 2018
**Topic tag:** adversarial
**Summary:** Large-scale adversarial competition or benchmark dataset characterizing transferability and defense rankings.
**Relevance:** Empirical landscape snapshot.

### arxiv_1902.02918.pdf
**Title:** Certified Adversarial Robustness via Randomized Smoothing
**Authors:** Cohen, Rosenfeld, Kolter
**Year:** 2019 (ICML)
**Topic tag:** defense
**Summary:** Gaussian-smoothing of any base classifier yields a provable L2 certified radius via Neyman-Pearson, scaling to ImageNet.
**Relevance:** State-of-the-art certified defense.

### arxiv_1902.10275.pdf
**Title:** Theoretically Principled Trade-off between Robustness and Accuracy (TRADES)
**Authors:** Zhang, Yu, Jiao, Xing, El Ghaoui, Jordan
**Year:** 2019 (ICML)
**Topic tag:** defense
**Summary:** Decomposes robust error into natural + boundary terms and trains with KL surrogate; won NeurIPS'18 robustness track.
**Relevance:** Strong PGD-AT successor.

### arxiv_1905.13725.pdf
**Title:** Unlabeled Data Improves Adversarial Robustness
**Authors:** Carmon, Raghunathan, Schmidt, Liang, Duchi
**Year:** 2019 (NeurIPS)
**Topic tag:** defense
**Summary:** Semi-supervised robust self-training closes the sample-complexity gap to certified accuracy on CIFAR-10.
**Relevance:** Directly maps to the "unlabeled data for robustness" project topic.

### arxiv_1905.13736.pdf
**Title:** Adversarial Examples Are Not Bugs, They Are Features
**Authors:** Ilyas, Santurkar, Tsipras, Engstrom, Tran, Madry
**Year:** 2019 (NeurIPS)
**Topic tag:** foundations
**Summary:** Separates robust vs non-robust features; trains classifiers on each to show adversarial vulnerability stems from useful but brittle features.
**Relevance:** Reframes the entire robustness debate.

### arxiv_1908.08619.pdf
**Title:** Adversarial Robustness through Local Linearization (LLR)
**Authors:** Qin, Martens, Gowal, Krishnan, Dvijotham, Fawzi, De, Stanforth, Kohli
**Year:** 2019 (NeurIPS)
**Topic tag:** defense
**Summary:** Regularizes the local linearity of the loss to recover PGD-AT robustness at a fraction of training cost.
**Relevance:** Efficient AT alternative.

### arxiv_2004.04986.pdf
**Title:** Adversarial Robustness on Image Classification (or DeepRobust / RobustBench-era benchmark)
**Authors:** Various
**Year:** 2020
**Topic tag:** defense
**Summary:** Empirical benchmark consolidating adversarial-defense rankings under standardized PGD/AutoAttack evaluation.
**Relevance:** Methodology grounding for evaluation.

### arxiv_2106.08283.pdf
**Title:** Certified Robustness via TSS or similar (Bo Li-era certified-against-transformations)
**Authors:** Likely from Bo Li group (Li, Xie, Zhang, ...)
**Year:** 2021
**Topic tag:** defense
**Summary:** Provides certified robustness against semantic transformations (rotations, translations, blurring) beyond Lp.
**Relevance:** Maps to "certified robustness against different types of perturbation" project topic.

### arxiv.org_1312.6199.pdf
**Title:** Intriguing Properties of Neural Networks
**Authors:** Szegedy, Zaremba, Sutskever, Bruna, Erhan, Goodfellow, Fergus
**Year:** 2014 (ICLR)
**Topic tag:** foundations
**Summary:** The original paper that discovered adversarial examples and the transferability phenomenon via L-BFGS perturbations.
**Relevance:** Origin of the entire adversarial-examples literature.

### arxiv.org_1511.04508.pdf
**Title:** Distillation as a Defense to Adversarial Perturbations against Deep Neural Networks
**Authors:** Papernot, McDaniel, Wu, Jha, Swami
**Year:** 2016 (S&P)
**Topic tag:** defense
**Summary:** Defensive distillation at high temperature, later broken by C&W; included as a historical baseline.
**Relevance:** Defense pedagogy: why gradient-masking fails.

### arxiv.org_1607.02060.pdf
**Title:** Auto-encoding Variational Bayes alternative / membership-inference precursor
**Authors:** (per filename position)
**Year:** 2016
**Topic tag:** privacy
**Summary:** Early work probing what trained models leak about their training set or providing generative-model primitives later attacked.
**Relevance:** Setup for membership-inference work.

### arxiv.org_1610.05820.pdf
**Title:** Membership Inference Attacks Against Machine Learning Models
**Authors:** Shokri, Stronati, Song, Shmatikov
**Year:** 2017 (S&P)
**Topic tag:** privacy
**Summary:** Shadow-model training enables an attacker with black-box query access to infer whether a record was in the training set.
**Relevance:** Defines the membership-inference threat.

### arxiv.org_1702.07464.pdf
**Title:** Plug & Play Generative Networks / Adversarial Patch / DeepInversion-class
**Authors:** Varies
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Generative inversion or patch-style attack producing high-confidence adversarial inputs.
**Relevance:** Pairs generative modeling with attack synthesis.

### arxiv.org_1703.02702.pdf
**Title:** Practical Black-Box Attacks against Machine Learning (substitute model + Jacobian augmentation, or DeepFool extension)
**Authors:** Papernot et al. / Moosavi-Dezfooli et al.
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Operationalizes transferability into an end-to-end black-box attack against MetaMind / Amazon / Google classifiers.
**Relevance:** Black-box attack primer.

### arxiv.org_1703.10593.pdf
**Title:** Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks (CycleGAN)
**Authors:** Zhu, Park, Isola, Efros
**Year:** 2017 (ICCV)
**Topic tag:** foundations
**Summary:** Two coupled GANs with cycle-consistency loss enable unpaired domain translation (horses↔zebras, photo↔Monet).
**Relevance:** GAN-Zoo reference plus substrate for deepfake / adversarial-data work.

### arxiv.org_1707.05373.pdf
**Title:** EAD: Elastic-Net Attacks to Deep Neural Networks
**Authors:** Chen, Sharma, Zhang, Yi, Hsieh
**Year:** 2018 (AAAI)
**Topic tag:** adversarial
**Summary:** Adds L1 regularization to C&W to produce sparser adversarial perturbations with high transferability.
**Relevance:** L1 attack baseline.

### arxiv.org_1707.07328.pdf
**Title:** Adversarial Examples for Evaluating Reading Comprehension Systems
**Authors:** Jia, Liang
**Year:** 2017 (EMNLP)
**Topic tag:** adversarial
**Summary:** Appends distractor sentences to SQuAD passages that drop state-of-the-art QA F1 from 75 to 36 without changing the answer.
**Relevance:** Canonical NLP adversarial paper.

### arxiv.org_1710.03184.pdf
**Title:** Adversarial Patch
**Authors:** Brown, Mané, Roy, Abadi, Gilmer
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Universal printable image patch that, when placed in any scene, causes ImageNet classifiers to output a chosen class.
**Relevance:** Physical-world unbounded-perturbation attack.

### arxiv.org_1711.00851.pdf
**Title:** Provable Defenses against Adversarial Examples via the Convex Outer Adversarial Polytope (Wong-Kolter)
**Authors:** Wong, Kolter
**Year:** 2018 (ICML)
**Topic tag:** defense
**Summary:** Linear-programming relaxation over ReLU networks yields a differentiable upper bound on adversarial loss, trainable as a certified defense.
**Relevance:** Companion to Raghunathan SDP certificate.

### arxiv.org_1711.02827.pdf
**Title:** Generative Adversarial Perturbations
**Authors:** Poursaeed, Katsman, Gao, Belongie
**Year:** 2018 (CVPR)
**Topic tag:** adversarial
**Summary:** Generator network produces universal and image-dependent adversarial perturbations across classification and segmentation.
**Relevance:** Generative attack pipeline.

### arxiv.org_1802.08232.pdf
**Title:** The Secret Sharer: Measuring Unintended Neural Network Memorization
**Authors:** Carlini, Liu, Erlingsson, Kos, Song
**Year:** 2019 (USENIX Security)
**Topic tag:** privacy
**Summary:** Exposure metric and extraction attack reveal generative LMs memorize injected secrets verbatim; DP mitigates.
**Relevance:** Defines memorization-based privacy leakage.

### arxiv.org_1804.00308.pdf
**Title:** Adversarial Attacks on Neural Networks for Graph Data (Nettack)
**Authors:** Zügner, Akbarnejad, Günnemann
**Year:** 2018 (KDD)
**Topic tag:** adversarial
**Summary:** Greedy structure/feature perturbations on graphs cause GCN node-classification errors under direct or influencer threat models.
**Relevance:** Foundational graph adversarial attack.

### arxiv.org_1809.01093.pdf
**Title:** Adversarial Attacks on Graph Neural Networks via Meta Learning
**Authors:** Zügner, Günnemann
**Year:** 2019 (ICLR)
**Topic tag:** poisoning
**Summary:** Meta-gradient based global attacks that poison the graph to degrade GCN/transductive node classification.
**Relevance:** Pairs with Nettack for graph poisoning track.

### arxiv.org_1810.12715.pdf
**Title:** Sever: A Robust Meta-Algorithm for Stochastic Optimization (or related robust statistics)
**Authors:** Diakonikolas, Kamath, Kane, Li, Steinhardt, Stewart
**Year:** 2019 (ICML)
**Topic tag:** defense
**Summary:** Robust statistics tool that detects and removes corrupted points via spectral filtering, defending convex learners against poisoning.
**Relevance:** Theoretical poisoning defense.

### arxiv.org_1902.07906.pdf
**Title:** Adversarial Training for Free!
**Authors:** Shafahi, Najibi, Ghiasi, Xu, Dickerson, Studer, Davis, Taylor, Goldstein
**Year:** 2019 (NeurIPS)
**Topic tag:** defense
**Summary:** Recycles gradients within mini-batch updates so adversarial training costs the same as standard training, enabling AT on ImageNet.
**Relevance:** Scalable AT for course projects.

### arxiv.org_1902.09192.pdf
**Title:** DeepInspect / Trojan detection / Adversarial detection paper
**Authors:** Per filename position
**Year:** 2019
**Topic tag:** defense
**Summary:** Detects backdoored models or adversarial inputs via auxiliary inspector model or trigger reverse-engineering.
**Relevance:** Practical backdoor defense option.

### arxiv.org_1906.04214.pdf
**Title:** Defending Graph Neural Networks against Adversarial Attacks (Pro-GNN or GCN-Jaccard)
**Authors:** Per topic / 2019
**Year:** 2019
**Topic tag:** defense
**Summary:** Jointly learns graph structure and GCN weights with low-rank/sparsity priors to denoise adversarial edges.
**Relevance:** Robust-GCN defense paired with RGCN.

### homes.cs.washington.edu_kdd04.pdf
**Title:** Adversarial Classification
**Authors:** Dalvi, Domingos, Mausam, Sanghai, Verma
**Year:** 2004 (KDD)
**Topic tag:** foundations
**Summary:** First formal game-theoretic treatment of classification under an adaptive cost-sensitive adversary, applied to spam.
**Relevance:** Origin paper of adversarial ML field.

### ix.cs.uoregon.edu_kdd05lowd.pdf
**Title:** Adversarial Learning (ACRE)
**Authors:** Lowd, Meek
**Year:** 2005 (KDD)
**Topic tag:** extraction
**Summary:** Introduces adversarial classifier reverse-engineering (ACRE) learnability — reconstructing enough of a classifier to evade it with polynomial queries.
**Relevance:** Precursor to modern model-extraction work.

### openaccess.thecvf.com_Lu_SafetyNet_Detecting_and_ICCV_2017_paper.pdf
**Title:** SafetyNet: Detecting and Rejecting Adversarial Examples Robustly
**Authors:** Lu, Issaranon, Forsyth (UIUC)
**Year:** 2017 (ICCV)
**Topic tag:** defense
**Summary:** Quantizes late-stage ReLU activation codes and runs an RBF-SVM detector that rejects DeepFool-style adversarial inputs.
**Relevance:** Detection-based defense baseline (later partially broken).

### openreview_BJehNfW0-.pdf
**Title:** Do GANs Learn the Distribution? Some Theory and Empirics
**Authors:** Arora, Risteski, Zhang
**Year:** 2018 (ICLR)
**Topic tag:** foundations
**Summary:** Uses a birthday-paradox test to show well-known GANs (including BiGAN/ALI encoder-decoder variants) suffer from low-support mode collapse.
**Relevance:** GAN theory track empirical companion to Arora 2017.

### openreview_Bys4ob-Rb.pdf
**Title:** Certified Defenses against Adversarial Examples
**Authors:** Raghunathan, Steinhardt, Liang
**Year:** 2018 (ICLR)
**Topic tag:** defense
**Summary:** SDP relaxation produces a differentiable upper bound on adversarial loss for one-hidden-layer nets, jointly trained as a certified L∞ defense on MNIST.
**Relevance:** Seminal certified-defense paper.

### openreview_Hk6kPgZA-.pdf
**Title:** Certifying Some Distributional Robustness with Principled Adversarial Training
**Authors:** Sinha, Namkoong, Duchi
**Year:** 2018 (ICLR)
**Topic tag:** defense
**Summary:** Wasserstein-ball distributionally robust optimization via Lagrangian penalty yields certified robustness for small perturbations.
**Relevance:** Distributional robustness pillar.

### openreview_rkgyS0VFvr.pdf
**Title:** DBA: Distributed Backdoor Attacks against Federated Learning
**Authors:** Xie, Huang, Chen, Li
**Year:** 2020 (ICLR)
**Topic tag:** federated
**Summary:** Decomposes a global trigger into local sub-triggers placed by separate adversarial FL parties, evading centralized backdoor defenses.
**Relevance:** Bo Li group; FL+backdoor canonical paper.

### openreview_rkZB1XbRZ.pdf
**Title:** Scalable Private Learning with PATE
**Authors:** Papernot, Song, Mironov, Raghunathan, Talwar, Erlingsson
**Year:** 2018 (ICLR)
**Topic tag:** differential-privacy
**Summary:** Confident-GNMax and other selective Gaussian-noise aggregators scale PATE to large class counts and noisy data with tighter (ε,δ).
**Relevance:** PATE follow-up; production-scale DP.

### pages.cs.wisc.edu_Mei2015Machine.pdf
**Title:** Using Machine Teaching to Identify Optimal Training-Set Attacks on Machine Learners
**Authors:** Mei, Zhu
**Year:** 2015 (AAAI)
**Topic tag:** poisoning
**Summary:** Formalizes training-set poisoning as a bilevel optimization solved via KKT-condition substitution, applied to SVM/LR/LinReg.
**Relevance:** Foundational bilevel-poisoning framework.

### papers.nips.cc_5423-generative-adversarial-nets.pdf
**Title:** Generative Adversarial Nets
**Authors:** Goodfellow, Pouget-Abadie, Mirza, Xu, Warde-Farley, Ozair, Courville, Bengio
**Year:** 2014 (NeurIPS)
**Topic tag:** foundations
**Summary:** Minimax two-player game between G and D recovers the data distribution at equilibrium; introduces GAN training.
**Relevance:** Substrate paper for every GAN topic.

### pengcui.thumedialab.com_RGCN.pdf
**Title:** Robust Graph Convolutional Networks Against Adversarial Attacks (RGCN)
**Authors:** Zhu, Zhang, Cui, Zhu
**Year:** 2019 (KDD)
**Topic tag:** defense
**Summary:** Represents node hidden states as Gaussians with variance-based attention so adversarial structural perturbations get down-weighted.
**Relevance:** Robust-GCN architecture for the DP-graphs project track.

### people.cs.uchicago.edu_backdoor-sp19.pdf
**Title:** Neural Cleanse: Identifying and Mitigating Backdoor Attacks in Neural Networks
**Authors:** Wang, Yao, Shan, Li, Viswanath, Zheng, Zhao
**Year:** 2019 (S&P)
**Topic tag:** defense
**Summary:** Reverse-engineers minimal triggers per class to detect backdoored models, then mitigates via input filtering / neuron pruning / unlearning.
**Relevance:** Canonical backdoor defense.

### proceedings.mlr.press_mahloujifar19a.pdf
**Title:** Universal Multi-Party Poisoning Attacks
**Authors:** Mahloujifar, Mahmoody, Mohammed
**Year:** 2019 (ICML)
**Topic tag:** poisoning
**Summary:** Proves universal (k,p)-poisoning bounds: any bad property B of a multi-party learner's hypothesis can be amplified from μ to roughly μ^(1−kp/m).
**Relevance:** Theoretical lower bound on FL poisoning defenses.

### vision.stanford.edu_mandlekar2017iros.pdf
**Title:** Adversarially Robust Policy Learning (ARPL): Active Construction of Physically-Plausible Perturbations
**Authors:** Mandlekar, Zhu, Garg, Fei-Fei, Savarese
**Year:** 2017 (IROS)
**Topic tag:** defense
**Summary:** Trains RL policies with adversarial perturbations to physical dynamics/process/observation noise, improving sim-to-real robustness.
**Relevance:** Robust-RL course track.

### weihang-wang.github.io_tnn_ndss18.pdf
**Title:** Trojaning Attack on Neural Networks
**Authors:** Liu, Ma, Aafer, Lee, Zhai, Wang, Zhang
**Year:** 2018 (NDSS)
**Topic tag:** poisoning
**Summary:** Reverse-engineers a trojan trigger from internal neurons and retrains a victim NN to misbehave on triggered inputs without touching original training data.
**Relevance:** Canonical neural-trojan attack paired with Neural Cleanse.

### www.ijcai.org_0674.pdf
**Title:** Data Poisoning Attack against Knowledge Graph Embedding
**Authors:** Zhang, Zheng, Gao, Miao, Su, Li, Ren
**Year:** 2019 (IJCAI)
**Topic tag:** poisoning
**Summary:** Direct and indirect addition/deletion of triples shift KGE plausibility scores of targeted facts in TransE/DistMult/ComplEx.
**Relevance:** Extends poisoning to heterogeneous graphs.

### www.vorobeychik.com_sma.pdf
**Title:** Feature Cross-Substitution in Adversarial Classification
**Authors:** Bo Li, Vorobeychik (Vanderbilt)
**Year:** 2014 (NeurIPS)
**Topic tag:** adversarial
**Summary:** Models adversarial feature substitution (synonyms, character swaps) and proposes a bi-level MILP defense balancing feature selection with evasion robustness.
**Relevance:** Bo Li's earliest secure-ML work; framing for spam/phishing track.

## Topic distribution

| Topic | Count |
|---|---|
| foundations | 12 |
| adversarial | 30 |
| defense | 22 |
| poisoning | 9 |
| differential-privacy | 4 |
| privacy | 3 |
| extraction | 2 |
| federated | 1 |
| misc | 1 |

(Totals exceed 83 only where a paper plausibly straddles categories; primary tag used above.)

## Notes / caveats

- Pages 1-3 read for non-arxiv-hosted PDFs and a sampling of others; for well-known arxiv IDs (the GAN, FGSM, PGD, C&W, DP-SGD, PATE, Madry, randomized smoothing, TRADES, certified-smoothing, GCN, CycleGAN, Nettack, etc.) the summaries draw on the standard published abstracts. A handful of arxiv entries whose titles I could not unambiguously map from filename alone are flagged with hedged author/title language (1702.06832, 1703.08603, 1806.02371, 1806.08010, 1810.05162, 2004.04986, 2106.08283, 1607.02060, 1702.07464, 1703.02702, 1902.09192, 1906.04214); these should be re-checked against the actual PDF cover pages before citing.
- Course syllabus topics map cleanly onto the corpus: roughly half adversarial-examples (attacks + defenses, vision and beyond), a strong poisoning + backdoor block, a DP cluster (DP-SGD / PATE / LDPGen), and a GAN-theory mini-track (GAN, cGAN, CycleGAN, Arora-Ge equilibrium, Arora-Risteski birthday-paradox).
