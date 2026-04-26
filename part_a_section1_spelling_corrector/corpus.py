"""
corpus.py - Corpus Builder & Preprocessor
Builds a movie domain-specific AI/NLP corpus from embedded seed text + generates 
a rich vocabulary of AI terminology.
"""

import re
import json
import math
from collections import Counter, defaultdict

# ─── Embedded AI/NLP Domain Corpus (seed text) ──────────────────────────────
SEED_CORPUS = """
Artificial intelligence and machine learning have revolutionized the field of 
natural language processing. Deep learning models such as transformers have 
enabled remarkable advances in text understanding and generation. The attention 
mechanism introduced in the seminal paper "Attention is All You Need" formed 
the foundation of modern large language models.

Tokenization is a fundamental preprocessing step in natural language processing 
pipelines. A tokenizer splits raw text into smaller units called tokens, which 
may represent words, subwords, or individual characters depending on the 
tokenization strategy. Byte-pair encoding is a popular subword tokenization 
algorithm that iteratively merges the most frequent character pairs. WordPiece 
tokenization is used in BERT-based models and constructs vocabulary by 
maximizing the language model likelihood. SentencePiece is a language-agnostic 
tokenizer that treats the input as a raw stream of Unicode characters.

The transformer architecture relies on self-attention to compute representations 
of sequences. Multi-head attention allows the model to jointly attend to 
information from different representation subspaces at different positions. 
Positional encoding injects information about the relative or absolute position 
of tokens in the sequence. Layer normalization is applied before or after 
attention sublayers to stabilize training dynamics.

Embeddings are dense vector representations of tokens in a continuous 
high-dimensional space. Word embeddings capture semantic and syntactic 
relationships between words. Contextual embeddings produced by models like 
BERT and GPT encode meaning that depends on surrounding context. Sentence 
embeddings represent entire sentences as fixed-size vectors useful for 
semantic similarity and retrieval tasks.

Pre-training on large unlabeled corpora followed by fine-tuning on task-specific 
labeled datasets is the dominant paradigm in modern NLP. Masked language 
modeling is a pre-training objective where a fraction of input tokens are 
masked and the model learns to predict the masked tokens. Causal language 
modeling trains the model to predict the next token given all preceding tokens 
in an autoregressive fashion. Contrastive learning encourages representations 
of similar examples to be close in embedding space while pushing dissimilar 
examples apart.

Retrieval-augmented generation combines a dense retrieval system with a 
generative language model. The retriever selects relevant passages from a 
knowledge base given a query, and the generator conditions on both the query 
and retrieved passages to produce the output. Semantic retrieval uses dense 
vector similarity rather than keyword matching to find relevant documents. 
A context window defines the maximum number of tokens a language model can 
process in a single forward pass. Extending context windows enables models 
to handle longer documents and multi-document reasoning.

Named entity recognition identifies and classifies named entities such as 
persons, organizations, locations, and dates in unstructured text. Part-of-speech 
tagging assigns grammatical labels to each token including noun, verb, adjective, 
adverb, preposition, and conjunction. Dependency parsing analyzes the grammatical 
structure of sentences and establishes relationships between head words and 
their dependents. Coreference resolution links mentions that refer to the same 
entity across a document.

Sequence-to-sequence models learn mappings from input sequences to output 
sequences and are widely used in machine translation, summarization, and 
question answering. The encoder processes the input and produces a context 
vector while the decoder generates the output token by token. Beam search is 
a heuristic search algorithm used during decoding that explores the most 
promising partial hypotheses according to the model probability. Greedy decoding 
selects the highest probability token at each step but may miss globally 
optimal solutions. Temperature scaling controls the sharpness of the output 
probability distribution during generation.

Reinforcement learning from human feedback aligns language model behavior with 
human preferences. A reward model is trained on human comparisons of model 
outputs and is used to provide a scalar reward signal. Proximal policy 
optimization updates the language model policy to maximize expected reward 
while constraining the deviation from the original model via a KL divergence 
penalty. Constitutional AI introduces a set of principles used to guide model 
behavior through self-critique and revision.

Hallucination refers to the tendency of language models to generate plausible-sounding 
but factually incorrect or unsupported content. Grounding techniques attempt to 
anchor model outputs to verifiable facts in external knowledge sources. Chain-of-thought 
prompting encourages the model to generate intermediate reasoning steps before 
producing the final answer. Zero-shot prompting evaluates model performance 
without any task-specific examples. Few-shot prompting provides a small number 
of labeled examples within the prompt to guide the model.

Perplexity is a standard metric for evaluating language model quality, measuring 
how well the probability distribution predicted by the model matches the actual 
distribution of the test data. Cross-entropy loss is minimized during language 
model training and is directly related to perplexity. BLEU score measures the 
overlap between generated and reference translations using n-gram precision. 
ROUGE metrics evaluate summarization quality by comparing n-gram recall between 
system and reference summaries. BERTScore uses contextual embeddings to compute 
semantic similarity between hypothesis and reference texts.

Quantization reduces the numerical precision of model weights and activations 
to decrease memory footprint and increase inference speed. Knowledge distillation 
trains a smaller student model to mimic the output distribution of a larger 
teacher model. Low-rank adaptation introduces trainable rank decomposition 
matrices into each layer of a pre-trained model enabling efficient fine-tuning 
with far fewer trainable parameters. Mixture of experts architectures route 
each input to a subset of specialized expert networks selected by a learned 
gating mechanism.

Prompt engineering involves crafting effective input prompts to elicit desired 
behavior from language models. System prompts configure the model's persona, 
capabilities, and constraints. In-context learning allows models to adapt to 
new tasks based solely on examples provided in the input without any gradient 
updates. Instruction tuning fine-tunes language models on datasets of instruction 
and response pairs improving their ability to follow natural language instructions.

The vocabulary of a language model defines the set of tokens recognized by the 
tokenizer. Out-of-vocabulary tokens are those not present in the model vocabulary 
and must be handled through special unknown tokens or subword decomposition. 
Vocabulary size trades off coverage against computational efficiency. A larger 
vocabulary reduces the average number of tokens per word but increases the size 
of the embedding matrix and the output projection layer.

Softmax normalization converts raw logit scores into a probability distribution 
over the vocabulary. The feed-forward network within each transformer layer 
applies two linear transformations with a nonlinear activation function such 
as GELU or ReLU in between. Residual connections add the input of each sublayer 
to its output facilitating gradient flow during backpropagation through deep 
networks. Dropout regularization randomly zeroes activations during training 
to prevent overfitting.

Semantic similarity measures the degree to which two pieces of text convey 
the same meaning. Cosine similarity computes the angle between two embedding 
vectors and is commonly used as a similarity metric. Euclidean distance measures 
the straight-line distance between points in embedding space. Approximate nearest 
neighbor search algorithms such as FAISS enable efficient retrieval from large 
embedding databases. Vector databases store and index embeddings to support 
fast semantic search at scale.

Coreference chains link all mentions of the same entity within a document. 
Anaphora resolution is the subtask of identifying pronouns and resolving them 
to their antecedents. Discourse analysis examines how sentences relate to one 
another to form coherent text. Sentiment analysis classifies the emotional tone 
of text as positive, negative, or neutral. Aspect-based sentiment analysis 
identifies sentiment expressed toward specific aspects or attributes of entities.

Information extraction converts unstructured text into structured representations. 
Relation extraction identifies semantic relationships between entities such as 
was-born-in, is-ceo-of, or located-in. Event extraction identifies events and 
their participants described in text. Open information extraction discovers 
relations without a predefined schema by extracting subject predicate object 
triples directly from text.

Machine translation produces text in a target language that conveys the same 
meaning as the source text. Neural machine translation systems use encoder-decoder 
architectures trained end-to-end on parallel corpora. Back-translation augments 
training data by translating target language monolingual data to the source 
language. Cross-lingual models share representations across multiple languages 
enabling zero-shot transfer to low-resource languages.

Dialogue systems engage in multi-turn conversations with users to accomplish 
tasks or provide information. Task-oriented dialogue systems help users complete 
specific goals such as booking a restaurant or querying a database. Open-domain 
dialogue systems engage in unrestricted conversation. Dialogue state tracking 
maintains a structured representation of the conversation history. Natural 
language generation produces grammatically correct and contextually appropriate 
responses.

Text classification assigns predefined category labels to documents or sentences. 
Multi-label classification allows each example to be assigned multiple labels 
simultaneously. Hierarchical text classification organizes labels in a taxonomy 
and assigns labels at multiple levels of the hierarchy. Imbalanced datasets pose 
challenges for classification when some classes have far fewer examples than others.

Transfer learning leverages knowledge acquired during training on one task to 
improve performance on related tasks. Domain adaptation addresses the mismatch 
between source and target domains. Catastrophic forgetting occurs when a model 
trained on new tasks loses performance on previously learned tasks. Continual 
learning methods aim to accumulate knowledge across tasks while avoiding 
catastrophic forgetting.

Graph neural networks extend deep learning to graph-structured data and are 
applied to knowledge graph completion and reasoning. Knowledge graphs represent 
facts as triples of subject relation object. Entity embeddings in knowledge 
graphs capture the semantic properties of entities and their relationships. 
Link prediction estimates the likelihood of missing edges in knowledge graphs.

Active learning selects the most informative unlabeled examples to annotate 
reducing the labeling effort required to achieve high model performance. 
Uncertainty sampling selects examples where the model is least confident. 
Query by committee selects examples where a committee of models disagrees most.

Federated learning trains models across decentralized devices without sharing 
raw data preserving privacy. Differential privacy adds calibrated noise to 
model updates to provide formal privacy guarantees. Membership inference attacks 
attempt to determine whether a specific example was used in training a model.

Explainability methods attempt to shed light on how language models make 
predictions. Attention visualization displays attention weights to identify 
which parts of the input the model focuses on. Gradient-based attribution 
methods compute the gradient of the output with respect to the input to identify 
influential tokens. LIME approximates the model locally with an interpretable 
surrogate model. SHAP computes Shapley values to assign contributions to each 
input feature.

Bias in language models arises from biases present in training data and can 
lead to unfair or discriminatory outputs. Debiasing techniques attempt to remove 
or reduce unwanted biases while preserving model utility. Fairness metrics 
quantify disparities in model performance across demographic groups.

Evaluation benchmarks such as GLUE, SuperGLUE, and BIG-Bench assess model 
capabilities across a diverse range of natural language understanding tasks. 
Human evaluation remains essential for assessing qualities such as fluency, 
coherence, and factual accuracy that automated metrics may not fully capture.

The field of natural language processing continues to evolve rapidly with new 
architectures models datasets and evaluation paradigms emerging at an 
accelerating pace. Researchers continue to push the boundaries of what is 
possible with computational models of language expanding both the capabilities 
and our theoretical understanding of intelligent systems.
"""

