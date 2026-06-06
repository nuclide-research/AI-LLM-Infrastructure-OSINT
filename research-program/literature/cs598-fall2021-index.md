# CS 598 (Fall 2021) — Graduate Adversarial ML Course Index

**Instructor:** Bo Li (UIUC)
**Course path:** ~/Documents/cs598-aisecure/
**Total PDFs indexed:** 126

## Syllabus

Bo Li's Fall 2021 graduate seminar on Advanced Topics in Security, Privacy and Machine Learning (cross-listed CS 562 / CS 598). TA: Huichen Li. Grading is 65% project (proposal + status + final report due Dec 5), 30% paper reading + presentation + reviews, 5% participation. Prereqs: prior ML coursework and ability to train NNs with TensorFlow/PyTorch. Stated goal: every group should produce one top-tier conference paper. Candidate project topics include attacks on 3D / BERT / RL, deepfake detection, poisoning robustness, certified robustness against Lp and non-Lp perturbations, GAN theory, differentially-private and robust GNNs, robust RL, semi-supervised robustness, robust AutoML, and safety-critical scenario generation in CARLA. Reading list lives at aisecure.github.io/TEACHING/CS562/CS562.html.

## Papers / lectures

### aisecure.github.io_TEACHING_CS598_Fall2021_files_syllabus.pdf

**Title:** Syllabus: CS 562. Advanced Topics in Security, Privacy and Machine Learning
**Authors:** Bo Li (instructor), Huichen Li (TA)
**Year:** 2021
**Topic tag:** misc
**Summary:** Course syllabus — grading breakdown, prereqs, 15 candidate project topics centered on attacks, defenses, certified robustness, privacy, and GAN theory.
**Relevance:** Frames the canonical AdvML topic taxonomy NuClide assesses against in the wild.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_lecture0825.pdf

**Title:** Course intro / Course logistics (lecture 1)
**Authors:** Bo Li
**Year:** 2021
**Topic tag:** misc
**Summary:** Opening lecture — course mechanics and motivation.
**Relevance:** Not directly relevant — administrative.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_lecture0826.pdf

**Title:** Adversarial ML overview (lecture 2)
**Authors:** Bo Li
**Year:** 2021
**Topic tag:** adversarial
**Summary:** Introduces the AdvML threat model and the attacks/defenses landscape.
**Relevance:** Sets baseline vocabulary for AdvML reasoning we apply during AI-infra assessments.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_lecture0831.pdf

**Title:** Evasion attacks against ML models (non-traditional attacks)
**Authors:** Bo Li
**Year:** 2021
**Topic tag:** adversarial
**Summary:** Survey of GAN-based, spatially-transformed, Wasserstein, and physical-world evasion attacks.
**Relevance:** Non-Lp attack surfaces matter when emulating realistic adversaries against deployed models.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_lecture0907.pdf

**Title:** Evasion against ML — FGSM/CW/PGD/BIM/Deepfool/JSMA + physical attacks (lecture)
**Authors:** Bo Li
**Year:** 2021
**Topic tag:** adversarial
**Summary:** Canonical white-box attack methods plus physical-world attacks; intrinsic vs extrinsic defenses framing.
**Relevance:** Baseline attack toolkit relevant to any robustness-claim verification.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_lecture0909.pdf

**Title:** Evasion black-box attacks (lecture)
**Authors:** Bo Li
**Year:** 2021
**Topic tag:** adversarial
**Summary:** Transferability, query-based, decision-boundary attacks against black-box ML.
**Relevance:** Black-box query attacks map directly to model-extraction surface on exposed inference endpoints.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_lecture0914.pdf

**Title:** Adversarial attacks against general ML (object detectors, segmentation, GANs, RL) (lecture)
**Authors:** Bo Li
**Year:** 2021
**Topic tag:** adversarial
**Summary:** Extends evasion to detectors, segmentation, pose estimation, generative models, and RL observation/action/reward manipulation.
**Relevance:** Generalizes attacks to non-classifier modalities — applicable to deployed multi-modal AI services.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_lecture0916.pdf

**Title:** Detection against adversarial attacks (lecture)
**Authors:** Bo Li
**Year:** 2021
**Topic tag:** defense
**Summary:** Pre-processing, classifier-based detectors, spatial/temporal consistency, manifold-distance detection.
**Relevance:** Establishes what defenses we should expect — and often fail to find — on production AI endpoints.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_lecture0921.pdf

**Title:** Defense against adversarial attacks — empirical (lecture)
**Authors:** Bo Li
**Year:** 2021
**Topic tag:** defense
**Summary:** PeerNet consistency, defensive distillation, PGD adversarial training; survey of empirical defenses.
**Relevance:** Empirical defenses still dominate production deployments; knowing their failure modes is core.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_class0902.pdf

**Title:** CS 562 — Today's Goal (class 0902)
**Authors:** Bo Li
**Year:** 2021
**Topic tag:** misc
**Summary:** Sets the FGSM/CW/PGD/BIM/Deepfool/JSMA roadmap and project topic discussion.
**Relevance:** Administrative roadmap, not technical content.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_abstract0923.pdf

**Title:** Guest talk — Open the black-box of self-supervised learning
**Authors:** Yuandong Tian (Facebook AI Research)
**Year:** 2021
**Topic tag:** foundations
**Summary:** Theoretical analysis of non-contrastive SSL — why it does not collapse, dimensional collapse, learned features.
**Relevance:** SSL backbones are pervasive in production AI; understanding what they actually learn matters for inversion-attack risk.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_abstract0928.pdf

**Title:** Guest talk — Adversarial, Backdoor and Unlearnable
**Authors:** Xingjun Ma (Deakin University)
**Year:** 2021
**Topic tag:** backdoor
**Summary:** Three ICLR-2021 works — neural attention distillation backdoor defense, channel-wise activation suppression, error-minimizing "unlearnable" examples.
**Relevance:** Backdoor erasure + unlearnable-data techniques are emerging defensive primitives for training-pipeline security.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_abstract1014.pdf

**Title:** Guest talk — How can we trust a black-box? Scalable neural network verifiers
**Authors:** Huan Zhang (CMU)
**Year:** 2021
**Topic tag:** certified-defense
**Summary:** Alpha-beta-CROWN — linear-relaxation + branch-and-bound NN verifier; VNN-COMP 2021 winner.
**Relevance:** Formal verification is the upper bound on robustness claims we encounter in vendor marketing.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_guest1014.pdf

**Title:** Open the black-box of self-supervised learning (slide deck of Tian guest lecture)
**Authors:** Yuandong Tian (FAIR)
**Year:** 2021
**Topic tag:** foundations
**Summary:** Slide deck companion to the SSL guest talk above.
**Relevance:** Same as abstract0923.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_abstract1111.pdf

**Title:** Guest talk — Towards Understanding End-to-end Learning in the Context of Data: ML Dancing over Semirings and Codd's Table
**Authors:** Ce Zhang (ETH Zurich)
**Year:** 2021
**Topic tag:** foundations
**Summary:** Shapley value of training examples, ML over data uncertainty, certifiable backdoor defense, data valuation/cleaning frameworks.
**Relevance:** Data-valuation primitives underpin defenses against poisoning and audit of training-set provenance.

