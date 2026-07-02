---
name: awesome-design-md
description: 提供 69 个来自知名网站（Stripe、Apple、Vercel、Claude、Notion、Figma 等）的 DESIGN.md 设计系统文件。每个 DESIGN.md 包含完整的视觉主题、色彩体系、排版规则、组件样式、布局原则、阴影层级和响应式行为。当用户要求「做一个看起来像 XXX 的页面」「参考 XXX 的设计风格」「使用 XXX 的设计系统」「仿 XXX 的 UI」「pixel-perfect 还原 XXX 风格」「design like Stripe/Apple/Vercel」或需要获取某个品牌的完整设计规范来生成前端代码时使用。也适用于需要精确的色值、字体、间距、阴影参数来构建高保真 UI 的场景。
---

# Awesome DESIGN.md

69 个来自真实网站的 DESIGN.md 设计系统文件。每个文件是完整的设计规范，包含色值、字体、间距、组件样式、阴影系统、响应式规则等，可直接用于生成高保真 UI。

## 使用方式

1. 根据用户描述的品牌/风格，从下方索引中找到对应的 `references/{file}`
2. 读取该 DESIGN.md 文件，获取完整设计规范
3. 按规范中的色值、字体、间距、组件样式等参数生成前端代码

支持的品牌包括：Stripe、Apple、Vercel、Claude、Notion、Figma、Linear、Supabase、Airbnb、Nike、Tesla、SpaceX、Spotify 等 69 个。

## DESIGN.md 文件结构

每个文件遵循 Google Stitch DESIGN.md 格式，包含以下章节：

| # | 章节 | 内容 |
|---|------|------|
| 1 | Visual Theme & Atmosphere | 视觉主题、氛围、设计哲学 |
| 2 | Color Palette & Roles | 语义化命名 + HEX 色值 + 功能角色 |
| 3 | Typography Rules | 字体族、完整排版层级表 |
| 4 | Component Stylings | 按钮、卡片、输入框、导航（含各状态） |
| 5 | Layout Principles | 间距体系、网格、留白哲学 |
| 6 | Depth & Elevation | 阴影系统、表面层级 |
| 7 | Do's and Don'ts | 设计护栏和反模式 |
| 8 | Responsive Behavior | 断点、触摸目标、折叠策略 |
| 9 | Agent Prompt Guide | 快速色彩参考、即用型提示词 |

## 品牌索引

### AI & LLM Platforms

- **Claude** — Anthropic's AI assistant. Warm terracotta accent, clean editorial layout. — `references/claude.md`
- **Cohere** — Enterprise AI platform. Vibrant gradients, data-rich dashboard aesthetic. — `references/cohere.md`
- **Cursor** — AI-first code editor. Sleek dark interface, gradient accents. — `references/cursor.md`
- **Elevenlabs** — AI voice platform. Dark cinematic UI, audio-waveform aesthetics. — `references/elevenlabs.md`
- **Lovable** — AI full-stack builder. Playful gradients, friendly dev aesthetic. — `references/lovable.md`
- **Minimax** — AI model provider. Bold dark interface with neon accents. — `references/minimax.md`
- **Mistral.ai** — Open-weight LLM provider. French-engineered minimalism, purple-toned. — `references/mistral.ai.md`
- **Ollama** — Run LLMs locally. Terminal-first, monochrome simplicity. — `references/ollama.md`
- **Opencode.ai** — AI coding platform. Developer-centric dark theme. — `references/opencode.ai.md`
- **Replicate** — Run ML models via API. Clean white canvas, code-forward. — `references/replicate.md`
- **Runwayml** — AI video generation. Cinematic dark UI, media-rich layout. — `references/runwayml.md`
- **Together.ai** — Open-source AI infrastructure. Technical, blueprint-style design. — `references/together.ai.md`
- **Voltagent** — AI agent framework. Void-black canvas, emerald accent, terminal-native. — `references/voltagent.md`
- **X.ai** — Elon Musk's AI lab. Stark monochrome, futuristic minimalism. — `references/x.ai.md`

