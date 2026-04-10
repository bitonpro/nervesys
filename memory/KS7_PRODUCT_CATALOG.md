# ks7 Flow — Product Catalog & Infrastructure Map
## Last Updated: 2026-04-10

---

## HARDWARE

### 5060i — Command Center
- **CPU:** Intel Core i5-14400F (16 cores)
- **RAM:** 32GB DDR5
- **GPU:** NVIDIA RTX 5060 Ti 16GB
- **Storage:** 480GB NVMe (367GB free)
- **Network:** 10.100.102.245 / Tailscale 100.78.111.114
- **Role:** Hub, Wazuh SIEM, Orchestration, CogVideoX video generation

### dgxsec — AI Powerhouse #1
- **CPU:** ARM Cortex-X925 + Cortex-A725 (20 cores)
- **RAM:** 128GB Unified
- **GPU:** NVIDIA GB10 (128GB unified memory)
- **Storage:** 3.6TB NVMe (1.3TB free / 65% used)
- **Network:** 10.100.102.240 / Tailscale 100.78.185.72
- **Role:** AI Training, Video Generation, LLM Inference, NFS Server

### dgxmain — AI Powerhouse #2 + Services
- **CPU:** ARM Cortex-X925 + Cortex-A725 (20 cores)
- **RAM:** 128GB Unified
- **GPU:** NVIDIA GB10 (128GB unified memory)
- **Storage:** 3.6TB NVMe (2.5TB free / 29% used)
- **Network:** 10.100.102.241 / Tailscale 100.124.217.84
- **Role:** Docker Services, Voice AI, Dify, K3s, Gitea

---

## AI CAPABILITIES

### Large Language Models (Ollama)

| Model | Size | Server | Use Case |
|-------|------|--------|----------|
| nemotron-3-super:120b | 86GB | dgxsec+dgxmain | Flagship reasoning |
| gpt-oss:120b | 65GB | dgxsec+dgxmain | Open-source GPT alternative |
| llama3.2-vision:90b | 54GB | dgxsec | Multimodal vision+text |
| deepseek-r1:70b | 42GB | dgxsec+dgxmain | Deep reasoning/math |
| llama3:70b | 39GB | dgxsec+dgxmain | General purpose |
| llava:34b | 20GB | dgxsec | Vision-language |
| qwen3:32b | 20GB | dgxsec+dgxmain | Multilingual + Hebrew |
| gemma3:27b | 17GB | dgxsec+dgxmain | Google quality |
| qwq:latest | 19GB | dgxsec | Reasoning |
| command-r:latest | 18GB | dgxsec | RAG/retrieval |
| mistral-large:latest | 73GB | dgxsec | Enterprise |
| devstral:latest | 14GB | dgxsec+dgxmain | Code generation |
| codestral:latest | 12GB | dgxsec | Code specialist |
| solar-pro:latest | 13GB | dgxsec | Korean/multilingual |
| dolphin-mistral | 4.1GB | dgxsec | Uncensored assistant |
| gemma3:4b | 3.3GB | dgxsec+dgxmain | Lightweight |
| qwen3:8b | 5.2GB | 5060i | Quick inference |
| llama3.1:8b | 4.9GB | 5060i | Quick inference |

**OCR Models:** deepseek-ocr:3b, glm-ocr, AstralOCR-8b, orion-ocr:8b
**Video Models:** smolvlm2-256m-video, llava_next_video
**Embedding:** nomic-embed-text, voyage-4-nano, twine/noinstruct-small-embedding

### Video AI

| Tool | Model | Server | Port |
|------|-------|--------|------|
| Wan2.1 T2V 1.3B | Text-to-Video | dgxsec | 7870 |
| Wan2.1 T2V 14B | Text-to-Video (full) | dgxsec | (available) |
| CogVideoX-2B | Text-to-Video | 5060i | script |
| ComfyUI | Workflow engine | dgxmain | 8188 |
| LivePortrait | Face animation | dgxsec | (env ready) |
| MuseTalk | Talking head | dgxsec | (env ready) |

### Voice AI

| Tool | Server | Port | Function |
|------|--------|------|----------|
| Fish Speech TTS | dgxmain | 9001 | Text-to-Speech |
| STT Server | dgxmain | 9000 | Speech-to-Text |
| Hebrew API | dgxmain | 8000 | Hebrew NLP |

### LLM Training

| Tool | Server | Port |
|------|--------|------|
| LLaMA-Factory | dgxsec | 7860 |
| llama.cpp | dgxsec+dgxmain | CLI |
| TensorRT-LLM | dgxmain | Docker |
| NVIDIA RAPIDS | dgxsec | (env ready) |

