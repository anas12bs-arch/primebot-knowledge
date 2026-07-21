# Gaps de conocimiento pendientes

Formato: `- [ ] slug-corto | query de búsqueda en inglés`

El worker (deep-research.yml) procesa hasta 3 por ejecución, agrega
evidencia de Wikipedia + arXiv + Semantic Scholar + HackerNews, y escribe
un brief citado en notes/deep-research/ (que fluye a Obsidian).

Quién añade gaps aquí:
1. Claude en sesión, cuando detecta que le falta profundidad en algo que Anas preguntó.
2. self_audit.py, cuando una categoría del scanner está muerta (0 notas).
3. Anas manualmente, cuando quiera investigar un tema.

## Pendientes (prioritario — investigar profundo, sesión 4)

### VOZ CLONADA / TTS LOCAL (para OpenMontage — Voicebox: chatterbox_turbo, luxtts, kokoro)
Objetivo: entender de verdad por qué los motores de clonación de voz locales que usamos
(Resemble AI Chatterbox / Chatterbox Turbo, LuxTTS) fallan como fallan -- alucinan
palabras con textos largos, no exponen control de velocidad/ritmo por API, y LuxTTS se
cuelga sin avisar en Apple Silicon con 8GB. Se hostean en
~/Desktop/voicebox (fork local de jamiepine/voicebox). Contexto ya confirmado en sesión
(2026-07-21/22): con chunks de ~800 caracteres alucina texto inventado; con chunks de
~250 genera correcto pero a 165-180 palabras/min (demasiado rápido, sin dial de
velocidad expuesto); el fix aplicado hoy fue post-procesar con ffmpeg atempo, no un
arreglo del modelo en sí. Quiero saber si hay una forma mejor, nativa del modelo.

- [ ] chatterbox-tts-architecture | Chatterbox TTS Resemble AI open source zero-shot voice cloning architecture quality benchmarks
- [ ] neural-tts-chunking-limits | autoregressive text-to-speech context window text chunking long-form generation hallucination degradation
- [ ] tts-speaking-rate-control | neural TTS speaking rate prosody duration control classifier-free guidance cfg weight speed parameter
- [ ] local-voice-cloning-apple-silicon | open source voice cloning TTS models Apple Silicon MPS performance comparison memory stability

### TÉCNICA DE EDICIÓN & MOTION DESIGN (para hyperframes / Remotion / OpenMontage)
Objetivo: nutrir el stack de vídeo con técnica real y efectos modernos, aplicables en
composiciones HTML/CSS/GSAP (hyperframes), React (Remotion) y pipeline ffmpeg (OpenMontage).

- [x] kinetic-typography-technique | kinetic typography animation principles timing legibility motion text design readability  (done 2026-07-19)
- [x] animation-easing-timing | easing functions animation timing principles anticipation overshoot follow-through motion perception  (done 2026-07-19)
- [x] webgl-shader-transitions | GLSL fragment shader video transitions displacement dissolve warp effects techniques  (done 2026-07-19)
- [x] modern-motion-effects | contemporary motion graphics effects glitch datamosh chromatic aberration RGB split displacement trends  (done 2026-07-19)
- [x] edit-pacing-attention | film editing pacing shot length cutting rate attention cognitive load viewer engagement empirical study  (done 2026-07-19)
- [x] scene-transition-grammar | film transition grammar match cut J-cut L-cut smash cut visual continuity editing theory  (done 2026-07-19)
- [x] visual-saliency-attention | visual saliency models eye tracking gaze prediction screen composition where viewers look  (done 2026-07-20)
- [x] color-grading-motion | color grading color science LUT contrast curves film emulation digital video look  (done 2026-07-20)
- [x] film-grain-halation-emulation | film grain synthesis halation bloom gate weave texture emulation digital video realism  (done 2026-07-20)
- [x] audio-reactive-visuals | audio reactive visualization FFT spectral analysis beat detection music driven animation sync  (done 2026-07-20)
- [x] video-compositing-techniques | alpha compositing premultiplied alpha matte keying blend modes layer compositing  (done 2026-07-20)
- [x] parallax-depth-2-5d | 2.5D parallax depth map camera projection still image animation monocular depth estimation  (done 2026-07-20)
- [x] procedural-motion-graphics | procedural generation motion graphics parametric animation generative design noise fields  (done 2026-07-21)
- [x] programmatic-video-rendering | programmatic video rendering React Remotion headless browser deterministic frame capture pipeline  (done 2026-07-21)

### VIDEO & HIGGSFIELD
- [x] higgsfield-video-analysis | how Higgsfield analyzes videos frame-level feature extraction temporal dynamics CNN models  (done 2026-07-14)
- [x] viral-hook-patterns | micro-patterns in first 3 seconds that cause viewers to stop scroll TikTok Reels Shorts  (done 2026-07-14)
- [x] retention-curve-mechanics | how retention curves work viewer drop-off points audience retention video length  (done 2026-07-14)