### Developer Tools & IDEs

- **Expo** — React Native platform. Dark theme, tight letter-spacing, code-centric. — `references/expo.md`
- **Raycast** — Productivity launcher. Sleek dark chrome, vibrant gradient accents. — `references/raycast.md`
- **Superhuman** — Fast email client. Premium dark UI, keyboard-first, purple glow. — `references/superhuman.md`
- **Vercel** — Frontend deployment. Black and white precision, Geist font. — `references/vercel.md`
- **Warp** — Modern terminal. Dark IDE-like interface, block-based command UI. — `references/warp.md`

### Backend, Database & DevOps

- **Airtable** — Spreadsheet-database hybrid. Colorful, friendly, structured data aesthetic. — `references/airtable.md`
- **Clickhouse** — Fast analytics database. Yellow-accented, technical documentation style. — `references/clickhouse.md`
- **Composio** — Tool integration platform. Modern dark with colorful integration icons. — `references/composio.md`
- **Hashicorp** — Infrastructure automation. Enterprise-clean, black and white. — `references/hashicorp.md`
- **MongoDB** — Document database. Green leaf branding, developer documentation focus. — `references/mongodb.md`
- **Posthog** — Product analytics. Playful hedgehog branding, developer-friendly dark UI. — `references/posthog.md`
- **Sanity** — Headless CMS. Red accent, content-first editorial layout. — `references/sanity.md`
- **Sentry** — Error monitoring. Dark dashboard, data-dense, pink-purple accent. — `references/sentry.md`
- **Supabase** — Open-source Firebase alternative. Dark emerald theme, code-first. — `references/supabase.md`

### Productivity & SaaS

- **Cal** — Open-source scheduling. Clean neutral UI, developer-oriented simplicity. — `references/cal.md`
- **Clay** — Creative agency. Organic shapes, soft gradients, art-directed layout. — `references/clay.md`
- **Intercom** — Customer messaging. Friendly blue palette, conversational UI patterns. — `references/intercom.md`
- **Linear.app** — Project management. Ultra-minimal, precise, purple accent. — `references/linear.app.md`
- **Mintlify** — Documentation platform. Clean, green-accented, reading-optimized. — `references/mintlify.md`
- **Notion** — All-in-one workspace. Warm minimalism, serif headings, soft surfaces. — `references/notion.md`
- **Pinterest** — Visual discovery. Red accent, masonry grid, image-first. — `references/pinterest.md`
- **Resend** — Email API. Minimal dark theme, monospace accents. — `references/resend.md`
- **Zapier** — Automation platform. Warm orange, friendly illustration-driven. — `references/zapier.md`

### Design & Creative Tools

- **Bugatti** — Hypercar brand. Cinema-black canvas, monochrome austerity, monumental display type. — `references/bugatti.md`
- **Ferrari** — Luxury automotive. Chiaroscuro editorial, Ferrari Red accents, cinematic black. — `references/ferrari.md`
- **Figma** — Collaborative design tool. Vibrant multi-color, playful yet professional. — `references/figma.md`
- **Framer** — Website builder. Bold black and blue, motion-first, design-forward. — `references/framer.md`
- **IBM** — Enterprise technology. Carbon design system, structured blue palette. — `references/ibm.md`
- **Miro** — Visual collaboration. Bright yellow accent, infinite canvas aesthetic. — `references/miro.md`
- **Webflow** — Visual web builder. Blue-accented, polished marketing site aesthetic. — `references/webflow.md`

### Fintech & Crypto

