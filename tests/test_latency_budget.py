"""⏱️ Unit Test: Verify 30Hz Deadline Compliance"""
import pytest
import asyncio
import time
from src.realtime_pipeline import ĐukaRealTimePipeline, RTConfig

@pytest.mark.asyncio
async def test_30hz_deadline_compliance():
    cfg = RTConfig(target_hz=30.0, cycle_budget_ms=33.33, fallback_threshold_ms=32.0, enable_monitoring=False)
    pipeline = ĐukaRealTimePipeline(cfg)
    
    latencies = []
    for _ in range(100):
        t0 = time.perf_counter()
        result = await pipeline.run_cycle({"state": [0.0]*12})
        latencies.append(result["latency_ms"])
        
    p95 = sorted(latencies)[int(0.95 * len(latencies))]
    mean = sum(latencies)/len(latencies)
    
    assert p95 < cfg.fallback_threshold_ms, f"P95 latency {p95:.2f}ms exceeds fallback threshold {cfg.fallback_threshold_ms}ms"
    assert mean < 25.0, f"Mean latency {mean:.2f}ms too high for 30Hz target"
    print(f"✅ Latency Test Passed | Mean: {mean:.2f}ms | P95: {p95:.2f}ms")

if __name__ == "__main__":
    asyncio.run(test_30hz_deadline_compliance())
