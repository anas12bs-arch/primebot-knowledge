---
title: "AlbumentationsX: One Augmentation Pipeline for Images and Related Annotations"
source: arxiv
url: https://arxiv.org/abs/2608.11123v1
category: ai_models
relevance_score: 5
matched_keywords: [image, support, train, training, video]
fetched_at: 2026-08-12T03:07:46.275846+00:00
published: 2026-08-11T16:34:47Z
status: raw
---

# AlbumentationsX: One Augmentation Pipeline for Images and Related Annotations

Augmentation can corrupt a training example when an image and its annotations receive different random changes. A crop must use the same coordinates for the image, mask, boxes, keypoints, stereo views, video frames, or volume. Code paths that choose these values separately can silently misalign the data.   AlbumentationsX keeps the transform list, probabilities, annotation settings, and random seed in one Compose object. Each call chooses random values once and applies them to every supported pa

[Fuente](https://arxiv.org/abs/2608.11123v1)
