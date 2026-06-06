# CS 307 — AI Security Course Index

**Instructor:** Bo Li (UIUC), with several decks by D.A. Forsyth (UIUC)
**Course path:** ~/Documents/cs307-aisecure/
**Course title (per decks):** CS 307 — Modeling and Learning in Data Science
**Total PDFs indexed:** 13 (one PDF in the corpus, `aisecure.github.io_syllabus.pdf`, is actually a GitHub Pages 404 HTML page, not a PDF — excluded from the count)

## Syllabus

The literal `aisecure.github.io_syllabus.pdf` file does not contain syllabus content — it is an HTML 404 ("Page not found · GitHub Pages") saved with a `.pdf` extension, the artifact of a broken URL on aisecure.github.io. The course shape can be reconstructed from the lecture decks and assignment PDFs:

CS 307 ("Modeling and Learning in Data Science") is an undergraduate-level UIUC course taught by Bo Li (with selected lectures by D.A. Forsyth). The arc is foundational ML — classification (nearest neighbors, linear classifiers/SVM, Naive Bayes, logistic regression, random forests), unsupervised representation learning (dimension reduction, VAE, GANs), sequence/language models (word embeddings, attention, Transformers, BERT, GPT), control (MDPs, RL, imitation learning), and a closing real-world applications lecture that introduces Vision Transformers, Trustworthy ML (adversarial perturbations, stationarity-assumption failure), and POMDPs. Labs use scikit-style problems (e.g. Week 1: leave-one-out cross-val of KNN on a Turkish-raisin dataset). The final project menu (MDP/RL tic-tac-toe, denoising AE on MNIST, or training a 3-layer DNN on MNIST and generating adversarial attacks against it) confirms the security angle is treated as one capstone option, not the through-line — this is intro ML with a Trustworthy-ML capstone, not a dedicated AI-security course despite the `aisecure.github.io` hosting.

## Papers / lectures

### aisecure.github.io_307-NB.pdf

**Title:** CS 397. Naïve Bayes (note: title slide says CS 397, deck reused for CS 307)
**Authors:** Bo Li (course material)
**Year:** 2022 (course)
**Topic tag:** foundations
**Summary:** Lecture deck on probabilistic classification — background of classifiers (discriminative vs generative), probability basics, Naive Bayes with the Play Tennis worked example. Standard intro-ML treatment.
**Relevance to NuClide research program:** Not directly relevant — pure ML foundations.

### aisecure.github.io_cs307-dimension-reduction.pdf

**Title:** CS307 — Dimension Reduction / Mapping (Sammon, t-SNE, Autoencoders)
**Authors:** Bo Li (course material)
**Year:** 2022
**Topic tag:** foundations
**Summary:** Lecture deck on dimension reduction and representation learning — motivation, Sammon mapping, t-SNE, autoencoders and denoising autoencoders (Forsyth textbook chapter 19).
**Relevance to NuClide research program:** Not directly relevant — pure ML foundations.

### aisecure.github.io_CS_307_Labs.pdf

**Title:** CS 307 Lab — Week 1
**Authors:** Course material (instructor unattributed)
**Year:** 2022
**Topic tag:** foundations
**Summary:** Lab handout — leave-one-out cross-validated nearest-neighbor classifier on a Turkish raisin dataset, with and without feature normalization, plus a k-NN sweep. One page.
**Relevance to NuClide research program:** Not directly relevant — intro lab exercise.

### aisecure.github.io_cs307-logistic.pdf

**Title:** CS 307. Logistic Regression, Kalman Filtering
**Authors:** Bo Li (course material)
**Year:** 2022
**Topic tag:** foundations
**Summary:** Lecture deck — recap of Naive Bayes, then logistic regression and Kalman filtering as probabilistic / state-estimation models.
**Relevance to NuClide research program:** Not directly relevant — pure ML foundations.

### aisecure.github.io_cs307-vae.pdf

**Title:** CS307 — VAE and GANs
**Authors:** Bo Li (course material)
**Year:** 2022
**Topic tag:** foundations
**Summary:** Lecture deck on generative models — recap of Sammon / t-SNE / autoencoders, then variational autoencoders and generative adversarial networks.
**Relevance to NuClide research program:** Foundational AI/ML background; VAEs/GANs are the architectural family behind many model-server payloads we fingerprint, but the deck is pure pedagogy.

### aisecure.github.io_cs307-word-bert.pdf

**Title:** CS 307 — Word Embeddings, BERT, GPT
**Authors:** Bo Li (course material)
**Year:** 2022
**Topic tag:** foundations
**Summary:** Lecture deck covering image autoencoder recap, simple word embeddings, encoder-decoder models, attention, Transformers, then BERT and GPT. Intro-level Transformer/LLM pipeline.
**Relevance to NuClide research program:** Foundational AI/ML background — the BERT/GPT pipeline this teaches is exactly the class of model sitting behind the inference endpoints we fingerprint with aimap.

### aisecure.github.io_cs307-word-embeddings.pdf

**Title:** CS 307 — Word Embeddings, Attention, Transformers
**Authors:** Bo Li (course material)
**Year:** 2022
**Topic tag:** foundations
**Summary:** Earlier-in-sequence companion to the BERT/GPT deck — image autoencoder recap, word embedding construction, encoder-decoder, attention mechanism, Transformer architecture (stops before BERT/GPT).
**Relevance to NuClide research program:** Foundational AI/ML background.

### aisecure.github.io_LinearStart.pdf

**Title:** Linear Classifiers and the Linear SVM
**Authors:** D.A. Forsyth (UIUC)
**Year:** 2022 (course)
**Topic tag:** foundations
**Summary:** Lecture deck on linear classifiers — feature vector x with label y in {-1, +1}, prediction sign(aᵀx + b), then derivation toward the linear SVM.
**Relevance to NuClide research program:** Not directly relevant — pure ML foundations.

