# Rollback Procedures - Data Ingestion Pipeline Optimizations

**Document Version**: 1.0.0
**Last Updated**: December 30, 2025
**Status**: Production Ready

---

## Overview

This document provides step-by-step procedures for rolling back the data ingestion pipeline optimizations in case of issues. The optimizations are designed to be **backward-compatible** and can be disabled without code changes using environment variables and feature flags.

---

## Quick Rollback (Emergency)

### Complete Disable - 30 seconds

If you need to **immediately** revert to baseline behavior:

```bash
# Set environment variables to disable ALL optimizations
export FEATURE_PARSE_CACHE=false
export FEATURE_BATCHING=false
export FEATURE_NEO4J_BATCH=false
export FEATURE_PARALLEL=false
export FEATURE_METRICS=false

# Restart the ingestion service
# (Method depends on your deployment - systemd, docker, k8s, etc.)
systemctl restart financial-lineage-ingestion
# OR
docker-compose restart ingestion
# OR
kubectl rollout restart deployment/ingestion
```

**Result**: System reverts to baseline 1x throughput (no optimizations).

---

## Gradual Rollback (Recommended)

### Disable One Feature at a Time

It's recommended to disable features incrementally to identify the problematic component:

#### Step 1: Disable Parallel Workers (Revert to Sequential)

```bash
export FEATURE_PARALLEL=false
systemctl restart financial-lineage-ingestion
```

**Effect**:
- Returns to sequential processing
- Removes ProcessPoolExecutor
- Reverts to ~2-3x throughput (cache + batching still active)

**Monitor**: Check if issue persists

---

#### Step 2: Disable Neo4j Batching

```bash
export FEATURE_NEO4J_BATCH=false
systemctl restart financial-lineage-ingestion
```

**Effect**:
- One-by-one Neo4j entity creation
- Removes UNWIND batch operations
- Reverts to ~2-3x throughput (cache + file batching still active)

**Monitor**: Check Neo4j connection and transaction logs

---

#### Step 3: Disable File Batching

```bash
export FEATURE_BATCHING=false
systemctl restart financial-lineage-ingestion
```

**Effect**:
- Immediate file processing (no debouncing)
- Event deduplication disabled
- Reverts to ~2x throughput (cache still active)

**Monitor**: Check CPU usage and file event handling

---

#### Step 4: Disable Parse Cache

```bash
export FEATURE_PARSE_CACHE=false
systemctl restart financial-lineage-ingestion
```

**Effect**:
- Re-parse all files on every change
- No cache lookups
- Reverts to **1x throughput (BASELINE)**

**Monitor**: Confirm baseline behavior restored

---

## Scenario-Based Rollback

### Scenario 1: High Memory Usage

**Symptoms**:
- Memory usage > 80%
- OOM errors
- System becomes unresponsive

**Rollback Steps**:

1. **Disable parallel workers first** (most memory-intensive):
   ```bash
   export FEATURE_PARALLEL=false
   systemctl restart financial-lineage-ingestion
   ```

2. **Clear parse cache** if memory still high:
   ```bash
   python -m src.ingestion.parallel_file_watcher --clear-cache
   ```

3. **Reduce batch sizes** (alternative to full disable):
   ```bash
   export BATCH_SIZE_THRESHOLD=10  # Default: 50
   export INGEST_WORKERS=2          # Default: 4
   systemctl restart financial-lineage-ingestion
   ```

---

### Scenario 2: Neo4j Connection Issues

**Symptoms**:
- Neo4j timeout errors
- Transaction deadlocks
- Failed entity creation

**Rollback Steps**:

1. **Disable Neo4j batching**:
   ```bash
   export FEATURE_NEO4J_BATCH=false
   systemctl restart financial-lineage-ingestion
   ```

2. **Check failed ingestion log**:
   ```bash
   cat data/failed_ingestion.jsonl
   # Contains entities that failed to write
   ```

3. **Retry failed items** after Neo4j is stable:
   ```bash
   # Manually retry failed entities (custom script)
   python scripts/retry_failed_ingestion.py data/failed_ingestion.jsonl
   ```

---

### Scenario 3: Cache Corruption

**Symptoms**:
- Incorrect parsing results
- Cache integrity check failures
- Unexpected parse errors