### abstract1111.pdf

**Title:** Duplicate copy of Ce Zhang guest talk abstract (Nov 11)
**Authors:** Ce Zhang
**Year:** 2021
**Topic tag:** foundations
**Summary:** Same content as abstract1111 above.
**Relevance:** Duplicate.

### Student presentations (slides; identifying paper presented where evident)

Student presentation slides — each is a class-presentation deck on an assigned paper. Index gives student + likely paper topic.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1005DominicJones.pdf

**Title:** Student presentation (Dominic Jones, 10/05)
**Authors:** Dominic Jones (presenter)
**Year:** 2021
**Topic tag:** adversarial
**Summary:** Class paper presentation slides — AdvML topic.
**Relevance:** Reflects student-facing topic coverage in the syllabus.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1005Hajder.pdf

**Title:** Student presentation (Hajder, 10/05)
**Authors:** Hajder (presenter)
**Year:** 2021
**Topic tag:** adversarial
**Summary:** Class paper presentation slides.
**Relevance:** Same as above.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1007BerkayKaplan.pdf

**Title:** Student presentation (Berkay Kaplan, 10/07)
**Authors:** Berkay Kaplan
**Year:** 2021
**Topic tag:** adversarial
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1007JaneDu.pdf

**Title:** Student presentation (Jane Du, 10/07)
**Authors:** Jane Du
**Year:** 2021
**Topic tag:** adversarial
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1012WesleyChan.pdf

**Title:** Student presentation (Wesley Chan, 10/12)
**Authors:** Wesley Chan
**Year:** 2021
**Topic tag:** defense
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1019ChunqiuXia.pdf

**Title:** Student presentation (Chunqiu Xia, 10/19)
**Authors:** Chunqiu Xia
**Year:** 2021
**Topic tag:** poisoning
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1019MatthewWeston.pdf

**Title:** Student presentation (Matthew Weston, 10/19)
**Authors:** Matthew Weston
**Year:** 2021
**Topic tag:** poisoning
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1021AdithyaMurali.pdf

**Title:** Student presentation (Adithya Murali, 10/21)
**Authors:** Adithya Murali
**Year:** 2021
**Topic tag:** backdoor
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1021LichengLuo.pdf

**Title:** Student presentation (Licheng Luo, 10/21)
**Authors:** Licheng Luo
**Year:** 2021
**Topic tag:** backdoor
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1026Kung-HsiangHuang.pdf

**Title:** Student presentation (Kung-Hsiang Huang, 10/26)
**Authors:** Kung-Hsiang Huang
**Year:** 2021
**Topic tag:** privacy
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1026QingyunWang.pdf

**Title:** Student presentation (Qingyun Wang, 10/26)
**Authors:** Qingyun Wang
**Year:** 2021
**Topic tag:** privacy
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1028CalvinXu.pdf

**Title:** Student presentation (Calvin Xu, 10/28)
**Authors:** Calvin Xu
**Year:** 2021
**Topic tag:** privacy
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1102ChenhuiZhang.pdf

**Title:** Student presentation (Chenhui Zhang, 11/02)
**Authors:** Chenhui Zhang
**Year:** 2021
**Topic tag:** certified-defense
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1102MuhammadAdilInam.pdf

**Title:** Student presentation (Muhammad Adil Inam, 11/02)
**Authors:** Muhammad Adil Inam
**Year:** 2021
**Topic tag:** certified-defense
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1104VikramDuvvur.pdf

**Title:** Student presentation (Vikram Duvvur, 11/04)
**Authors:** Vikram Duvvur
**Year:** 2021
**Topic tag:** certified-defense
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1109RaginiGupta.pdf

**Title:** Student presentation (Ragini Gupta, 11/09)
**Authors:** Ragini Gupta
**Year:** 2021
**Topic tag:** defense
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1109ZifengWang.pdf

**Title:** Student presentation (Zifeng Wang, 11/09)
**Authors:** Zifeng Wang
**Year:** 2021
**Topic tag:** defense
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1116ZijianHuang.pdf

**Title:** Student presentation (Zijian Huang, 11/16)
**Authors:** Zijian Huang
**Year:** 2021
**Topic tag:** misc
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1118JiaweiZhang.pdf

**Title:** Student presentation (Jiawei Zhang, 11/18)
**Authors:** Jiawei Zhang
**Year:** 2021
**Topic tag:** misc
**Summary:** Class paper presentation slides.
**Relevance:** Student topic coverage.

### aisecure.github.io_TEACHING_CS598_Fall2021_files_student_pres_1130BillTao.pdf

**Title:** Student presentation (Bill Tao, 11/30)
**Authors:** Bill Tao
**Year:** 2021
**Topic tag:** misc
**Summary:** Class paper presentation slides — final session.
**Relevance:** Student topic coverage.

## Reading list — arXiv & venue papers

### arxiv_1206.6389.pdf

**Title:** Poisoning Attacks against Support Vector Machines
**Authors:** Battista Biggio, Blaine Nelson, Pavel Laskov
**Year:** 2012 (ICML)
**Topic tag:** poisoning
**Summary:** Gradient-ascent poisoning attack that crafts malicious training points to maximally degrade an SVM's validation error.
**Relevance:** Foundational poisoning result; the threat model behind every "user-data accepted as training input" concern in modern AI infra.

### arxiv_1411.1784.pdf

**Title:** Conditional Generative Adversarial Nets
**Authors:** Mehdi Mirza, Simon Osindero
**Year:** 2014
**Topic tag:** foundations
**Summary:** Extends GANs with conditional label input to generate class-conditioned samples.
**Relevance:** Not directly relevant — pure ML foundations.

### arxiv_1412.6572.pdf

**Title:** Explaining and Harnessing Adversarial Examples
**Authors:** Ian J. Goodfellow, Jonathon Shlens, Christian Szegedy
**Year:** 2014
**Topic tag:** adversarial
**Summary:** Linear-explanation of adversarial examples and the Fast Gradient Sign Method (FGSM).
**Relevance:** Canonical attack primitive — still the default L_infty probe in NN robustness checks.

### arxiv_1510.05328.pdf

**Title:** Exploring the Space of Adversarial Images
**Authors:** Pedro Tabacof, Eduardo Valle
**Year:** 2015
**Topic tag:** adversarial
**Summary:** L-BFGS bisection search to characterize the geometry of adversarial-image regions in pixel space.
**Relevance:** Pixel-space topology informs whether random-noise defenses are even theoretically sound.

### arxiv_1605.07277.pdf

**Title:** Transferability in Machine Learning: from Phenomena to Black-Box Attacks using Adversarial Samples
**Authors:** Nicolas Papernot, Patrick McDaniel, Ian Goodfellow
**Year:** 2016
**Topic tag:** adversarial
**Summary:** Demonstrates intra- and cross-technique transferability enabling practical black-box attacks via surrogate models.
**Relevance:** Transferability is the load-bearing assumption behind no-query attacks on closed inference endpoints.

### arxiv_1607.00133.pdf

