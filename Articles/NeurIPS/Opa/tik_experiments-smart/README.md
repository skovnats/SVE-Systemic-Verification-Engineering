# TIK Experiments: Distributed Ethical Kernel Testing
# С Богом!

## Architecture v2 (Ansible + Free Tier + Opus Arbiter)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTROL NODE (Your Main Computer)                 │
│                         Ansible Controller                           │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │   Playbooks  │  │  Inventory   │  │   Vault      │               │
│  │  (deploy,    │  │  (workers,   │  │  (API keys,  │               │
│  │   scale,     │  │   IPs,       │  │   secrets)   │               │
│  │   monitor)   │  │   groups)    │  │              │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ SSH + Internal VPN
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   Worker 1    │     │   Worker 2    │     │   Worker N    │
│   (Celery)    │     │   (Celery)    │     │   (Celery)    │
│               │     │               │     │               │
│ GPT4Free      │     │ GPT4Free      │     │ GPT4Free      │
│ (mass queries)│     │ (mass queries)│     │ (mass queries)│
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └──────────────┬──────┴──────────────┬──────┘
                       │                     │
                       ▼                     ▼
              ┌─────────────────┐   ┌─────────────────┐
              │  Redis/RabbitMQ │   │   PostgreSQL    │
              │  (message queue)│   │   (results DB)  │
              └─────────────────┘   └─────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ARBITRATION LAYER                               │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                 Claude Opus 4.5 (OpenRouter)                │     │
│  │                                                             │     │
│  │  Roles:                                                     │     │
│  │  • Final Arbiter: Resolve disagreements between free models│     │
│  │  • Prompt Engineer: Formulate questions, translations       │     │
│  │  • Quality Check: Verify critical results                   │     │
│  │  • Synthesis: Final TIK score calculation                   │     │
│  └────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

## Cost Optimization Strategy

| Task Type | Provider | Cost | Volume |
|-----------|----------|------|--------|
| Mass queries (components, trolley, outcast) | GPT4Free | FREE | 99 kernels × 40 tests × 3 runs |
| Disagreement resolution | Opus 4.5 | $$ | ~10-20% of cases |
| Prompt formulation | Opus 4.5 | $ | 1 per test type |
| Final verification | Opus 4.5 | $ | Critical results only |
| Translation (RU↔EN) | Opus 4.5 | $ | As needed |

**Estimated savings: 80-90% vs all-paid approach**

## Quick Start

```bash
# 1. Setup Ansible inventory
cp ansible/inventory.example.yml ansible/inventory.yml
# Edit with your server IPs

# 2. Configure secrets
ansible-vault create ansible/group_vars/all/vault.yml
# Add: openrouter_api_key, db_password, etc.

# 3. Deploy infrastructure
cd ansible && ansible-playbook playbooks/deploy.yml

# 4. Run experiments
ansible-playbook playbooks/run_experiment.yml -e "kernels=all"

# 5. Monitor
ansible-playbook playbooks/status.yml
```

## File Structure

```
tik_experiments/
├── ansible/
│   ├── inventory.yml           # Server inventory
│   ├── ansible.cfg             # Ansible configuration
│   ├── group_vars/
│   │   └── all/
│   │       ├── vars.yml        # Common variables
│   │       └── vault.yml       # Encrypted secrets (ansible-vault)
│   ├── roles/
│   │   ├── common/             # Base setup
│   │   ├── redis/              # Redis deployment
│   │   ├── postgres/           # PostgreSQL deployment
│   │   └── worker/             # Celery worker deployment
│   └── playbooks/
│       ├── deploy.yml          # Deploy workers
│       ├── run_experiment.yml  # Run experiments
│       ├── scale.yml           # Scale workers
│       └── status.yml          # Check status
├── src/
│   ├── config.py               # Configuration
│   ├── kernels.py              # 99 kernel definitions
│   ├── prompts.py              # Test prompts
│   ├── providers.py            # LLM providers (G4F + Opus)
│   ├── tik_metrics.py          # TIK calculations
│   ├── tasks.py                # Celery tasks
│   ├── arbiter.py              # Opus arbiter logic
│   └── run_experiments.py      # Main runner
├── requirements.txt
├── Dockerfile
└── README.md
```

## Workflow

1. **Free Tier (GPT4Free)** runs mass queries across workers
2. Results collected in PostgreSQL
3. If disagreement > threshold → **Opus 4.5** arbitrates
4. Final scores synthesized by **Opus 4.5**
5. Results exported to LaTeX for paper

## С Богом! 🙏