**Rollback Steps**:

1. **Clear cache immediately**:
   ```bash
   python -m src.ingestion.parallel_file_watcher --clear-cache
   ```

2. **Verify cache statistics**:
   ```bash
   python -m src.ingestion.parallel_file_watcher --cache-stats
   # Should show 0 entries after clear
   ```

3. **Temporarily disable cache** (optional):
   ```bash
   export FEATURE_PARSE_CACHE=false
   systemctl restart financial-lineage-ingestion
   ```

4. **Re-enable after verification**:
   ```bash
   export FEATURE_PARSE_CACHE=true
   systemctl restart financial-lineage-ingestion
   ```

---

### Scenario 4: Performance Regression

**Symptoms**:
- Throughput below expected (< 5x improvement)
- Processing times increasing
- Prometheus metrics show degradation

**Rollback Steps**:

1. **Check feature flag status**:
   ```bash
   python -c "from src.config.feature_flags import FeatureFlags; FeatureFlags.print_status()"
   ```

2. **Run benchmark suite**:
   ```bash
   pytest tests/performance/test_ingestion_benchmark.py -v
   # Compare against baseline
   ```

3. **Check Prometheus metrics**:
   ```bash
   curl http://localhost:8000/metrics | grep -E "(files_processed|batch_processing_duration)"
   ```

4. **If regression confirmed, disable optimizations**:
   ```bash
   # Disable all and re-enable one-by-one to identify culprit
   export FEATURE_PARSE_CACHE=false
   export FEATURE_BATCHING=false
   export FEATURE_NEO4J_BATCH=false
   export FEATURE_PARALLEL=false
   systemctl restart financial-lineage-ingestion
   ```

---

## Verification Procedures

### After Rollback - Verify System Health

1. **Check service status**:
   ```bash
   systemctl status financial-lineage-ingestion
   # Should show "active (running)"
   ```

2. **Verify feature flags**:
   ```bash
   python -c "from src.config.feature_flags import FeatureFlags; FeatureFlags.print_status()"
   ```

3. **Test basic ingestion**:
   ```bash
   # Create test file
   echo "CREATE TABLE test_rollback (id INT);" > /tmp/test_rollback.sql

   # Copy to watch directory
   cp /tmp/test_rollback.sql ./data/raw/

   # Watch logs for successful processing
   tail -f logs/ingestion.log
   ```

4. **Check Prometheus metrics**:
   ```bash
   curl http://localhost:8000/metrics
   ```

5. **Verify Neo4j connectivity**:
   ```bash
   # Test Neo4j connection
   python -c "
   from src.knowledge_graph.neo4j_client import Neo4jGraphClient
   client = Neo4jGraphClient()
   # Should connect without error
   "
   ```

---

## Configuration Files

### Environment Variable Reference

| Variable | Default | Baseline Value | Purpose |
|----------|---------|----------------|---------|
| `FEATURE_PARSE_CACHE` | `true` | `false` | Enable parse caching |
| `FEATURE_BATCHING` | `true` | `false` | Enable file batching |
| `FEATURE_NEO4J_BATCH` | `true` | `false` | Enable Neo4j batching |
| `FEATURE_PARALLEL` | `true` | `false` | Enable parallel workers |
| `FEATURE_METRICS` | `true` | `false` | Enable metrics collection |
| `INGEST_WORKERS` | `4` | `1` | Number of parallel workers |
| `BATCH_SIZE_THRESHOLD` | `50` | `1` | Files per batch |
| `DEBOUNCE_WINDOW_SECONDS` | `5.0` | `0.0` | Debounce delay |

### Systemd Service File (Example)

```ini
[Unit]
Description=Financial Lineage Ingestion Service
After=network.target neo4j.service

[Service]
Type=simple
User=lineage
WorkingDirectory=/opt/financial-lineage
Environment="FEATURE_PARSE_CACHE=true"
Environment="FEATURE_BATCHING=true"
Environment="FEATURE_NEO4J_BATCH=true"
Environment="FEATURE_PARALLEL=true"
Environment="FEATURE_METRICS=true"
ExecStart=/opt/financial-lineage/venv/bin/python -m src.ingestion.parallel_file_watcher ./data/raw ./data/output
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**To modify**:
```bash
sudo vi /etc/systemd/system/financial-lineage-ingestion.service
sudo systemctl daemon-reload
sudo systemctl restart financial-lineage-ingestion
```

---

## Rollback Decision Tree

```
┌─────────────────────────────┐
│ Production Issue Detected   │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Is it urgent/critical?      │
└──────────┬──────────────────┘
           │
    ┌──────┴──────┐
    │             │
   YES           NO
    │             │
    ▼             ▼