---

## PLATFORMS & SERVICES

### Docker (dgxmain) — 22 containers

| Service | Image | Port | Function |
|---------|-------|------|----------|
| **Dify** | langgenius/dify | 80/443 | AI workflow platform |
| **Open WebUI** | open-webui | 12000 | ChatGPT-like interface |
| **n8n** | n8nio/n8n | 5678 | Workflow automation |
| **Gitea** | gitea | 3002 (web) / 2222 (ssh) | Git hosting |
| **Uptime Kuma** | louislam/uptime-kuma | 3001 | Monitoring |
| **WordPress** | wordpress + mariadb | 8081 | Website |
| **Kali Linux** | kalilinux/kali-rolling | — | Pentesting |
| **NVIDIA OpenShell** | nvidia/openshell | 8080 | Cluster management |
| **TensorRT-LLM** | nvidia/tensorrt-llm | — | LLM acceleration |
| **ArangoDB** | arangodb | 8529 | Graph database |
| **Caddy (OpenClaw)** | caddy | — | Reverse proxy |
| **Weaviate** | weaviate | — | Vector database |

### Snap Apps (5060i)

| App | Function |
|-----|----------|
| **Nextcloud** | File sync & share |
| **Rocket.Chat** | Team communication |
| **MicroK8s** | Kubernetes |
| **Prometheus** | Metrics monitoring |
| **Wekan** | Kanban/project management |
| **etcd** | Distributed key-value |
| **Keepalived** | High availability |
| **Mosquitto** | MQTT broker (IoT) |
| **Nomad** | Container orchestration |
| **SABnzbd** | Download manager |

### Security

| Tool | Server | Function |
|------|--------|----------|
| **Wazuh SIEM** | 5060i | Manager + Indexer + Dashboard |
| **Fail2Ban** | ALL | Brute force protection |
| **Tailscale** | ALL | Zero-trust mesh VPN |
| **ks7-forensics** | ALL | Custom security audit (every 5 min) |
| **Kali Linux** | dgxmain | Penetration testing |
| **retaliator.py** | dgxmain | Active defense |

### Network

| Component | Details |
|-----------|---------|
| **Tailscale Mesh** | 40+ devices under bar@yohay.ai |
| **NFS** | dgxsec serves shared storage |
| **Nomad** | Job orchestration across cluster |
| **Cloudflare Tunnel** | dgxsec public access |

---

## ks7 FLOW PRODUCTS (for sales)

### 1. AI Infrastructure as a Service
- 128GB GPU memory per node
- 30+ LLM models ready to use
- Wan2.1 + CogVideoX video generation
- Voice AI (STT + TTS + Hebrew)
- Pay-per-use or monthly

### 2. AI Video Production
- Text-to-Video (Wan2.1 1.3B & 14B)
- Face Animation (LivePortrait)
- Talking Head (MuseTalk)
- ComfyUI workflows
- CogVideoX 720p generation

### 3. Enterprise AI Platform
- Dify AI workflows
- Open WebUI chat interface
- 30+ models including 120B parameter
- Custom fine-tuning (LLaMA-Factory)
- RAG with Weaviate + ArangoDB

### 4. Security & Compliance
- Wazuh SIEM with dashboard
- 24/7 automated forensics
- Fail2Ban + Tailscale zero-trust
- Penetration testing (Kali)
- Active defense (retaliator)

### 5. DevOps & Hosting
- Gitea Git hosting
- n8n workflow automation
- WordPress sites
- Nextcloud file sharing
- Uptime monitoring (Kuma)
- K3s/MicroK8s Kubernetes

### 6. Voice-First AI
- Hebrew STT (Speech-to-Text)
- Fish Speech TTS
- Hebrew NLP API
- Real-time voice interaction

---

## ACCESS POINTS (Tailscale)

| Service | URL |
|---------|-----|
| Wazuh Dashboard | https://100.78.111.114:443 |
| Wan2.1 Video | http://100.78.185.72:7870 |
| LLaMA-Factory | http://100.78.185.72:7860 |
| Open WebUI | http://100.124.217.84:12000 |
| Dify AI | http://100.124.217.84:80 |
| n8n Workflows | http://100.124.217.84:5678 |
| ComfyUI | http://100.124.217.84:8188 |
| Uptime Kuma | http://100.124.217.84:3001 |
| Gitea | http://100.124.217.84:3002 |
| Voice TTS | http://100.124.217.84:9001 |
| Voice STT | http://100.124.217.84:9000 |
| Hebrew API | http://100.124.217.84:8000 |
| Wazuh API | https://100.78.111.114:55000 |
| Ollama | http://any-node:11434 |
