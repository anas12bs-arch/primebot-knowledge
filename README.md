# primebot-knowledge

Motor de investigación autónomo 24/7. GitHub Actions escanea fuentes gratuitas
cada 30 minutos, filtra por relevancia (heurística, sin gastar tokens de
Claude) y guarda notas en `notes/`. Un sync local copia esas notas a la
bóveda de Obsidian sin convertirla en repo git.

## Cómo funciona

```
GitHub Actions (cada 30 min, 24/7, gratis en repo público)
  -> scripts/run_scan.py
     -> fetch_hackernews.py  (Algolia HN Search API)
     -> fetch_arxiv.py       (arXiv API oficial)
     -> fetch_rss.py         (blogs de labs de IA, SaaStr, a16z, etc.)
     -> fetch_reddit.py      (best-effort, Reddit bloquea bots -> normalmente 0 resultados)
  -> filtro de relevancia (config/keywords.yml, scoring por keyword, sin LLM)
  -> dedupe (data/seen.json)
  -> notes/<categoria>/<fecha>-<slug>.md
  -> git commit + push

Mac local (launchd, cada 30 min)
  -> sync/sync_to_obsidian.sh
     -> git pull del repo (cache en ~/.primebot-knowledge-cache)
     -> rsync de notes/ -> boveda/wiki/auto-research/
```

La bóveda de Obsidian real (con tus notas de negocio, clientes, etc.) nunca
se toca como repo git. Solo se le copian archivos .md ya generados.

## Categorías que cubre

- `ai_models`: modelos de IA nuevos, video generation, arquitecturas
- `automation`: n8n, Make, agentes autónomos, workflow automation
- `sales_psychology`: Cialdini, behavioral economics, objection handling
- `marketing_growth`: growth hacking, CRO, viral loops
- `business_models`: SaaS pricing, unit economics, LTV/CAC
- `fiscal_legal`: VAT UE, fiscalidad autónomos

Editar `config/keywords.yml` para agregar/quitar keywords o categorías
nuevas — no requiere tocar código.

## Setup (una sola vez)

1. Repo ya está en GitHub: https://github.com/anas12bs-arch/primebot-knowledge
2. Activar el sync local:
   ```bash
   cp sync/com.primebot.knowledgesync.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.primebot.knowledgesync.plist
   ```
3. Verificar que corre:
   ```bash
   tail -f sync/sync.log
   ```

## Mantenimiento

- **Agregar keywords/categorías nuevas**: editar `config/keywords.yml`, commit, push.
- **Ver qué se ha capturado**: `notes/` en el repo, o `wiki/auto-research/` en Obsidian.
- **Pausar el scan**: desactivar el workflow en GitHub Actions (tab Actions del repo).
- **Pausar el sync local**: `launchctl unload ~/Library/LaunchAgents/com.primebot.knowledgesync.plist`

## Límites honestos

- Reddit bloquea scraping automatizado sistemáticamente (403 con cualquier
  user-agent). El fetcher se deja como best-effort pero normalmente no trae
  nada — cubierto en su lugar con más fuentes RSS.
- El filtro de relevancia es heurístico (keyword matching + scoring), no usa
  ningún LLM. Es rápido y gratis pero menos inteligente que un filtro con IA.
  Se puede ajustar el threshold por categoría en `config/keywords.yml`.
- arXiv publica en tandas, no continuamente — su ventana de "reciente" es
  72h en vez de las 36h del resto de fuentes.
- Esto NO reemplaza investigación profunda / ingeniería inversa de modelos
  específicos — eso sigue siendo trabajo de sesión con Claude, aplicado
  sobre este material bruto ya filtrado y guardado.