# Additional AI terminology for vocabulary enrichment
AI_TERMS = [
    "tokenization", "tokenizer", "tokens", "embedding", "embeddings", "transformer",
    "transformers", "attention", "self-attention", "multi-head", "positional", "encoding",
    "decoder", "encoder", "autoregressive", "autoencoder", "variational", "generative",
    "discriminative", "backpropagation", "gradient", "optimizer", "Adam", "SGD",
    "learning", "rate", "scheduler", "warmup", "epoch", "batch", "minibatch",
    "overfitting", "underfitting", "regularization", "dropout", "normalization",
    "layer", "layers", "neuron", "neurons", "activation", "sigmoid", "softmax",
    "ReLU", "GELU", "tanh", "logit", "logits", "probability", "distribution",
    "perplexity", "entropy", "cross-entropy", "KL-divergence", "BLEU", "ROUGE",
    "BERTScore", "benchmark", "dataset", "corpus", "vocabulary", "lexicon",
    "bigram", "trigram", "unigram", "n-gram", "ngram", "language", "model",
    "BERT", "GPT", "LLM", "NLP", "AI", "ML", "DL", "NN", "CNN", "RNN", "LSTM",
    "GRU", "seq2seq", "fine-tuning", "pre-training", "pretraining", "finetuning",
    "hyperparameter", "hyperparameters", "inference", "hallucination", "grounding",
    "retrieval", "semantic", "syntactic", "pragmatic", "morphological", "lemma",
    "lemmatization", "stemming", "stopwords", "preprocessing", "postprocessing",
    "annotation", "labeling", "crowdsourcing", "inter-annotator", "agreement",
    "coreference", "anaphora", "cataphora", "discourse", "coherence", "cohesion",
    "summarization", "abstractive", "extractive", "paraphrase", "paraphrasing",
    "entailment", "contradiction", "inference", "reasoning", "commonsense",
    "knowledge", "graph", "ontology", "taxonomy", "hierarchy", "classification",
    "regression", "clustering", "dimensionality", "reduction", "PCA", "TSNE",
    "UMAP", "cosine", "similarity", "euclidean", "distance", "nearest", "neighbor",
    "retrieval-augmented", "generation", "RAG", "vector", "database", "FAISS",
    "quantization", "distillation", "pruning", "compression", "LoRA", "PEFT",
    "instruction", "tuning", "alignment", "RLHF", "reward", "proximal", "policy",
    "constitutional", "harmless", "helpful", "honest", "prompting", "zero-shot",
    "few-shot", "in-context", "chain-of-thought", "scratchpad", "system", "prompt",
    "completion", "generation", "sampling", "temperature", "nucleus", "top-k",
    "beam", "search", "greedy", "decoding", "token", "subword", "wordpiece",
    "sentencepiece", "BPE", "byte-pair", "unigram", "character", "phoneme",
    "morpheme", "syntax", "semantics", "pragmatics", "phonology", "parse",
    "parsing", "dependency", "constituency", "span", "phrase", "clause",
    "sentence", "document", "paragraph", "passage", "query", "context", "window",
    "truncation", "padding", "masking", "masked", "causal", "bidirectional",
    "unidirectional", "encoder-only", "decoder-only", "encoder-decoder",
    "cross-attention", "feed-forward", "residual", "connection", "skip",
    "layer-norm", "batch-norm", "weight", "weights", "parameters", "gradients",
    "loss", "objective", "task", "downstream", "upstream", "modality", "multimodal",
    "vision", "language", "audio", "speech", "recognition", "synthesis", "TTS",
    "ASR", "OCR", "translation", "multilingual", "cross-lingual", "zero-resource",
    "low-resource", "transfer", "domain", "adaptation", "continual", "catastrophic",
    "federated", "differential", "privacy", "fairness", "bias", "debiasing",
    "explainability", "interpretability", "attribution", "saliency", "attention",
    "probing", "mechanistic", "emergent", "capability", "scaling", "law",
    "architecture", "parameter", "billion", "trillion", "compute", "FLOPS",
    "throughput", "latency", "efficiency", "parallelism", "tensor", "matrix"
]


