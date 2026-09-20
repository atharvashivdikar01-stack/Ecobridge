# ECOBRIDGE 🌿📱

> **Bridging the gap between informal e-waste collectors and certified recyclers.**  
> An offline-first, AI-driven platform delivering fair-price intelligence, net-earning optimization, end-to-end traceability, and multilingual hazard guidance.

---

## 🌟 Overview

Informal e-waste collectors (*kabadiwalas*, waste pickers, scrap aggregators) handle the majority of global electronic waste. However, they face systemic challenges: predatory middleman pricing, hazardous dismantling conditions (acid leaching, open burning), and zero formal verification for Extended Producer Responsibility (EPR) credits.

**ECOBRIDGE** transforms this ecosystem by providing:
- 📴 **Offline-First Resilience:** Full functionality in basements and remote scrap yards with seamless background delta sync.
- 👁️ **Edge AI Material & Hazard Vision:** Instant on-device classification of e-waste components with immediate PPE and safety alerts.
- ⚖️ **Fair-Price Intelligence:** Real-time scrap metal indices (LME, domestic scrap rates) to guarantee fair commodity pricing.
- 🚚 **Net-Earning Optimization:** Route and logistics calculation factoring in transport costs, recycler acceptance rates, and sorting penalties.
- 🔗 **Tamper-Evident Traceability:** Cryptographic chain-of-custody verifying e-waste origin and generating auditable EPR certificates.
- 🗣️ **Voice & Vernacular Support:** High-contrast, icon-driven interface with multi-language voice prompts (Hindi, Tamil, Telugu, Bengali, Marathi, English).
- 💳 **Escrow-Backed Instant Payments:** Fast digital settlements upon verified weighbridge intake.

---

## 🏗️ Architecture & Monorepo Layout

ECOBRIDGE is structured as a production-grade monorepo managed with **Turborepo** and **pnpm workspaces**:

```text
ecobridge/
├── apps/
│   ├── collector-mobile/      # React Native / Expo offline-first collector app
│   ├── recycler-portal/       # Next.js web portal for certified recycling facilities
│   ├── admin-dashboard/       # Next.js console for platform administrators & regulators
│   └── api-server/            # NestJS / Fastify core backend & microservices
├── packages/
│   ├── api-contracts/         # Shared TypeScript interfaces, DTOs, & Zod schemas
│   ├── database/              # PostgreSQL + PostGIS schema, migrations, & client
│   ├── sync-engine/           # Offline delta sync protocol, CRDTs, & queue logic
│   ├── ai-core/               # Edge TFLite models, hazard rules, & pricing math
│   ├── crypto-traceability/   # SHA-256 chain of custody, QR tokens, digital signatures
│   ├── ui/                    # Shared React design system & Tailwind tokens
│   ├── i18n/                  # Multilingual translation catalogs & voice dictionaries
│   ├── tsconfig/              # Shared strict TypeScript configuration
│   └── eslint-config/         # Unified linting and code quality standards
├── infra/
│   ├── docker/                # Local development docker-compose & Dockerfiles
│   ├── k8s/                   # Production Kubernetes deployment manifests
│   └── terraform/             # Cloud infrastructure as code
├── docs/
│   ├── ARCHITECTURE.md        # Complete system architecture specification
│   └── DEVELOPMENT.md         # Developer onboarding & local setup guide
└── scripts/
    └── dev-setup.sh           # Automated developer workstation bootstrapping script
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js**: `v18.0.0` or higher
- **pnpm**: `v9.0.0` or higher
- **Docker & Docker Compose**: For local PostgreSQL, Redis, and MinIO storage
- **Git**

### 1. Clone & Bootstrap
```bash
git clone https://github.com/atharvashivdikar01-stack/Ecobridge.git
cd Ecobridge

# Run the automated setup script
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh
```

### 2. Start Local Supporting Services
```bash
docker compose -f infra/docker/docker-compose.yml up -d
```

### 3. Launch Applications
```bash
# Start all apps in parallel using Turborepo
pnpm dev

# Or run specific applications:
pnpm --filter @ecobridge/api-server dev
pnpm --filter @ecobridge/recycler-portal dev
pnpm --filter @ecobridge/collector-mobile start
pnpm --filter @ecobridge/admin-dashboard dev
```

---

## 📚 Documentation

Detailed documentation is available in the [`docs/`](./docs) directory:
- [**System Architecture (`docs/ARCHITECTURE.md`)**](./docs/ARCHITECTURE.md): Deep-dive into all 11 core modules, data flows, offline sync protocols, and cryptographic ledger designs.
- [**Development Guide (`docs/DEVELOPMENT.md`)**](./docs/DEVELOPMENT.md): Step-by-step instructions for setting up local development, running tests, creating migrations, and submitting PRs.
- [**Agent Guidelines (`AGENTS.md`)**](./AGENTS.md): Architectural invariants, code rules, and contribution procedures for AI agents and developers.

---

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