**Title:** Deep Learning with Differential Privacy
**Authors:** Martin Abadi, Andy Chu, Ian Goodfellow, H. Brendan McMahan, Ilya Mironov, Kunal Talwar, Li Zhang
**Year:** 2016 (CCS)
**Topic tag:** privacy
**Summary:** DP-SGD — differentially-private stochastic gradient descent with moments accountant.
**Relevance:** The privacy mechanism every "DP-trained" production claim references; verification means checking the accountant, not the marketing.

### arxiv_1608.04644.pdf

**Title:** Towards Evaluating the Robustness of Neural Networks
**Authors:** Nicholas Carlini, David Wagner
**Year:** 2016
**Topic tag:** adversarial
**Summary:** The Carlini-Wagner (C&W) L_2/L_inf/L_0 attacks; breaks defensive distillation and sets the bar for robustness eval.
**Relevance:** C&W is the standard "is this defense real" probe — relevant whenever a vendor claims adversarial robustness.

### arxiv_1608.08182.pdf

**Title:** Data Poisoning Attacks on Factorization-Based Collaborative Filtering
**Authors:** Bo Li, Yining Wang, Aarti Singh, Yevgeniy Vorobeychik
**Year:** 2016 (NeurIPS)
**Topic tag:** poisoning
**Summary:** Gradient-based poisoning against alternating-minimization and nuclear-norm collaborative filtering, with detection-evading user mimicry.
**Relevance:** Recommender-system poisoning is the prototype for shaping outputs of personalized AI services via user-controlled inputs.

### arxiv_1609.02907.pdf

**Title:** Semi-Supervised Classification with Graph Convolutional Networks
**Authors:** Thomas N. Kipf, Max Welling
**Year:** 2016
**Topic tag:** foundations
**Summary:** GCN — spectral graph convolution for semi-supervised node classification.
**Relevance:** Not directly relevant — pure ML foundations (substrate for many graph-AdvML papers in this corpus).

### arxiv_1610.05755.pdf

**Title:** Semi-supervised Knowledge Transfer for Deep Learning from Private Training Data (PATE)
**Authors:** Nicolas Papernot, Martín Abadi, Úlfar Erlingsson, Ian Goodfellow, Kunal Talwar
**Year:** 2016
**Topic tag:** privacy
**Summary:** Private Aggregation of Teacher Ensembles — train teachers on disjoint sensitive splits, transfer to student via noisy voting.
**Relevance:** Architectural privacy pattern with weaker assumptions than DP-SGD; relevant to multi-tenant model-training disclosures.

### arxiv_1702.02284.pdf

**Title:** Adversarial Attacks on Neural Network Policies
**Authors:** Sandy Huang, Nicolas Papernot, Ian Goodfellow, Yan Duan, Pieter Abbeel
**Year:** 2017
**Topic tag:** adversarial
**Summary:** FGSM-style perturbations on observations of trained RL agents (DQN, TRPO, A3C) cause large policy degradation.
**Relevance:** Observation-channel attack model maps directly to RL-as-a-service and autonomous-system threat surfaces.

### arxiv_1702.06832.pdf

**Title:** Adversarial Examples for Generative Models
**Authors:** Jernej Kos, Ian Fischer, Dawn Song
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Three classes of adversarial attacks on VAE and VAE-GAN — classifier-attached, VAE-loss, latent-distance targeted reconstruction.
**Relevance:** Attacks on generative models are the unseen attack class on image-/video-synthesis pipelines.

### arxiv_1703.00573.pdf

**Title:** Generalization and Equilibrium in Generative Adversarial Nets (GANs)
**Authors:** Sanjeev Arora, Rong Ge, Yingyu Liang, Tengyu Ma, Yi Zhang
**Year:** 2017 (ICML)
**Topic tag:** foundations
**Summary:** Proves GAN training lacks generalization in standard metrics, introduces neural-net distance and MIX+GAN.
**Relevance:** Not directly relevant — GAN theory.

### arxiv_1703.04730.pdf

**Title:** Understanding Black-box Predictions via Influence Functions
**Authors:** Pang Wei Koh, Percy Liang
**Year:** 2017 (ICML)
**Topic tag:** poisoning
**Summary:** Influence functions trace predictions back to most-responsible training points and craft targeted training-set attacks.
**Relevance:** Foundational primitive for poisoning attribution and data-valuation audit on training pipelines.

### arxiv_1703.08603.pdf

**Title:** Adversarial Examples for Semantic Segmentation and Object Detection
**Authors:** Cihang Xie, Jianyu Wang, Zhishuai Zhang, Yuyin Zhou, Lingxi Xie, Alan Yuille
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Dense Adversary Generation (DAG) extends adversarial perturbations to segmentation and detection with cross-task transferability.
**Relevance:** Extends evasion to vision tasks used in autonomous-driving / surveillance AI services.

### arxiv_1706.02744.pdf

**Title:** Avoiding Discrimination through Causal Reasoning
**Authors:** Niki Kilbertus, Mateo Rojas-Carulla, Giambattista Parascandolo, Moritz Hardt, Dominik Janzing, Bernhard Schölkopf
**Year:** 2017 (NeurIPS)
**Topic tag:** misc
**Summary:** Causal fairness criteria — distinguishing protected attributes from their proxies via interventions.
**Relevance:** Not directly relevant — fairness, not security.

### arxiv_1706.03691.pdf

**Title:** Certified Defenses for Data Poisoning Attacks
**Authors:** Jacob Steinhardt, Pang Wei Koh, Percy Liang
**Year:** 2017
**Topic tag:** certified-defense
**Summary:** Approximate upper bounds on worst-case loss for outlier-removal-plus-ERM defenders against data poisoning.
**Relevance:** Establishes how much poisoning a "robust" defender survives — relevant to data-ingestion-trust audits.

### arxiv_1707.08945.pdf

**Title:** Robust Physical-World Attacks on Deep Learning Visual Classification
**Authors:** Kevin Eykholt, Ivan Evtimov, Earlence Fernandes, Bo Li, Amir Rahmati, Chaowei Xiao, Atul Prakash, Tadayoshi Kohno, Dawn Song
**Year:** 2017
**Topic tag:** physical-attack
**Summary:** Physical-world adversarial stickers/graffiti that fool road-sign classifiers under varied conditions (RP2).
**Relevance:** Physical-world attacks are the relevant threat model for deployed CV systems in OT/autonomous contexts.

### arxiv_1708.07975.pdf

**Title:** Plausible Deniability for Privacy-Preserving Data Synthesis
**Authors:** Vincent Bindschaedler, Reza Shokri, Carl A. Gunter
**Year:** 2017
**Topic tag:** privacy
**Summary:** Plausible-deniability criterion for releasing synthetic records — k indistinguishable input records could have produced the output.
**Relevance:** Synthetic-data-as-privacy claims are common in healthcare AI; this is the rigor bar.

### arxiv_1711.02651.pdf

**Title:** Theoretical Limitations of Encoder-Decoder GAN architectures
**Authors:** Sanjeev Arora, Andrej Risteski, Yi Zhang
**Year:** 2017
**Topic tag:** foundations
**Summary:** Proves encoder-decoder GANs (BiGAN, ALI) cannot prevent mode collapse nor enforce meaningful code learning.
**Relevance:** Not directly relevant — GAN theory.

### arxiv_1712.04248.pdf