┌───────────┐  ┌──────────────────┐
│ Emergency │  │ Gradual Rollback │
│ Rollback  │  │ (One feature at  │
│ (All)     │  │  a time)         │
└───────────┘  └──────────────────┘
    │                   │
    ▼                   ▼
┌───────────────────────────────┐
│ Verify System Restored        │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│ Investigate Root Cause        │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│ Fix Issue → Re-enable         │
│ (Test in staging first)       │
└───────────────────────────────┘
```

---

## Re-Enablement Procedure

Once the issue is resolved, re-enable optimizations gradually:

### Step-by-Step Re-enablement

1. **Enable in staging first**:
   ```bash
   # Staging environment
   export FEATURE_PARSE_CACHE=true
   systemctl restart financial-lineage-ingestion-staging
   ```

2. **Monitor for 24 hours**:
   - Check Prometheus metrics
   - Monitor error rates
   - Verify performance improvement

3. **Enable next feature**:
   ```bash
   export FEATURE_BATCHING=true
   systemctl restart financial-lineage-ingestion-staging
   ```

4. **Repeat until all features enabled**:
   - Parse Cache → Batching → Neo4j Batch → Parallel Workers

5. **Deploy to production**:
   ```bash
   # Production environment
   export FEATURE_PARSE_CACHE=true
   export FEATURE_BATCHING=true
   export FEATURE_NEO4J_BATCH=true
   export FEATURE_PARALLEL=true
   systemctl restart financial-lineage-ingestion
   ```

---

## Monitoring During Rollback

### Key Metrics to Watch

1. **Throughput** (Prometheus):
   ```promql
   rate(files_processed_total[1m]) * 60  # Files per minute
   ```

2. **Error Rate** (Prometheus):
   ```promql
   rate(files_failed_total[1m]) / rate(files_processed_total[1m])
   ```

3. **Queue Size** (Prometheus):
   ```promql
   queue_size  # Should decrease after rollback
   ```

4. **System Resources**:
   ```bash
   # CPU
   top -p $(pgrep -f "parallel_file_watcher")

   # Memory
   ps aux | grep parallel_file_watcher | awk '{print $4 "%"}'

   # Disk I/O
   iotop -p $(pgrep -f "parallel_file_watcher")
   ```

---

## Support Contacts

**Escalation Path**:
1. Check Prometheus metrics: `http://your-host:8000/metrics`
2. Review logs: `/var/log/financial-lineage/ingestion.log`
3. Consult documentation: `/opt/financial-lineage/docs/`
4. Contact DevOps team: devops@example.com
5. Emergency escalation: oncall@example.com

---

## Appendix: Common Error Messages

### Parse Cache Errors

**Error**: `sqlite3.DatabaseError: database disk image is malformed`
**Solution**: Clear cache immediately
```bash
python -m src.ingestion.parallel_file_watcher --clear-cache
```

---

### Neo4j Errors

**Error**: `ServiceUnavailable: Connection pool timeout`
**Solution**: Disable Neo4j batching
```bash
export FEATURE_NEO4J_BATCH=false
systemctl restart financial-lineage-ingestion
```

---

### Worker Pool Errors

**Error**: `ProcessPoolExecutor: BrokenProcessPool`
**Solution**: Disable parallel workers
```bash
export FEATURE_PARALLEL=false
systemctl restart financial-lineage-ingestion
```

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-12-30 | Initial release | Claude Code |

---

**For additional support, refer to**:
- [Feature Flags Documentation](../../src/config/feature_flags.py)
- [Deployment Guide](DEPLOYMENT_GUIDE.md) _(to be created)_
- [Monitoring Guide](MONITORING_GUIDE.md) _(to be created)_