# Common English words — prevents false positives on everyday vocabulary
COMMON_WORDS = [
    # Core function words & verbs
    "the","be","to","of","and","a","in","that","have","it","for","not","on","with",
    "he","she","they","we","you","do","at","this","but","his","her","by","from","or",
    "an","all","there","which","one","would","what","so","up","out","if","about","who",
    "get","go","me","when","make","can","like","time","no","just","him","know","take",
    "into","your","some","could","them","see","other","than","then","now","look",
    "only","come","its","over","think","also","back","after","use","two","how","our",
    "work","first","well","way","even","new","want","because","any","these","give","day",
    "most","us","between","need","large","often","hand","high","place","hold","turn",
    "was","were","are","has","had","been","will","did","does","said","say","made","may",
    # Common verbs
    "feel","feels","felt","find","found","set","show","try","call","keep","let",
    "begin","seem","help","talk","start","might","move","play","run","live","believe",
    "bring","happen","write","provide","sit","stand","lose","pay","meet","include",
    "continue","learn","change","lead","understand","watch","follow","stop","create",
    "read","spend","grow","open","walk","win","offer","remember","love","consider",
    "appear","buy","wait","serve","die","send","expect","build","stay","fall","cut",
    "reach","remain","suggest","raise","pass","sell","require","report","decide",
    "hear","return","eat","apply","explain","develop","describe","perform","allow",
    "increase","reduce","produce","accept","agree","affect","assume","attempt",
    "cause","choose","claim","compare","complete","contain","control","cover",
    "define","demonstrate","determine","discuss","enable","establish","exist",
    "extend","form","identify","improve","involve","measure","observe","occur",
    "prevent","process","recognize","relate","release","rely","replace","respond",
    "reveal","support","refer","indicate","implement","obtain","achieve","address",
    "assess","associate","calculate","collect","combine","conduct","confirm","connect",
    "construct","contribute","convert","detect","distribute","enhance","ensure",
    "evaluate","examine","execute","generate","integrate","interpret","introduce",
    "investigate","maintain","manage","modify","organize","overcome","predict",
    "propose","resolve","review","select","separate","solve","store","summarize",
    "test","utilize","validate","verify","present","represent","explore",
    # Adjectives
    "good","new","first","last","long","great","little","own","right","big","high",
    "different","small","next","early","young","important","bad","same","able","each",
    "free","real","best","sure","far","low","local","strong","clear","true","short",
    "simple","hard","full","human","known","specific","possible","whole","main",
    "recent","common","general","single","particular","open","available","likely",
    "current","basic","direct","previous","personal","old","final","significant",
    "complete","social","dark","light","deep","wide","heavy","easy","slow","fast",
    "cold","hot","warm","cool","modern","traditional","original","natural","special",
    "useful","necessary","similar","various","several","certain","few","many","both",
    "another","such","rather","quite","already","still","even","much","more","less",
    "effective","efficient","accurate","robust","complex","powerful","advanced",
    "standard","typical","normal","unique","multiple","primary","secondary",
    "additional","external","internal","initial","overall","public","national",
    # Nouns
    "year","people","way","day","man","woman","child","world","life","part","place",
    "case","week","system","question","government","number","night","point","home",
    "water","room","area","money","story","fact","month","lot","study","book","eye",
    "job","word","business","issue","side","kind","head","house","service","friend",
    "power","hour","game","line","end","name","land","term","city","community",
    "group","problem","idea","body","information","level","office","door","health",
    "person","art","war","history","party","result","morning","reason","research",
    "girl","guy","moment","air","teacher","force","education","subject","series",
    "plan","detail","course","method","approach","example","type","class","value",
    "view","role","action","effect","step","rate","piece","thing","things",
    "something","anything","nothing","everything","someone","anyone","everyone",
    "ability","activity","amount","analysis","aspect","attention","behaviour",
    "benefit","choice","combination","component","condition","content","decision",
    "description","design","development","difference","direction","discussion",
    "element","environment","evidence","experience","feature","focus","function",
    "goal","impact","knowledge","lack","limitation","list","loss","nature","network",
    "note","objective","operation","opportunity","output","performance","position",
    "purpose","quality","range","relationship","response","section","situation",
    "solution","source","structure","success","technique","technology","theory",
    "understanding","version","error","errors","text","input","user","process",
    # Adverbs & prepositions
    "very","also","just","now","here","there","when","where","while","then",
    "more","most","less","least","quite","rather","really","never","always","often",
    "usually","sometimes","already","still","yet","soon","again","once","twice",
    "together","however","therefore","thus","furthermore","moreover","although",
    "though","despite","during","before","after","since","until","unless","whether",
    "within","without","across","along","among","around","behind","below","beside",
    "beyond","except","inside","near","outside","through","throughout","toward",
    "under","upon","above","against","approximately","currently","effectively",
    "especially","generally","highly","increasingly","particularly","previously",
    "recently","relatively","significantly","specifically","successfully","typically",
    "widely","automatically","directly","explicitly","frequently","globally","largely",
    "mainly","naturally","normally","primarily","quickly","randomly","rarely",
    "simultaneously","slightly","strongly","substantially","sufficiently","virtually",
]