**Title:** Decision-Based Adversarial Attacks: Reliable Attacks Against Black-Box Machine Learning Models
**Authors:** Wieland Brendel, Jonas Rauber, Matthias Bethge
**Year:** 2017 (ICLR 2018)
**Topic tag:** adversarial
**Summary:** Boundary Attack — decision-only black-box attack that needs only the final predicted label.
**Relevance:** Decision-only attacks work against real production APIs that return labels but not confidences.

### arxiv_1712.09491.pdf

**Title:** Exploring the Space of Black-box Attacks on Deep Neural Networks
**Authors:** Arjun Nitin Bhagoji, Warren He, Bo Li, Dawn Song
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Gradient-estimation black-box attacks with PCA / random-grouping query reduction; demoed against Clarifai NSFW/moderation.
**Relevance:** Direct template for assessing query-limited attacks on commercial moderation/content-classification APIs.

### arxiv_1801.01944.pdf

**Title:** Audio Adversarial Examples: Targeted Attacks on Speech-to-Text
**Authors:** Nicholas Carlini, David Wagner
**Year:** 2018
**Topic tag:** adversarial
**Summary:** White-box iterative optimization attack on DeepSpeech producing near-imperceptible audio that transcribes to attacker-chosen phrases (100% success).
**Relevance:** ASR attack surface — relevant to voice-control and dictation services we assess.

### arxiv_1801.02610.pdf

**Title:** Spatially Transformed Adversarial Examples
**Authors:** Chaowei Xiao, Jun-Yan Zhu, Bo Li, Warren He, Mingyan Liu, Dawn Song
**Year:** 2018 (ICLR)
**Topic tag:** adversarial
**Summary:** stAdv — adversarial examples via small spatial transformations (flow field) rather than Lp perturbations.
**Relevance:** Non-Lp attack class — bypasses Lp-based defenses common in commercial robustness claims.

### arxiv_1801.02612.pdf

**Title:** Generating Adversarial Examples with Adversarial Networks (AdvGAN)
**Authors:** Chaowei Xiao, Bo Li, Jun-Yan Zhu, Warren He, Mingyan Liu, Dawn Song
**Year:** 2018
**Topic tag:** adversarial
**Summary:** GAN-based generator producing perceptually realistic adversarial examples in one feed-forward pass.
**Relevance:** Fast generative attacks scale adversarial-example production for at-scale model abuse.

### arxiv_1801.02613.pdf

**Title:** Characterizing Adversarial Subspaces Using Local Intrinsic Dimensionality
**Authors:** Xingjun Ma, Bo Li, Yisen Wang, Sarah M. Erfani, Sudanthi Wijewickrema, Grant Schoenebeck, Dawn Song, Michael E. Houle, James Bailey
**Year:** 2018 (ICLR)
**Topic tag:** defense
**Summary:** LID-based detection — adversarial examples live in higher-LID subspaces than clean inputs.
**Relevance:** Detection primitive; later shown weak against adaptive attackers — useful template for evaluating "detector" defenses.

### arxiv_1801.08535.pdf

**Title:** CommanderSong: A Systematic Approach for Practical Adversarial Voice Recognition
**Authors:** Xuejing Yuan, Yuxuan Chen, Yue Zhao, Yunhui Long, Xiaokang Liu, Kai Chen, Shengzhi Zhang, Heqing Huang, XiaoFeng Wang, Carl A. Gunter
**Year:** 2018 (USENIX Security)
**Topic tag:** adversarial
**Summary:** Embeds voice commands in songs such that ASR (Kaldi, iFLYTEK) executes them while humans hear only music.
**Relevance:** Real-world ASR attack vector against IVC products (Alexa/Siri/Google Assistant analogs).

### arxiv_1803.01128.pdf

**Title:** Seq2Sick: Evaluating the Robustness of Sequence-to-Sequence Models with Adversarial Examples
**Authors:** Minhao Cheng, Jinfeng Yi, Pin-Yu Chen, Huan Zhang, Cho-Jui Hsieh
**Year:** 2018 (AAAI 2020)
**Topic tag:** adversarial
**Summary:** Projected-gradient + group-lasso attack on seq2seq (machine translation, summarization) — non-overlapping and targeted-keyword attacks.
**Relevance:** NLP attack class relevant to translation/summarization-as-a-service deployments.

### arxiv_1803.04383.pdf

**Title:** Delayed Impact of Fair Machine Learning
**Authors:** Lydia T. Liu, Sarah Dean, Esther Rolf, Max Simchowitz, Moritz Hardt
**Year:** 2018
**Topic tag:** misc
**Summary:** Shows static fairness criteria can harm disadvantaged groups via one-step feedback dynamics.
**Relevance:** Not directly relevant — fairness dynamics, not security.

### arxiv_1804.00792.pdf

**Title:** Poison Frogs! Targeted Clean-Label Poisoning Attacks on Neural Networks
**Authors:** Ali Shafahi, W. Ronny Huang, Mahyar Najibi, Octavian Suciu, Christoph Studer, Tudor Dumitras, Tom Goldstein
**Year:** 2018
**Topic tag:** poisoning
**Summary:** Clean-label feature-collision poisoning — poisoned images keep correct labels and induce targeted misclassification.
**Relevance:** Clean-label poisoning is the realistic threat model for crowdsourced / scraped training data.

### arxiv_1804.02485.pdf

**Title:** Fortified Networks: Improving the Robustness of Deep Networks by Modeling the Manifold of Hidden Representations
**Authors:** Alex Lamb, Jonathan Binas, Anirudh Goyal, Dmitriy Serdyuk, Sandeep Subramanian, Ioannis Mitliagkas, Yoshua Bengio
**Year:** 2018
**Topic tag:** defense
**Summary:** Denoising-autoencoder "fortification" of hidden layers detects/maps off-manifold inputs back to the data manifold.
**Relevance:** Representative empirical defense — useful baseline for what production "robustness" usually amounts to.

### arxiv_1806.00088.pdf

**Title:** PeerNets: Exploiting Peer Wisdom Against Adversarial Attacks
**Authors:** Jan Svoboda, Jonathan Masci, Federico Monti, Michael M. Bronstein, Leonidas Guibas
**Year:** 2018
**Topic tag:** defense
**Summary:** Architecture alternating Euclidean and graph convolutions over a peer-sample graph for non-local feature aggregation; ~3× robustness gain.
**Relevance:** Architectural defense template — relevant when assessing custom robust-NN deployments.

### arxiv_1806.02371.pdf

**Title:** Adversarial Attack on Graph Structured Data
**Authors:** Hanjun Dai, Hui Li, Tian Tian, Xin Huang, Lin Wang, Jun Zhu, Le Song
**Year:** 2018 (ICML)
**Topic tag:** adversarial
**Summary:** RL- and genetic-algorithm-based attacks that perturb graph edges to fool GNN classifiers in white/practical-black/restricted-black settings.
**Relevance:** Graph-attack class relevant to fraud-detection / social-graph ML systems we encounter.

### arxiv_1806.08010.pdf

**Title:** Fairness Without Demographics in Repeated Loss Minimization
**Authors:** Tatsunori B. Hashimoto, Megha Srivastava, Hongseok Namkoong, Percy Liang
**Year:** 2018 (ICML)
**Topic tag:** misc
**Summary:** Distributionally-robust optimization (DRO) to control worst-group risk over time without demographic labels.
**Relevance:** Not directly relevant — fairness over time, not security.