### aisecure.github.io_MDPS-RL-daf-1.pdf

**Title:** Learning to control (MDPs, RL, Imitation Learning)
**Authors:** D.A. Forsyth (UIUC)
**Year:** 2022 (course)
**Topic tag:** foundations
**Summary:** Lecture deck — "scamper through" basic reinforcement learning ideas, then imitation learning and its variants framed as structure learning.
**Relevance to NuClide research program:** Not directly relevant — pure RL foundations.

### aisecure.github.io_nnstart.pdf

**Title:** Classification and Nearest Neighbors
**Authors:** D.A. Forsyth (UIUC)
**Year:** 2022 (course)
**Topic tag:** foundations
**Summary:** Lecture deck — what classification is (feature vector to label), binary vs multiclass, evaluation, and the central problem of estimating accuracy on unlabeled data. Sets up KNN.
**Relevance to NuClide research program:** Not directly relevant — pure ML foundations.

### aisecure.github.io_RandomForest.pdf

**Title:** CS 307: Random Forests
**Authors:** Bo Li (course material)
**Year:** 2022
**Topic tag:** foundations
**Summary:** Lecture deck — decision trees, random forests, RF hyperparameter tuning, feature importance / interpretation.
**Relevance to NuClide research program:** Not directly relevant — pure ML foundations.

### dropbox_CS307_Finals.pdf

**Title:** CS 307 — Final (project specification)
**Authors:** Course material (Bo Li, UIUC)
**Year:** 2022 (May 11 due date)
**Topic tag:** misc
**Summary:** One-page final project handout. Four suggested topics: (1) MDP tic-tac-toe via value/policy iteration, (2) RL tic-tac-toe, (3) denoising autoencoder for MNIST, (4) train a small DNN on MNIST and generate adversarial attacks against it. NeurIPS format, ≥3-page report.
**Relevance to NuClide research program:** Topic 4 (DNN + adversarial attack) is the only direct touch point with our threat-class taxonomy — the canonical undergraduate entry into evasion attacks against image classifiers.

### dropbox_cs307-real.pdf

**Title:** CS 307 Real-World Applications (Vision Transformer; Trustworthy ML; RL/POMDP)
**Authors:** Bo Li (course material)
**Year:** 2022
**Topic tag:** adversarial (mixed — also covers ViT and POMDPs)
**Summary:** 69-page capstone deck stitching three real-world ML topics together. Section 1 is a Vision Transformer walkthrough (patch tokenization, class token, positional embeddings, MLP head) with CIFAR-10/100 benchmarks comparing ViT, Hybrid ViT, ResNet34, and pretrained ViT. Section 2 ("Trustworthy ML") is the security content — adversarial environments around TensorFlow/PyTorch/H2O/AWS ML, the perils of the stationary-data assumption, and the adversarial perturbation formulation max_ε J(θ, x+ε, y) solved via local search / combinatorial opt / convex relaxation. Section 3 covers reinforcement learning and POMDPs.
**Relevance to NuClide research program:** Threat class enabling LLM03/LLM04 lineage — establishes the classical adversarial-perturbation framing for inference-time evasion that later evolved into prompt-injection and jailbreaking against LLMs. Useful as background for any case study discussing evasion vs. extraction vs. poisoning taxonomy.

### dropbox_MDPS-RL429.pdf

**Title:** Learning to control (MDPs, RL, Imitation Learning) — April 29 version
**Authors:** D.A. Forsyth (UIUC)
**Year:** 2022
**Topic tag:** foundations
**Summary:** Duplicate / later revision of `aisecure.github.io_MDPS-RL-daf-1.pdf` — same outline (RL basics, imitation learning as structure learning), expanded body (8.1MB vs 3.1MB).
**Relevance to NuClide research program:** Not directly relevant — pure RL foundations.

## Lecture videos (skipped from indexing)

- 19-Jan-22.mp4 (~196MB)
- 21-Jan-22.mp4 (~203MB)
- 26-Jan-22.mp4 (~151MB)
- 28-Jan-22.mp4 (~267MB)
- Class-29-April.mp4 (~128MB)

These are the live-lecture recordings; January videos almost certainly cover the early foundations decks (classification, KNN, linear classifiers); the April 29 video corresponds to the `MDPS-RL429` deck (Learning to Control). Not transcribed for this index.

## Topic distribution

Of 13 indexed PDFs: 11 are pure ML foundations (classification, KNN, linear/SVM, Naive Bayes, logistic regression, random forests, dimension reduction, VAE/GAN, word embeddings/attention/Transformers/BERT/GPT, MDP/RL/imitation x2, the Week-1 lab), 1 (`dropbox_cs307-real.pdf`) is mixed — Vision Transformer + Trustworthy ML + RL/POMDP — and is the only deck containing the adversarial-perturbation formulation, and 1 (`dropbox_CS307_Finals.pdf`) is the final-project handout, misc, whose topic #4 (DNN + adversarial attacks on MNIST) is the only other adversarial touch point. There are 0 papers in this corpus on extraction, model inversion, membership inference, data poisoning, backdoor / Trojan attacks, watermarking, differential privacy, or LLM-specific threats (prompt injection, jailbreaking, RAG poisoning). The course title — "Modeling and Learning in Data Science" — is the honest one; "aisecure" in the GitHub Pages slug overstates the security content, which is one capstone deck and one final-project option. For NuClide threat-class taxonomy work, only `dropbox_cs307-real.pdf` (adversarial perturbation lineage) and `dropbox_CS307_Finals.pdf` (the MNIST-adversarial project prompt) are directly cite-worthy; the rest are useful only as foundational ML background context.