class CorpusBuilder:
    """Builds and manages the movie domain-specific AI/NLP corpus."""

    def __init__(self):
        self.raw_text = ""
        self.tokens = []
        self.word_freq = Counter()
        self.vocabulary = set()
        self.bigrams = Counter()
        self.word_count = 0

    def load_seed_corpus(self):
        """Load the embedded seed corpus."""
        self.raw_text = SEED_CORPUS
        return self

    def preprocess(self):
        """Tokenize and clean the corpus text."""
        text = self.raw_text.lower()
        # Remove punctuation except apostrophes within words
        text = re.sub(r"[^\w\s'-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        # Tokenize
        raw_tokens = text.split()
        # Clean tokens
        self.tokens = []
        for tok in raw_tokens:
            tok = tok.strip("'-_")
            if tok and re.match(r'^[a-z][a-z\'-]*$', tok) and len(tok) > 1:
                self.tokens.append(tok)
        # Enrich with AI terms
        for term in AI_TERMS:
            normalized = term.lower().strip("'-_")
            if normalized and len(normalized) > 1:
                self.tokens.extend([normalized] * 3)  # weight domain terms
        # Enrich with common English words (weight ×6 — prevents false positives)
        for word in COMMON_WORDS:
            normalized = word.lower().strip("'-_")
            if normalized and len(normalized) > 1 and re.match(r'^[a-z]+$', normalized):
                self.tokens.extend([normalized] * 10)
        self.word_count = len(self.tokens)
        return self

    def build_frequency_table(self):
        """Build unigram frequency table."""
        self.word_freq = Counter(self.tokens)
        self.vocabulary = set(self.word_freq.keys())
        return self

    def build_bigrams(self):
        """Build bigram frequency table."""
        for w1, w2 in zip(self.tokens[:-1], self.tokens[1:]):
            self.bigrams[(w1, w2)] += 1
        return self

    def get_stats(self):
        return {
            "total_tokens": self.word_count,
            "unique_words": len(self.vocabulary),
            "total_bigrams": len(self.bigrams),
            "top_20": self.word_freq.most_common(20)
        }

    def load_from_json(self, path: str) -> bool:
        """
        Load a pre-built corpus from corpus.json with validation.
        Returns True if successful, False if file not found or invalid.
        """
        import os
        import logging
        logger = logging.getLogger(__name__)
        
        if not os.path.exists(path):
            logger.warning(f"Corpus file not found: {path}")
            return False
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Validate required structure
            required_keys = {"tokens", "word_freq", "vocabulary", "bigrams"}
            if not required_keys.issubset(set(data.keys())):
                missing = required_keys - set(data.keys())
                raise ValueError(f"Missing keys: {missing}")
            
            # Load with type validation
            self.tokens    = data["tokens"]
            self.word_freq = Counter(data["word_freq"])
            self.vocabulary = set(data["vocabulary"])
            self.bigrams   = Counter({tuple(k.split("|", 1)): v
                                      for k, v in data["bigrams"].items()})
            self.word_count = len(self.tokens)
            self._source   = path
            
            # Enrich with common words
            for word in COMMON_WORDS:
                normalized = word.lower().strip("\'-_")
                if normalized and len(normalized) > 1 and re.match(r'^[a-z]+$', normalized):
                    freq = self.word_freq.get(normalized, 0)
                    if freq < 10:
                        self.tokens.extend([normalized] * 10)
                        self.word_freq[normalized] = max(freq, 10)
                        self.vocabulary.add(normalized)
            self.word_count = len(self.tokens)
            logger.info(f"Loaded: {len(self.vocabulary)} words")
            return True
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {path}: {e}")
            return False
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Corrupt corpus: {e}")
            return False
        except IOError as e:
            logger.error(f"Cannot read {path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False

    def build(self):
        """
        Run full pipeline.
        Priority: corpus.json (from build_corpus.py) > embedded seed text.
        """
        import os
        json_path = os.path.join(os.path.dirname(__file__), "corpus.json")
        if self.load_from_json(json_path):
            print(f"Loaded corpus from {json_path}")
            print(
                f"  {self.word_count:,} tokens | {len(self.vocabulary):,} unique words | "
                f"{len(self.bigrams):,} bigrams"
            )
        else:
            print("corpus.json not found - using embedded seed corpus.")
            print("   Run  python build_corpus.py  to build from IMDB Dataset.csv (repo root).")
            self.load_seed_corpus()
            self.preprocess()
            self.build_frequency_table()
            self.build_bigrams()
        return self


if __name__ == "__main__":
    cb = CorpusBuilder().build()
    stats = cb.get_stats()
    print(f"Corpus built: {stats['total_tokens']} tokens, {stats['unique_words']} unique words")