- **Binance** — Crypto exchange. Bold yellow accent on monochrome, trading-floor urgency. — `references/binance.md`
- **Coinbase** — Crypto exchange. Clean blue identity, trust-focused, institutional feel. — `references/coinbase.md`
- **Kraken** — Crypto trading. Purple-accented dark UI, data-dense dashboards. — `references/kraken.md`
- **Mastercard** — Global payments network. Warm cream canvas, orbital pill shapes, editorial warmth. — `references/mastercard.md`
- **Revolut** — Digital banking. Sleek dark interface, gradient cards, fintech precision. — `references/revolut.md`
- **Stripe** — Payment infrastructure. Signature purple gradients, weight-300 elegance. — `references/stripe.md`
- **Wise** — Money transfer. Bright green accent, friendly and clear. — `references/wise.md`

### E-commerce & Retail

- **Airbnb** — Travel marketplace. Warm coral accent, photography-driven, rounded UI. — `references/airbnb.md`
- **Meta** — Tech retail store. Photography-first, binary light/dark surfaces, Meta Blue CTAs. — `references/meta.md`
- **Nike** — Athletic retail. Monochrome UI, massive uppercase type, full-bleed photography. — `references/nike.md`
- **Playstation** — Gaming console retail. Three-surface channel layout, quiet-authority display type, cyan hover-scale. — `references/playstation.md`
- **Shopify** — E-commerce platform. Dark-first cinematic, neon green accent, ultra-light type. — `references/shopify.md`
- **Starbucks** — Global coffee retail brand. Four-tier green system, warm cream canvas, full-pill buttons. — `references/starbucks.md`

### Media & Consumer Tech

- **Apple** — Consumer electronics. Premium white space, SF Pro, cinematic imagery. — `references/apple.md`
- **Nvidia** — GPU computing. Green-black energy, technical power aesthetic. — `references/nvidia.md`
- **SpaceX** — Space technology. Stark black and white, full-bleed imagery, futuristic. — `references/spacex.md`
- **Spotify** — Music streaming. Vibrant green on dark, bold type, album-art-driven. — `references/spotify.md`
- **Theverge** — Tech editorial media. Acid-mint and ultraviolet accents, Manuka display, rave-flyer story tiles. — `references/theverge.md`
- **Uber** — Mobility platform. Bold black and white, tight type, urban energy. — `references/uber.md`
- **Vodafone** — Global telecom brand. Monumental uppercase display, Vodafone Red chapter bands. — `references/vodafone.md`
- **Wired** — Tech magazine. Paper-white broadsheet density, custom serif display, mono kickers, ink-blue links. — `references/wired.md`

### Automotive

- **BMW** — Luxury automotive. Dark premium surfaces, precise German engineering aesthetic. — `references/bmw.md`
- **Lamborghini** — Supercar brand. True black surfaces, gold accents, dramatic uppercase typography. — `references/lamborghini.md`
- **Renault** — French automotive. Vibrant aurora gradients, NouvelR typography, bold energy. — `references/renault.md`
- **Tesla** — Electric automotive. Radical subtraction, full-viewport photography, near-zero UI. — `references/tesla.md`

## 使用指南

### 典型工作流

1. 用户说"做一个像 Stripe 风格的落地页" → 读取 `references/stripe.md`
2. 从 DESIGN.md 中提取关键参数：主色 `#533afd`、字体 `sohne-var` weight 300、阴影 `rgba(50,50,93,0.25)`
3. 按照组件样式章节中的按钮、卡片、导航规范生成 HTML/CSS

### 融合多个品牌风格

当用户要求融合多个品牌风格时，分别读取对应的 DESIGN.md，提取各自的核心特征后进行混合。例如"Stripe 的配色 + Vercel 的排版"。

### 关键注意事项

- DESIGN.md 中的色值、字体、间距参数是精确值，生成代码时应严格遵循
- 注意区分 Light/Dark 模式的不同参数
- 响应式断点和折叠策略在 Responsive Behavior 章节中定义
- Do's and Don'ts 章节包含重要的设计约束，务必遵守

## 来源

本技能的设计系统文件来源于 [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) 开源项目（MIT License），数据更新至 2026-04-21。