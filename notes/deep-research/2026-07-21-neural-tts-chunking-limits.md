---
gap: neural-tts-chunking-limits
query: "autoregressive text-to-speech context window text chunking long-form generation hallucination degradation"
status: gathered
sources_count: 14
generated_at: 2026-07-21T22:45:52.062981+00:00
---

# Deep research: autoregressive text-to-speech context window text chunking long-form generation hallucination degradation

## Contexto (Wikipedia)

### Context window
The context window of a large language model (LLM) is the maximum amount of text or other tokenized input available to the model at one time when generating output. It is usually measured in tokens, which are units produced by the model's tokenizer rather than words or characters. In practical terms, the context window is the material the model can "see" while producing response; anything outside that window is not directly available unless it is summarized, retrieved, or provided again. A longer context window can allow a model to work with longer prompts, conversations, documents, codebases,
[Fuente](https://en.wikipedia.org/wiki/Context_window)

## Papers (arXiv)

### DELTA-TTS: Adapting Autoregressive Model into Diffusion Language Model for Text-to-Speech (2026-07-05)
Autoregressive (AR) text-to-speech (TTS) models generate discrete speech tokens sequentially, which makes inference slow and can degrade robustness by propagating local errors and hallucinations. This limitation stems from their left-to-right AR commitment: each token must be determined before future speech-token context is available. However, such ordering is not an inherent requirement for TTS, as the full input text is available before synthesis. In this paper, we introduce DELTA-TTS, a lightweight LoRA-based adaptation framework that converts a pretrained AR TTS model into a discrete diffu
[Fuente](https://arxiv.org/abs/2607.04140v1)

### Evaluating Long-form Text-to-Speech: Comparing the Ratings of Sentences and Paragraphs (2019-09-09)
Text-to-speech systems are typically evaluated on single sentences. When long-form content, such as data consisting of full paragraphs or dialogues is considered, evaluating sentences in isolation is not always appropriate as the context in which the sentences are synthesized is missing. In this paper, we investigate three different ways of evaluating the naturalness of long-form text-to-speech synthesis. We compare the results obtained from evaluating sentences in isolation, evaluating whole paragraphs of speech, and presenting a selection of speech or text as context and evaluating the subse
[Fuente](https://arxiv.org/abs/1909.03965v1)

### Recurrent Neural Network based Part-of-Speech Tagger for Code-Mixed Social Media Text (2016-11-15)
This paper describes Centre for Development of Advanced Computing's (CDACM) submission to the shared task-'Tool Contest on POS tagging for Code-Mixed Indian Social Media (Facebook, Twitter, and Whatsapp) Text', collocated with ICON-2016. The shared task was to predict Part of Speech (POS) tag at word level for a given text. The code-mixed text is generated mostly on social media by multilingual users. The presence of the multilingual words, transliterations, and spelling variations make such content linguistically complex. In this paper, we propose an approach to POS tag code-mixed social medi
[Fuente](https://arxiv.org/abs/1611.04989v2)

### Non-Autoregressive Neural Text-to-Speech (2019-05-21)
In this work, we propose ParaNet, a non-autoregressive seq2seq model that converts text to spectrogram. It is fully convolutional and brings 46.7 times speed-up over the lightweight Deep Voice 3 at synthesis, while obtaining reasonably good speech quality. ParaNet also produces stable alignment between text and speech on the challenging test sentences by iteratively improving the attention in a layer-by-layer manner. Furthermore, we build the parallel text-to-speech system and test various parallel neural vocoders, which can synthesize speech from text through a single feed-forward pass. We al
[Fuente](https://arxiv.org/abs/1905.08459v3)

### Multimodal Hate Speech Detection from Bengali Memes and Texts (2022-04-19)
Numerous machine learning (ML) and deep learning (DL)-based approaches have been proposed to utilize textual data from social media for anti-social behavior analysis like cyberbullying, fake news detection, and identification of hate speech mainly for highly-resourced languages such as English. However, despite having a lot of diversity and millions of native speakers, some languages like Bengali are under-resourced, which is due to a lack of computational resources for natural language processing (NLP). Similar to other languages, Bengali social media contents also include images along with t
[Fuente](https://arxiv.org/abs/2204.10196v3)

## Papers (Semantic Scholar)

(sin resultados)

## Discusión práctica (HackerNews, all-time, >40 puntos)

### LongRoPE: Extending LLM Context Window Beyond 2M Tokens (2024-02-22)
142 puntos, 46 comentarios
[Fuente](https://arxiv.org/abs/2402.13753)

### 100K Context Windows (2023-05-11)
924 puntos, 389 comentarios
[Fuente](https://www.anthropic.com/index/100k-context-windows)

### The Secret Sauce behind 100K context window in LLMs: all tricks in one place (2023-06-17)
474 puntos, 99 comentarios
[Fuente](https://blog.gopenai.com/how-to-speed-up-llms-and-use-100k-context-window-all-tricks-in-one-place-ffd40577b4c)

### The RAG Obituary: Killed by agents, buried by context windows (2025-10-01)
290 puntos, 179 comentarios
[Fuente](https://www.nicolasbustamante.com/p/the-rag-obituary-killed-by-agents)

### Don't trust large context windows (2026-06-14)
277 puntos, 195 comentarios
[Fuente](https://garrit.xyz/posts/2026-05-06-dont-trust-large-context-windows)

### GPT-4 Update: 32K Context Window Now for All Users (2023-11-03)
208 puntos, 140 comentarios
[Fuente](https://github.com/spdustin/ChatGPT-AutoExpert/blob/main/_system-prompts/all_tools.md)

### Grok 4 Fast now has 2M context window (2025-11-09)
194 puntos, 281 comentarios
[Fuente](https://docs.x.ai/docs/models)

### Who needs Git when you have 1M context windows? (2025-10-03)
177 puntos, 192 comentarios
[Fuente](https://www.alexmolas.com/2025/07/28/unexpected-benefit-llm.html)


---

## Síntesis

PENDIENTE — Claude: sintetizar en sesión. Formato: mecanismo → implicación práctica para Anas → condición límite. Solo con las fuentes de arriba.