### arxiv_1808.06601.pdf

**Title:** Video-to-Video Synthesis
**Authors:** Ting-Chun Wang, Ming-Yu Liu, Jun-Yan Zhu, Guilin Liu, Andrew Tao, Jan Kautz, Bryan Catanzaro
**Year:** 2018
**Topic tag:** foundations
**Summary:** Conditional-GAN framework for 2K photorealistic vid2vid translation (segmentation → driving footage, sketches, poses).
**Relevance:** Not directly relevant — generative video model; substrate for downstream deepfake/synthesis risks.

### arxiv_1810.05162.pdf

**Title:** Characterizing Adversarial Examples Based on Spatial Consistency Information for Semantic Segmentation
**Authors:** Chaowei Xiao, Ruizhi Deng, Bo Li, Fisher Yu, Mingyan Liu, Dawn Song
**Year:** 2018 (ECCV)
**Topic tag:** defense
**Summary:** Spatial-consistency detector for adversarial segmentation examples; segmentation-task adversarial perturbations transfer poorly across models.
**Relevance:** Detection template specific to dense-prediction tasks (autonomous driving segmentation).

### arxiv_1902.02918.pdf

**Title:** Certified Adversarial Robustness via Randomized Smoothing
**Authors:** Jeremy Cohen, Elan Rosenfeld, J. Zico Kolter
**Year:** 2019 (ICML)
**Topic tag:** certified-defense
**Summary:** Tight L_2 robustness guarantee for Gaussian-smoothed classifiers; first certified defense scaling to ImageNet (49% top-1 at L2≤0.5).
**Relevance:** Canonical certified-robustness mechanism; the bar real "certified" claims should meet.

### arxiv_1902.10275.pdf

**Title:** Towards Efficient Data Valuation Based on the Shapley Value
**Authors:** Ruoxi Jia, David Dao, Boxin Wang, Frances Ann Hubis, Nick Hynes, Nezihe Merve Gurel, Bo Li, Ce Zhang, Dawn Song, Costas Spanos
**Year:** 2019 (AISTATS)
**Topic tag:** misc
**Summary:** Efficient Shapley-value approximations for per-datum valuation in ML pipelines.
**Relevance:** Data-valuation underpins post-hoc audits of poisoned/biased contributors in training-data markets.

### arxiv_1905.13725.pdf

**Title:** Are Labels Required for Improving Adversarial Robustness? (UAT)
**Authors:** Jonathan Uesato, Jean-Baptiste Alayrac, Po-Sen Huang, Robert Stanforth, Alhussein Fawzi, Pushmeet Kohli
**Year:** 2019 (NeurIPS)
**Topic tag:** defense
**Summary:** Unsupervised Adversarial Training — unlabeled data closes most of the robustness gap from extra labeled data.
**Relevance:** Reduces the cost of robustness; relevant when assessing scalable robust-training claims.

### arxiv_1905.13736.pdf

**Title:** Unlabeled Data Improves Adversarial Robustness
**Authors:** Yair Carmon, Aditi Raghunathan, Ludwig Schmidt, Percy Liang, John C. Duchi
**Year:** 2019 (NeurIPS)
**Topic tag:** defense
**Summary:** Robust self-training (RST) leverages 500K unlabeled CIFAR images via TRADES + smoothing for SOTA L_inf/L_2 robustness.
**Relevance:** Concurrent with UAT; both establish unlabeled-data scaling laws for robustness.

### arxiv_1908.08619.pdf

**Title:** Efficient Task-Specific Data Valuation for Nearest Neighbor Algorithms
**Authors:** Ruoxi Jia, David Dao, Boxin Wang, Frances Ann Hubis, Nezihe Merve Gurel, Bo Li, Ce Zhang, Costas J. Spanos, Dawn Song
**Year:** 2019
**Topic tag:** misc
**Summary:** Exact O(N log N) Shapley-value computation for unweighted KNN classifiers; LSH-based sublinear approximation.
**Relevance:** Practical data-valuation for KNN/retrieval components in modern RAG/agent stacks.

### arxiv_2004.04986.pdf

**Title:** Towards Federated Learning With Byzantine-Robust Client Weighting
**Authors:** Amit Portnoy, Yoav Tirosh, Danny Hendler
**Year:** 2020
**Topic tag:** defense
**Summary:** Weight-truncation preprocessing for FL preserving Byzantine robustness when client weights are self-reported.
**Relevance:** FL-robustness primitive — relevant when assessing federated AI deployments with untrusted clients.

### arxiv_2106.08283.pdf / 2106.08283v1.pdf

**Title:** CRFL: Certifiably Robust Federated Learning against Backdoor Attacks
**Authors:** Chulin Xie, Minghao Chen, Pin-Yu Chen, Bo Li
**Year:** 2021 (ICML)
**Topic tag:** certified-defense
**Summary:** First general certified-robust FL framework against backdoors — parameter clipping + smoothing yield sample-wise certification.
**Relevance:** Federated backdoor certification — relevant where FL is deployed under poisoning-capable participants. (Two identical files: 2106.08283.pdf and 2106.08283v1.pdf.)

### arxiv.org_pdf_1312.6199.pdf

**Title:** Intriguing Properties of Neural Networks
**Authors:** Christian Szegedy, Wojciech Zaremba, Ilya Sutskever, Joan Bruna, Dumitru Erhan, Ian Goodfellow, Rob Fergus
**Year:** 2013
**Topic tag:** adversarial
**Summary:** First demonstration of adversarial examples in DNNs via L-BFGS perturbations.
**Relevance:** The origin paper — the entire AdvML field starts here.

### arxiv.org_pdf_1511.04508.pdf

**Title:** Distillation as a Defense to Adversarial Perturbations against Deep Neural Networks
**Authors:** Nicolas Papernot, Patrick McDaniel, Xi Wu, Somesh Jha, Ananthram Swami
**Year:** 2015
**Topic tag:** defense
**Summary:** Defensive distillation reduces input-gradient sensitivity (later broken by C&W).
**Relevance:** Historically broken defense — example case for "broken-by-stronger-attack" pattern.

### arxiv.org_pdf_1607.02060.pdf

**Title:** Detecting Communities under Differential Privacy
**Authors:** Hiep H. Nguyen, Abdessamad Imine, Michaël Rusinowitch
**Year:** 2016
**Topic tag:** privacy
**Summary:** LouvainDP (input perturbation) and ModDivisive (algorithm perturbation) for DP community detection.
**Relevance:** Graph-DP primitive — relevant for social-graph / fraud-graph deployments with privacy constraints.

### arxiv.org_pdf_1608.02257.pdf

**Title:** Hidden Voice Commands
**Authors:** Nicholas Carlini, Pratyush Mishra, Tavish Vaidya, Yuankai Zhang, Micah Sherr, Clay Shields, David Wagner, Wenchao Zhou
**Year:** 2016 (USENIX Security)
**Topic tag:** adversarial
**Summary:** Crafts obfuscated audio that humans hear as noise but ASR systems interpret as commands.
**Relevance:** Earliest ASR command-injection class — relevant to voice-assistant assessments.

