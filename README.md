# Đuka Protocol v1.0
**Programmable Reality Engine**

<div align="center">

![Đuka Banner](https://img.shields.io/badge/Đuka-Protocol-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)

**One Network. Infinite Learning. Re-simulated Existence.**

*Made with ❤️ from Algeria (Oran)*

[Documentation](#documentation) • [Quick Start](#quick-start) • [Roadmap](#roadmap) • [Contributing](#contributing)

</div>

---

## 🌟 Vision

**Đuka** (Distributed Unified Knowledge Architecture) is an open-source foundational protocol that unifies four critical domains into a single evolutionary intelligence system:

- **🤖 Robotics**: Tesla Optimus compatibility + ROS2 + humanoid systems
- **🧠 AI**: Hierarchical World Models + Causal Surrogates + Reinforcement Learning
- **🎮 Simulation**: PyBullet, Unity/Isaac Sim bridges + Frequency-based programmable reality
- **📡 Networking**: Starlink-like realtime mesh + WebSocket + UDP discovery

**Đuka serves as the "Foundational Layer"** that unifies methodologies from Tesla (Optimus), Starlink, and xAI under one vision:  
**A fleet of intelligent robots that learn federatedly, communicate with global low-latency, and evolve safely within a unified simulation-reality environment.**

### Why Đuka for Tesla, Starlink & xAI?

| Company | Đuka Integration |
|---------|------------------|
| **Tesla Optimus** | ROS2 Compatibility Layer + end-to-end neural networks + fleet learning |
| **Starlink** | Real-time mesh networking + low-latency satellite routing + global telemetry |
| **xAI** | Hierarchical World Model + Reality Firewall + Constitutional Guardrails |

**Đuka is not a competitor—it's the open bridge** accelerating integration between robotics, networking, and intelligence.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional but recommended)
- GPU support (optional, CUDA-compatible for faster training)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/abdelkadermeflahi4000/-uka.git
cd -uka

# Create necessary directories
mkdir -p logs models tensorboard

# Start the full stack (App + Monitoring)
docker-compose up -d

# View logs
docker-compose logs -f duka_app

# Access services:
# - Gradio Demo: http://localhost:7860
# - Grafana Dashboard: http://localhost:3000 (admin/duka2026)
# - Prometheus Metrics: http://localhost:9090
```

### Option 2: Local Installation

```bash
# Clone and navigate
git clone https://github.com/abdelkadermeflahi4000/-uka.git
cd -uka

# Install dependencies
pip install -r requirements.txt

# Run the real-time pipeline
python -m src.realtime_pipeline

# Or run the Gradio demo
python app.py
```

### Option 3: Quick Test

```bash
# Run the latency test to verify 30Hz compliance
python -m pytest tests/test_latency_budget.py -v
```

---

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Đuka Protocol Stack                       │
├─────────────────────────────────────────────────────────────┤
│  Application Layer                                           │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐  │
│  │ Gradio Demo │ │ FastAPI API  │ │ ROS2 Bridge         │  │
│  └─────────────┘ └──────────────┘ └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Real-Time Pipeline (30Hz Target)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Perception → World Model → Decision → Actuation      │   │
│  │            ↑              ↑              ↑            │   │
│  │    Hierarchical    Constitutional    Reality          │   │
│  │    Surrogate       Gate            Firewall           │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Safety & Governance                                         │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐  │
│  │ DP-FedAvg   │ │ Audit Logger │ │ Human-in-the-Loop   │  │
│  └─────────────┘ └──────────────┘ └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Monitoring Stack                                            │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐  │
│  │ Prometheus  │ │ Grafana      │ │ Loki (Logs)         │  │
│  └─────────────┘ └──────────────┘ └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Real-time Pipeline** | 30Hz strict deadline enforcement with fallback policies | ✅ Stable |
| **Hierarchical World Model** | Multi-abstraction state representation + causal surrogates | ✅ Prototype |
| **Constitutional Gate** | Ethical decision-making with audit trail | ✅ Stable |
| **DP-FedAvg** | Federated learning with differential privacy | ✅ Prototype |
| **Reality Firewall** | Mandatory safety check before any actuation | ✅ Prototype |
| **Noosphere** | Collective consciousness field simulation | 🧪 Experimental |
| **ROS2 Bridge** | Tesla Optimus compatibility layer | 🚧 In Progress |
| **Starlink Mesh** | Satellite-aware networking simulation | 🚧 In Progress |

---

## 📊 Monitoring & Observability

Đuka includes a production-ready monitoring stack:

### Prometheus Metrics
- Cycle latency (per-layer breakdown)
- Decision confidence scores
- Fallback activation events
- Resource utilization (CPU, memory, GPU)

### Grafana Dashboards
Access at `http://localhost:3000` (default credentials: `admin` / `duka2026`)

Pre-configured dashboards:
- **Đuka Main Dashboard**: Real-time pipeline performance
- **System Metrics**: Node exporter + cAdvisor data
- **Federation Health**: DP-FedAvg sync status

### Loki Logs
Aggregated logging for all components, queryable via Grafana.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_latency_budget.py -v

# Run with coverage (requires pytest-cov)
pytest tests/ --cov=src --cov-report=html
```

### Latency Budget Test
The core real-time guarantee is tested via `test_latency_budget.py`:
- **Target**: 30Hz (33.33ms per cycle)
- **P95 Threshold**: < 32ms
- **Mean Threshold**: < 25ms

---

## 📁 Project Structure

```
-uka/
├── src/
│   ├── core/               # Core orchestrators
│   ├── layers/             # Pipeline layers (World Model, Constitutional Gate, etc.)
│   ├── frequency_matter/   # Programmable reality engine
│   ├── collective/         # Noosphere & collective intelligence
│   ├── utils/              # Utilities & helpers
│   └── realtime_pipeline.py # Main 30Hz loop
├── monitoring/
│   ├── metrics.py          # Prometheus metrics
│   └── tensorboard_logger.py
├── tests/
│   └── test_latency_budget.py
├── docker/
│   ├── docker-compose.yml  # Full monitoring stack
│   ├── prometheus.yml
│   └── grafana/
│       ├── datasources.yml
│       └── dashboards/
├── app.py                  # Gradio demo
├── run_đuka.py            # Full cycle runner
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🛣️ Roadmap

### Phase 1: Security & Foundation (Q2 2026)
- [x] Real-time pipeline (30Hz)
- [x] Constitutional Guardrail
- [x] DP-FedAvg prototype
- [ ] Reality Firewall v1 (WebAssembly + eBPF)
- [ ] Zero-Trust node authentication
- [ ] Homomorphic Encryption in DP-FedAvg

### Phase 2: Big Tech Integration (Q3 2026)
- [ ] Optimus Compatibility Pack (ROS2 + end-to-end NN hooks)
- [ ] Starlink-aware realtime mesh
- [ ] Hierarchical World Model benchmark vs Isaac Sim / MuJoCo
- [ ] PyBullet humanoid bridge

### Phase 3: Productization (Q4 2026)
- [ ] Đuka Cloud beta (hosted federation + dashboard)
- [ ] Open-Core launch: free core + paid enterprise
- [ ] First enterprise pilots
- [ ] Arabic/Darija guardrail support

See full roadmap in [ROADMAP.md](ROADMAP.md).

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas We Need Help
- 🔒 Security & Privacy (Zero-Trust, Homomorphic Encryption)
- 🤖 ROS2 + Optimus compatibility
- 📡 Starlink-like realtime mesh
- 🧠 Hierarchical World Model improvements
- 📚 Documentation & demos
- 🌍 Arabic/Darija support in guardrails

### Development Setup
```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/-uka.git
cd -uka

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dev dependencies
pip install -r requirements.txt

# Run tests before committing
pytest tests/ -v
```

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### Open-Core Model
- **Open Source (Apache 2.0)**: Core Protocol, ROS2 Bridge, Hierarchical World Model, DP-FedAvg, basic Reality Firewall
- **Enterprise (Commercial)**: Advanced Zero-Trust Security, Homomorphic Encryption, Đuka Cloud, Professional Services

---

## 🙏 Acknowledgments

- Inspired by Tesla's Optimus program, Starlink's global network, and xAI's approach to safe AGI
- Built with ideas from Constitutional AI, Federated Learning, and Causal Representation Learning
- **Made with ❤️ from Algeria** 🇩🇿

---

## 📬 Contact

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and community discussions
- **Email**: [Project maintainers]

---

<div align="center">

**"One Network. Infinite Learning."**

⭐ Star this repo if you believe in open, safe, unified intelligence!

</div>