### YOUTUBE — FOCO ACTIVO (canal Straight Face, sesión 2026-07-20)
Objetivo: cubrir TODO lo relacionado con hacer crecer un canal de YouTube faceless de
narrativa (guion, edición, audio, miniaturas, descripciones, algoritmo) sin esperar a
que falte para pedirlo. Se reengorda este bloque cada sesión que toque YouTube.
- [x] youtube-algorithm-impressions-2025 | YouTube recommendation algorithm impressions click-through-rate suggested videos ranking signals 2025  (done 2026-07-21)
- [ ] youtube-new-channel-cold-start | new YouTube channel cold start algorithm behavior zero subscriber seed distribution test audience
- [ ] youtube-thumbnail-ctr-psychology | YouTube thumbnail design click-through-rate psychology contrast face expression composition studies
- [ ] youtube-title-click-psychology | video title curiosity gap clickbait threshold psychology headline click-through research
- [ ] youtube-description-seo | YouTube video description SEO keyword optimization search ranking metadata best practices
- [ ] youtube-chapters-endscreens-cards | YouTube chapters end screens cards optimal placement viewer navigation retention impact
- [ ] youtube-audio-mastering-narration | voiceover narration audio mastering loudness normalization EQ compression podcast documentary standards
- [ ] youtube-analytics-retention-graph | YouTube Studio analytics audience retention graph interpretation absolute vs relative retention drop-off diagnosis
- [ ] documentary-narration-script-structure | true crime documentary narration script structure pacing information reveal ordering techniques
- [ ] youtube-watch-time-vs-ctr-weighting | YouTube ranking watch time versus click-through-rate weighting session duration signals
- [ ] youtube-shorts-to-longform-funnel | YouTube Shorts driving traffic to long-form videos funnel conversion strategies channel growth
- [ ] voice-cloning-tts-narration-quality | AI voice cloning text-to-speech narration quality naturalness prosody for video documentary use

### CASOS CRIMINALES — VERIFICACIÓN PARA GUIONES (canal Deep Sea)
- [x] gardner-museum-heist | Isabella Stewart Gardner Museum 1990 art theft timeline 81 minutes fake police guards handcuffed stolen paintings value unsolved  (done 2026-07-16)
- [x] belenko-mig25-defection | Viktor Belenko 1976 MiG-25 defection Japan Hakodate flight fuel radar evasion Soviet intelligence damage  (done 2026-07-16)
- [x] mabhouh-dubai-assassination | Mahmoud al-Mabhouh Dubai 2010 assassination Mossad agents fake passports hotel CCTV forensic evidence  (done 2026-07-16)
- [x] qusay-iraq-central-bank | Qusay Hussein 2003 Iraq Central Bank one billion dollars removal handwritten note trucks  (done 2026-07-17)
- [x] ghosn-escape-japan | Carlos Ghosn 2019 escape Japan audio equipment case Osaka private jet Michael Taylor operation details  (done 2026-07-17)
- [x] tipton-lottery-hack | Eddie Tipton lottery random number generator rootkit hack Multi-State Lottery Association conviction details  (done 2026-07-17)
- [x] vastberga-helicopter-heist | Vastberga G4S cash depot helicopter heist Stockholm 2009 police helicopter hangar fake bombs planning  (done 2026-07-18)
- [x] silk-road-ulbricht | Silk Road Ross Ulbricht marketplace reputation system escrow operational security capture details  (done 2026-07-18)

### DROPSHIPPING & E-COMMERCE
- [x] winning-products-2025 | product characteristics high-margin low-weight fast-shipping winning dropshipping niches  (done 2026-07-15)
- [x] dropshipping-margin-math | supplier cost CAP pricing elasticity profit margins competitive analysis  (done 2026-07-15)
- [x] international-shipping-2025 | DHL FedEx UPS costs regions customs tariffs import taxes clearance time  (done 2026-07-15)
- [x] product-bundling-strategy | bundling psychology cross-sell upsell anchor pricing complementary products  (done 2026-07-16)

### TIKTOK & ALGORITHM
- [x] tiktok-fyp-algorithm-2025 | TikTok For You Page recommendation system watch time engagement signal ranking  (done 2026-07-16)
- [x] tiktok-organic-growth | seed strategy posting time hashtag strategy duet stitch growth tactics  (done 2026-07-16)
- [x] reels-vs-shorts-algorithm | YouTube Shorts vs Instagram Reels vs TikTok algorithm differences 2025  (done 2026-07-18)

### CONVERSION & PRICING
- [ ] conversion-rate-optimization | landing page checkout funnel friction CRO methodology frameworks
- [ ] price-anchoring-empirical | price anchoring studies e-commerce psychology charm pricing prestige pricing
- [ ] urgency-scarcity-conversion | scarcity countdown timers limited inventory conversion rate impact studies
- [ ] landing-page-copywriting | copywriting techniques persuasion framework value proposition benefit hierarchy

### META ADS & PAID
- [ ] meta-ads-roas-2025 | Facebook Instagram ads ROAS optimization audience targeting creative testing 2025
- [ ] cpc-ctr-benchmarks-ecommerce | cost-per-click CTR benchmarks by industry e-commerce conversion benchmarks

### DONE (anterior)
- [x] improve-sources-fiscal-legal | (done 2026-07-11)
- [x] improve-sources-business-models | (done 2026-07-11)
- [x] improve-sources-marketing-growth | (done 2026-07-11)
- [ ] ai-video-generation-landscape |
- [ ] b2b-pricing-anchoring |
- [ ] eu-vat-digital-freelancer |

## Completados