### arxiv.org_pdf_1610.05820.pdf

**Title:** Membership Inference Attacks Against Machine Learning Models
**Authors:** Reza Shokri, Marco Stronati, Congzheng Song, Vitaly Shmatikov
**Year:** 2016
**Topic tag:** privacy
**Summary:** Shadow-model training to determine if a specific record was in the target model's training set; works against MLaaS APIs.
**Relevance:** Canonical privacy attack — direct template for assessing model-API exposure to membership inference.

### arxiv.org_pdf_1702.07464.pdf

**Title:** Deep Models Under the GAN: Information Leakage from Collaborative Deep Learning
**Authors:** Briland Hitaj, Giuseppe Ateniese, Fernando Perez-Cruz
**Year:** 2017 (CCS)
**Topic tag:** privacy
**Summary:** GAN-based attack reconstructs training-class samples from other participants in collaborative/federated DL, defeating record-level DP.
**Relevance:** Demonstrates record-level DP is insufficient for collaborative learning — relevant to FL audit.

### arxiv.org_pdf_1703.02702.pdf

**Title:** Adversarial Examples for Evaluating Reading Comprehension Systems
**Authors:** Robin Jia, Percy Liang
**Year:** 2017 (EMNLP)
**Topic tag:** adversarial
**Summary:** Appending distractor sentences to SQuAD passages drops F1 of SOTA QA models by ~50%.
**Relevance:** Earliest NLP-task adversarial-example — relevant to QA-as-a-service robustness.

### arxiv.org_pdf_1703.10593.pdf

**Title:** Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks (CycleGAN)
**Authors:** Jun-Yan Zhu, Taesung Park, Phillip Isola, Alexei A. Efros
**Year:** 2017
**Topic tag:** foundations
**Summary:** CycleGAN — unpaired image-to-image translation via cycle-consistency loss.
**Relevance:** Not directly relevant — pure ML foundations; generative substrate.

### arxiv.org_pdf_1707.05373.pdf

**Title:** Houdini: Fooling Deep Structured Visual and Speech Recognition Models with Adversarial Examples
**Authors:** Moustapha Cisse, Yossi Adi, Natalia Neverova, Joseph Keshet
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Differentiable surrogate loss for attacking non-differentiable structured-prediction metrics (BLEU, IoU, WER).
**Relevance:** Generalizes evasion to structured-output AI systems — relevant to translation/segmentation/ASR audits.

### arxiv.org_pdf_1707.07328.pdf

**Title:** Adversarial Examples for Evaluating Reading Comprehension Systems (alt ID)
**Authors:** Robin Jia, Percy Liang
**Year:** 2017
**Topic tag:** adversarial
**Summary:** Same paper as 1703.02702 in this corpus listing — text-distractor attack on QA systems.
**Relevance:** Same as 1703.02702 entry.

### arxiv.org_pdf_1710.03184.pdf

**Title:** On Formalizing Fairness in Prediction with Machine Learning
**Authors:** Pratik Gajane, Mykola Pechenizkiy
**Year:** 2017
**Topic tag:** misc
**Summary:** Survey mapping ML-fairness formalizations to distributive-justice notions from social science.
**Relevance:** Not directly relevant — fairness taxonomy.

### arxiv.org_pdf_1711.00851.pdf

**Title:** Provable Defenses against Adversarial Examples via the Convex Outer Adversarial Polytope
**Authors:** Eric Wong, J. Zico Kolter
**Year:** 2017
**Topic tag:** certified-defense
**Summary:** LP-relaxation bounds give a trainable certificate of robustness for L_inf attacks on small NNs.
**Relevance:** Foundational certified-robustness mechanism — predecessor to IBP and randomized smoothing.

### arxiv.org_pdf_1711.02827.pdf

**Title:** Inverse Reward Design
**Authors:** Dylan Hadfield-Menell, Smitha Milli, Pieter Abbeel, Stuart Russell, Anca D. Dragan
**Year:** 2017 (NeurIPS)
**Topic tag:** misc
**Summary:** Treats given reward functions as observations of true reward, enabling risk-averse RL under distributional shift.
**Relevance:** Not directly relevant — reward-design / safety, tangential to AdvML.

### arxiv.org_pdf_1802.08232.pdf

**Title:** The Secret Sharer: Evaluating and Testing Unintended Memorization in Neural Networks
**Authors:** Nicholas Carlini, Chang Liu, Úlfar Erlingsson, Jernej Kos, Dawn Song
**Year:** 2018
**Topic tag:** privacy
**Summary:** Exposure metric quantifying that generative LMs memorize and leak secret-style training inputs.
**Relevance:** Core memorization-leakage methodology — directly relevant to LLM training-data leakage audits.

### arxiv.org_pdf_1804.00308.pdf

**Title:** Mitigating Sybils in Federated Learning Poisoning (FoolsGold)
**Authors:** Clement Fung, Chris J.M. Yoon, Ivan Beschastnikh
**Year:** 2018
**Topic tag:** defense
**Summary:** FoolsGold detects sybil poisoners in FL via cosine-similarity of their gradient updates.
**Relevance:** Standard FL-robustness baseline — what we expect to see in FL deployments.

### arxiv.org_pdf_1809.01093.pdf

**Title:** Adversarial Attacks on Node Embeddings via Graph Poisoning
**Authors:** Aleksandar Bojchevski, Stephan Günnemann
**Year:** 2018 (ICML 2019)
**Topic tag:** poisoning
**Summary:** First poisoning attack on unsupervised random-walk node embeddings via eigenvalue-perturbation theory.
**Relevance:** Graph-embedding poisoning relevant to fraud/recommendation/social-graph downstream tasks.

### arxiv.org_pdf_1810.12715.pdf

**Title:** On the Effectiveness of Interval Bound Propagation for Training Verifiably Robust Models
**Authors:** Sven Gowal, Krishnamurthy Dvijotham, Robert Stanforth, Rudy Bunel, Chongli Qin, Jonathan Uesato, Relja Arandjelović, Timothy Mann, Pushmeet Kohli
**Year:** 2018
**Topic tag:** certified-defense
**Summary:** IBP — simple interval bounds yield SOTA verifiable accuracy with curriculum training; first provable ImageNet defense.
**Relevance:** IBP is now the standard for verified-robustness baseline against L_inf in production-scale models.

### arxiv.org_pdf_1902.07906.pdf

**Title:** Wasserstein Adversarial Examples via Projected Sinkhorn Iterations
**Authors:** Eric Wong, Frank R. Schmidt, J. Zico Kolter
**Year:** 2019
**Topic tag:** adversarial
**Summary:** Adversarial examples bounded in Wasserstein distance via projected-Sinkhorn iteration; non-Lp threat model.
**Relevance:** Non-Lp attack class bypassing Lp-defended classifiers — relevant to "Lp robustness" claims.

### arxiv.org_pdf_1902.09192.pdf

**Title:** Batch Virtual Adversarial Training for Graph Convolutional Networks
**Authors:** Zhijie Deng, Yinpeng Dong, Jun Zhu
**Year:** 2019
**Topic tag:** defense
**Summary:** BVAT — virtual-adversarial regularization tailored to GCN receptive fields for semi-supervised robustness.
**Relevance:** Graph-task defense relevant to fraud/social GNN deployments.

