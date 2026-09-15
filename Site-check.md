# Site Check: HUMAIN's First Building

**Site:** HUMAIN's first building — 50 MW connection, 18,000 NVIDIA GB300 GPUs (announced)

---

## 1. How many racks and GPUs does the site's power buy?
**Question asked:** How many racks and GPUs does the site's power buy?

**Working:**
- Usable power after 20% headroom: 50 MW × 0.80 = 40 MW
- IT power after PUE 1.25: 40 MW ÷ 1.25 = 32 MW
- GPU power after 10% for switches/storage: 32 MW × 0.90 = 28.8 MW
- GB300 NVL72 rack draws ~120 kW → racks = 28,800 kW ÷ 120 kW = **240 racks**
- GPUs = 240 racks × 72 GPUs/rack = **17,280 GPUs**

**Assumption:** Order of operations — headroom is taken off the grid connection first, then PUE, then the switches/storage split is taken off the remaining IT power. Result lands within ~4% of the announced 18,000 GPUs, which supports this assumption.

**Answer: 240 racks, 17,280 GPUs**

---

## 2. What is the largest open model it can serve, and how many copies?

**Question asked:** What is the largest open model it can serve, and how many copies of it?

**Working:**
- Model chosen: **Llama 3.1 405B** (largest widely-available open-weight model with published architecture)
- Weights at fp8 ≈ 1 byte/param → 405 GB
- KV cache for 32 conversations × 128K tokens context, estimated from published architecture (126 layers, 8 KV heads, head_dim 128, fp16 cache): ≈ 504 KB/token × 4.19M tokens ≈ 2.1 TB
- Total memory per instance: 405 GB + 2.1 TB ≈ **2.5 TB**
- GB300 NVL72 rack memory ≈ 20 TB → ~7–8 copies per rack (memory-only ceiling)
- Across 240 racks ≈ **~1,700–1,900 copies sitewide**

**Assumption:** One model instance is kept within a single rack (no cross-rack sharding); memory is the binding constraint, not compute.

**Answer: Llama 3.1 405B, ~7–8 copies per rack, ~1,700–1,900 copies across the site**

---

## 3. What is the largest model it could train in six months?

**Question asked:** What is the largest model it could train in six months?

**Working:**
- Time: 6 months ≈ 15,552,000 seconds (30-day months)
- Effective compute: 17,280 GPUs × 989 TFLOPS (H100 peak, given) × 0.40 utilization × 15,552,000 s ≈ 1.06 × 10²⁶ FLOPs
- Training-compute rule: 6 operations/parameter/token, 20 tokens/parameter → total FLOPs = 6 × P × (20P) = 120P²
- Solve for P: P² = 1.06 × 10²⁶ ÷ 120 → P ≈ 9.4 × 10¹¹

**Assumption:** Using the given H100 peak FLOPS figure (989 TFLOPS) as the per-GPU compute rate, since no GB300/Blackwell Ultra peak FLOPS figure was provided in the source materials.

**Answer: ~940 billion parameters** (dense model equivalent; this is a floor, since the real GPU is faster than an H100 — see caveat below)

---

## 4. What is its electricity bill for a month?

**Question asked:** What is its electricity bill for a month?

**Working:**
- Average draw: 50 MW × 0.65 = 32.5 MW
- Monthly energy: 32.5 MW × 24 h × 30 days = 23,400 MWh = 23,400,000 kWh
- At standard rate ($0.08/kWh): 23,400,000 × 0.08 = **$1,872,000/month**
- At industrial rate ($0.048/kWh): 23,400,000 × 0.048 = **$1,123,200/month**

**Assumption:** 30-day month used for the calculation; industrial rate assumed to be the applicable tariff for a site of this scale.

**Answer: ~$1,123,200/month (industrial rate) or ~$1,872,000/month (standard rate)**

---

## 5. What does a million tokens cost, at 30% and at 80% of capacity sold?

**Question asked:** What does a million tokens cost, at 30% and at 80% of capacity sold?

**Working:**
- Non-electricity cost: $450,000/MW-month × 50 MW = $22,500,000/month
- Total monthly cost (using industrial electricity rate): $22,500,000 + $1,123,200 ≈ $23,623,200/month
- Max monthly token output at 100% capacity: 17,280 GPUs × 125 tokens/sec/GPU × 2,592,000 s/month ≈ 5.6 trillion tokens/month
- At 30% capacity sold: 1.68 trillion tokens → $23,623,200 ÷ 1.68M (millions of tokens) ≈ **$14.07 per million tokens**
- At 80% capacity sold: 4.48 trillion tokens → $23,623,200 ÷ 4.48M (millions of tokens) ≈ **$5.28 per million tokens**

**Assumption:** Total monthly cost is fixed regardless of tokens actually sold (power draw is given as a flat average, not scaled to sales volume), so only the denominator (tokens sold) changes between the two scenarios.

**Answer: $14.07/million tokens at 30% capacity sold; $5.28/million tokens at 80% capacity sold**

---

## One thing the announcement does not tell you

The site's actual GPU (GB300 / Blackwell Ultra) peak FLOPS figure is never published in any of the sourced announcements — only the general H100 constant (989 TFLOPS) was given to work with. Every training-capacity estimate in Question 3 is therefore built on a stand-in chip figure, not the real one. The actual site could plausibly train a model several times larger than ~940B parameters in the same six months, since Blackwell Ultra significantly exceeds H100 throughput per GPU.
