# ECS Autoscaling Analysis - 2026-03-11

## Service: harvester-service (cluster: harvester)

### Previous Configuration
| Setting | Value |
|---|---|
| Min capacity | 20 |
| Max capacity | 200 |
| Target value (ALBRequestCountPerTarget) | 4.0 |
| Scale-out cooldown | 0s |
| Scale-in cooldown | 0s |

### New Configuration (applied 2026-03-11)
| Setting | Value |
|---|---|
| Min capacity | 30 |
| Max capacity | 150 |
| Target value (ALBRequestCountPerTarget) | 10.0 |
| Scale-out cooldown | 120s |
| Scale-in cooldown | 300s |

### Container Setup
- Gunicorn with 4 sync workers, 120s timeout
- Each task can handle ~4 concurrent requests (1 per worker)
- Each worker can handle ~15 requests/min at p50 response time (~4s)
- Theoretical max per task: ~60 requests/min

### Traffic Pattern (2026-03-11)
- **Off-hours (00:00-06:00 UTC)**: 100-270 requests/hour
- **Burst ramp (06:00-08:00)**: Spikes from near-zero to thousands in a single 5-min window, then drops back
- **Sustained peak (08:00-14:00)**: 45k-77k requests/hour (~750-1,300/min)
- **Taper (14:00-17:00)**: 20-25k/hour with gaps of near-zero traffic
- Traffic is very bursty within each hour (e.g., 10,000 requests one 5-min window, then 15 the next)

### Response Times (peak hours)
| Percentile | Value |
|---|---|
| p50 | 3-5 seconds |
| p90 | 8-35 seconds |
| p99 | 35-56 seconds |

### Error Rates (pre-change)
- **ELB 5xx**: 1,800-5,600/hour during peak (likely 502/504 from ALB when tasks can't respond)
- **Target 5xx**: 800-1,300/hour (mix of gunicorn timeouts and upstream publisher errors via Zyte)

### Host Count (pre-change)
- Highly volatile: swinging between 5 and 103 within a single hour
- Averaged ~98-100 during sustained peak
- Rarely needed more than ~100 for sustained traffic; jumps to 200 were reactions to momentary spikes after scale-down

### Problems Identified
1. **Zero cooldowns** caused rapid oscillation (sawtooth pattern): service would scale down every minute during brief traffic gaps, then jump back to 200 on the next burst
2. **Target of 4** was too sensitive for the bursty traffic pattern, triggering scale-out too aggressively
3. **Max of 200** was rarely needed — sustained traffic was handled by ~100 tasks
4. **Scaling activity showed**: scaled down from 135 to 93 over ~10 minutes (every 1-2 min), then immediately jumped back to 200

### Expected Improvements
- Elimination of sawtooth scaling pattern
- Reduced ELB 5xx errors from capacity thrashing
- Lower costs from not over-scaling to 200 unnecessarily
- More stable task count during sustained traffic

### Monitoring Checklist
- [ ] Compare ELB 5xx error rates after 24-48 hours
- [ ] Check scaling activity for smoother patterns (no rapid oscillation)
- [ ] Verify host count stays more stable during peak hours
- [ ] Confirm no increase in response times (p50/p90/p99)
- [ ] Check that off-hours baseline of 30 tasks is sufficient
- [ ] Verify burst ramp-up is fast enough (no spike in errors at start of traffic bursts)

### Commands to Re-check
```bash
# Scaling activities
aws application-autoscaling describe-scaling-activities --service-namespace ecs --resource-id service/harvester/harvester-service --max-items 10

# Current config
aws application-autoscaling describe-scalable-targets --service-namespace ecs --resource-ids service/harvester/harvester-service
aws application-autoscaling describe-scaling-policies --service-namespace ecs --resource-id service/harvester/harvester-service

# Request count (last 24h hourly)
aws cloudwatch get-metric-statistics --namespace AWS/ApplicationELB --metric-name RequestCount --dimensions Name=LoadBalancer,Value=app/harvester-load-balancer/d5fb7aac78d5460e --start-time $(date -u -v-24H +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --period 3600 --statistics Sum

# ELB 5xx errors
aws cloudwatch get-metric-statistics --namespace AWS/ApplicationELB --metric-name HTTPCode_ELB_5XX_Count --dimensions Name=LoadBalancer,Value=app/harvester-load-balancer/d5fb7aac78d5460e --start-time $(date -u -v-24H +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --period 3600 --statistics Sum

# Response times
aws cloudwatch get-metric-statistics --namespace AWS/ApplicationELB --metric-name TargetResponseTime --dimensions Name=LoadBalancer,Value=app/harvester-load-balancer/d5fb7aac78d5460e --start-time $(date -u -v-24H +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --period 3600 --statistics Average --extended-statistics p50 p90 p99

# Healthy host count
aws cloudwatch get-metric-statistics --namespace AWS/ApplicationELB --metric-name HealthyHostCount --dimensions "Name=TargetGroup,Value=targetgroup/ecs-harvester-tg/edf4ed151e41ab37" "Name=LoadBalancer,Value=app/harvester-load-balancer/d5fb7aac78d5460e" --start-time $(date -u -v-24H +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --period 3600 --statistics Average Minimum Maximum
```