### arxiv.org_pdf_1906.04214.pdf

**Title:** Topology Attack and Defense for Graph Neural Networks: An Optimization Perspective
**Authors:** Kaidi Xu, Hongge Chen, Sijia Liu, Pin-Yu Chen, Tsui-Wei Weng, Mingyi Hong, Xue Lin
**Year:** 2019
**Topic tag:** adversarial
**Summary:** Convex-relaxation-based first-order topology attacks (PGD/min-max) on GNNs plus adversarial-training defense.
**Relevance:** Graph-attack template applicable to deployed GNN classification systems.

### 1097_dba_distributed_backdoor_attac.pdf

**Title:** DBA: Distributed Backdoor Attacks against Federated Learning
**Authors:** Chulin Xie, Keli Huang, Pin-Yu Chen, Bo Li
**Year:** 2020 (ICLR)
**Topic tag:** backdoor
**Summary:** Decomposes a global backdoor trigger into per-adversary local triggers, evading robust FL aggregation rules.
**Relevance:** Distributed backdoor model — direct threat to multi-party FL deployments.

### acmccs.github.io_papers_p425-qinAemb.pdf

**Title:** Generating Synthetic Decentralized Social Graphs with Local Differential Privacy (LDPGen)
**Authors:** Zhan Qin, Ting Yu, Yin Yang, Issa Khalil, Xiaokui Xiao, Kui Ren
**Year:** 2017 (CCS)
**Topic tag:** privacy
**Summary:** Multi-phase LDP technique that clusters users by partition connectivity to synthesize utility-preserving social graphs.
**Relevance:** LDP graph synthesis — relevant to deployed contact-graph privacy claims.

### openreview_BJehNfW0-.pdf

**Title:** Certified Defenses against Adversarial Examples
**Authors:** Aditi Raghunathan, Jacob Steinhardt, Percy Liang
**Year:** 2018 (ICLR)
**Topic tag:** certified-defense
**Summary:** SDP-relaxation certificate that, jointly optimized with the network, acts as a robustness regularizer for two-layer NNs.
**Relevance:** Early provable defense — foundational reference for certified-robustness claims.

### openreview_Bys4ob-Rb.pdf

**Title:** Certifying Some Distributional Robustness with Principled Adversarial Training
**Authors:** Aman Sinha, Hongseok Namkoong, John Duchi
**Year:** 2018 (ICLR)
**Topic tag:** certified-defense
**Summary:** Wasserstein-DRO Lagrangian formulation gives certified bounds on adversarial population loss with cost comparable to ERM.
**Relevance:** DRO-based certified robustness — distinct from L_p smoothing; relevant for distribution-shift audits.

### openreview_Hk6kPgZA-.pdf

**Title:** DBA: Distributed Backdoor Attacks against Federated Learning (OpenReview)
**Authors:** Chulin Xie, Keli Huang, Pin-Yu Chen, Bo Li
**Year:** 2020 (ICLR)
**Topic tag:** backdoor
**Summary:** Same as 1097_dba paper — OpenReview copy.
**Relevance:** Duplicate of the DBA paper above.

### openreview_rkgyS0VFvr.pdf

**Title:** Scalable Private Learning with PATE
**Authors:** Nicolas Papernot, Shuang Song, Ilya Mironov, Ananth Raghunathan, Kunal Talwar, Úlfar Erlingsson
**Year:** 2018 (ICLR)
**Topic tag:** privacy
**Summary:** Improved PATE — Confident-GNMax aggregation with Gaussian noise scales DP teacher-ensemble learning to large datasets.
**Relevance:** Production-scale PATE — the practical reference for high-utility differentially-private training.

### openreview_rkZB1XbRZ.pdf

**Title:** Do GANs learn the distribution? Some Theory and Empirics
**Authors:** Sanjeev Arora, Andrej Risteski, Yi Zhang
**Year:** 2018 (ICLR)
**Topic tag:** foundations
**Summary:** Birthday-paradox test shows GANs (including encoder-decoder) exhibit mode collapse and fail to learn full distribution.
**Relevance:** Not directly relevant — GAN theory.

### papers.nips.cc_paper_5423-generative-adversarial-nets.pdf

**Title:** Generative Adversarial Nets
**Authors:** Ian J. Goodfellow, Jean Pouget-Abadie, Mehdi Mirza, Bing Xu, David Warde-Farley, Sherjil Ozair, Aaron Courville, Yoshua Bengio
**Year:** 2014 (NeurIPS)
**Topic tag:** foundations
**Summary:** The original GAN paper.
**Relevance:** Not directly relevant — pure ML foundations; underpins many generative-attack papers in this corpus.

### papers.nips.cc_paper_5515-robust-logistic-regression-and-classification.pdf

**Title:** Robust Logistic Regression and Classification
**Authors:** Jiashi Feng, Huan Xu, Shie Mannor, Shuicheng Yan
**Year:** 2014 (NeurIPS)
**Topic tag:** defense
**Summary:** Robust logistic regression resistant to outlier contamination in training data.
**Relevance:** Foundational robust-classification primitive — substrate for later poisoning defenses.

### homes.cs.washington.edu_~pedrod_papers_kdd04.pdf

**Title:** Adversarial Classification
**Authors:** Nilesh Dalvi, Pedro Domingos, Mausam, Sumit Sanghai, Deepak Verma
**Year:** 2004 (KDD)
**Topic tag:** adversarial
**Summary:** Game-theoretic Bayes-vs-attacker model for spam filtering — original adversarial-classification paper.
**Relevance:** The historical seed of the entire AdvML field.

### ix.cs.uoregon.edu_~lowd_kdd05lowd.pdf / kdd05lowd.pdf

**Title:** Adversarial Learning
**Authors:** Daniel Lowd, Christopher Meek
**Year:** 2005 (KDD)
**Topic tag:** adversarial
**Summary:** Defines ACRE (adversarial classifier reverse engineering) — query-based attacks on linear classifiers.
**Relevance:** Earliest query-based model-extraction framing. (Two identical files.)

### nodeprivacy-TCC.pdf

**Title:** Analyzing Graphs with Node Differential Privacy
**Authors:** Shiva Prasad Kasiviswanathan, Kobbi Nissim, Sofya Raskhodnikova, Adam Smith
**Year:** 2013 (TCC)
**Topic tag:** privacy
**Summary:** Algorithms for accurate node-DP graph statistics via projection onto bounded-degree graphs.
**Relevance:** Node-DP foundations — relevant where social/contact graphs underpin AI deployments.

### openaccess.thecvf.com_content_ICCV_2017_papers_Lu_SafetyNet_Detecting_and_ICCV_2017_paper.pdf

**Title:** SafetyNet: Detecting and Rejecting Adversarial Examples Robustly
**Authors:** Jiajun Lu, Theerasit Issaranon, David Forsyth
**Year:** 2017 (ICCV)
**Topic tag:** defense
**Summary:** ReLU-pattern + SVM detector that classifies adversarial vs natural inputs at intermediate layers.
**Relevance:** Detector-style defense — class later shown weak against adaptive attackers.

### pages.cs.wisc.edu_~jerryzhu_pub_Mei2015Machine.pdf

**Title:** Using Machine Teaching to Identify Optimal Training-Set Attacks on Machine Learners
**Authors:** Shike Mei, Xiaojin Zhu
**Year:** 2015 (AAAI)
**Topic tag:** poisoning
**Summary:** Machine-teaching framework finds the smallest training-set perturbation that flips the learned model toward a target.
**Relevance:** Foundational optimal-poisoning formulation — basis for the data-poisoning literature.

### pengcui.thumedialab.com_papers_RGCN.pdf

**Title:** Robust Graph Convolutional Networks Against Adversarial Attacks (RGCN)
**Authors:** Dingyuan Zhu, Ziwei Zhang, Peng Cui, Wenwu Zhu
**Year:** 2019 (KDD)
**Topic tag:** defense
**Summary:** Gaussian-distribution node-representation GCN with variance-based attention to absorb adversarial perturbations.
**Relevance:** Graph defense relevant to GNN-based fraud/recommendation systems.

### people.cs.uchicago.edu_~ravenben_publications_pdf_backdoor-sp19.pdf

**Title:** Neural Cleanse: Identifying and Mitigating Backdoor Attacks in Neural Networks
**Authors:** Bolun Wang, Yuanshun Yao, Shawn Shan, Huiying Li, Bimal Viswanath, Haitao Zheng, Ben Y. Zhao
**Year:** 2019 (IEEE S&P)
**Topic tag:** backdoor
**Summary:** Reverse-engineers minimal triggers per class to detect backdoors and patches them out via unlearning.
**Relevance:** Standard backdoor-detection technique — relevant whenever third-party / supplied models are accepted.

### proceedings.mlr.press_v97_mahloujifar19a_mahloujifar19a.pdf

**Title:** The Curse of Concentration in Robust Learning: Evasion and Poisoning Attacks from Concentration of Measure
**Authors:** Saeed Mahloujifar, Dimitrios I. Diochnos, Mohammad Mahmoody
**Year:** 2019 (ICML)
**Topic tag:** adversarial
**Summary:** Concentration-of-measure arguments showing distributions in NN-relevant metric spaces inherently admit evasion and p-tampering poisoning.
**Relevance:** Information-theoretic lower bound on robustness — sets ceiling on what any defense can claim.

### tnn_ndss18.pdf / weihang-wang.github.io_papers_tnn_ndss18.pdf

**Title:** Trojaning Attack on Neural Networks
**Authors:** Yingqi Liu, Shiqing Ma, Yousra Aafer, Wen-Chuan Lee, Juan Zhai, Weihang Wang, Xiangyu Zhang
**Year:** 2018 (NDSS)
**Topic tag:** backdoor
**Summary:** Reverse-engineers a stamp trigger that maximally activates chosen neurons, retrains on synthesized inputs to inject backdoor without original data.
**Relevance:** Canonical no-data-needed trojaning attack — direct threat to model-marketplace deployments. (Two identical files.)

### semscholar-cb30f71d.pdf

**Title:** (Semantic Scholar export — content varies; likely a privacy/robustness paper indexed by hash)
**Authors:** TBD
**Year:** TBD
**Topic tag:** misc
**Summary:** Identifier-only filename; rendered content matches a CS562/598 reading-list paper but specific title not confirmed in sampled pages.
**Relevance:** Reflects coverage of corpus; treat as supplementary reading.

### vision.stanford.edu_pdf_mandlekar2017iros.pdf

**Title:** Adversarially Robust Policy Learning: Active Construction of Physically-Plausible Perturbations
**Authors:** Ajay Mandlekar, Yuke Zhu, Animesh Garg, Li Fei-Fei, Silvio Savarese
**Year:** 2017 (IROS)
**Topic tag:** defense
**Summary:** Adversarial training for RL policies using physically plausible perturbations during simulation.
**Relevance:** Robust-RL — relevant to safety-critical robotics/autonomous-system audits.

### www.ijcai.org_proceedings_2019_0674.pdf

**Title:** Data Poisoning Attack against Knowledge Graph Embedding
**Authors:** Hengtong Zhang, Tianhang Zheng, Jing Gao, Chenglin Miao, Lu Su, Yaliang Li, Kui Ren
**Year:** 2019 (IJCAI)
**Topic tag:** poisoning
**Summary:** Direct/indirect strategies that add or delete facts to manipulate plausibility of target triples in KGE methods.
**Relevance:** KG poisoning relevant to recommendation/QA systems built on knowledge graphs.

### www.vorobeychik.com_2014_sma.pdf

**Title:** Feature Cross-Substitution in Adversarial Classification
**Authors:** Bo Li, Yevgeniy Vorobeychik
**Year:** 2014 (NeurIPS)
**Topic tag:** adversarial
**Summary:** Mixed-integer programming framework for spam/phishing classifiers robust to feature cross-substitution attacks (synonyms, character swaps).
**Relevance:** Bo Li's early work — feature-substitution attack template for text/spam classifiers.

### Prolego LLM Optimization Playbook.pdf

**Title:** LLM Optimization Playbook
**Authors:** Prolego (industry whitepaper)
**Year:** ~2023-2024
**Topic tag:** misc
**Summary:** Industry guide to moving LLM demos to production — covers 13 optimization choices from prompts to fine-tuning to agents/tools.
**Relevance:** Not part of original 2021 reading list; appears to be a later-added industry reference for project-implementation guidance.

## Topic distribution

Of the 126 PDFs: roughly 22 are course slides (Bo Li lectures + 19 student presentation decks + the syllabus), 4 are guest-lecture abstracts/slides, and ~100 are reading-list papers. Of the readings, the largest cluster is evasion / adversarial-example attacks (FGSM/CW/PGD lineage, transferability, decision-based black-box, audio/video/segmentation/graph/RL evasion — ~30 papers) and the matched defense / detection cluster (PeerNet, Fortified Networks, LID, SafetyNet, defensive distillation — ~15). Certified-defense forms a distinct ~10-paper cluster (randomized smoothing, IBP, convex outer polytope, SDP certification, Wasserstein-DRO, CRFL, certified poisoning defense). Privacy contributes ~10 (DP-SGD, PATE × 2, Secret Sharer, membership inference, GAN-leakage in FL, LDP graph synthesis, node-DP, plausible deniability). Poisoning + backdoor together total ~12 (Biggio SVM poisoning, Poison Frogs, KGE/CF/influence-function poisoning, DBA × 2, Neural Cleanse, Trojaning × 2, Mei-Zhu machine teaching). The remainder is foundations (GANs, GCNs, CycleGAN, vid2vid, generalization-of-GANs theory — ~10), graph/GNN-specific AdvML (~6 papers attacks+defenses), and a small misc tail (fairness/causality/IRD — 5) plus one industry LLM playbook PDF. Skipped/degraded: none — every PDF rendered with extractable first pages; a few are duplicates (DBA in two forms, CRFL in two forms, Jia-Liang QA paper duplicated, Lowd-Meek duplicated, Trojaning duplicated). The semscholar-cb30f71d.pdf was identifier-only and the rendered content didn't match a canonical title cleanly — left as TBD.
