# CHALLENGE_PROMPT - Performance Engineers

## SCENARIO: Sudden Production Performance Collapse Under Peak Load

**SITUATION CONTEXT:**

It's Cyber Monday, 9:47 AM EST. Your e-commerce platform is experiencing peak annual traffic (10X normal load). The company projects $85M revenue for this 24-hour period. Your platform currently serves 847,000 concurrent users with 42,000 transactions per minute.

**IMMEDIATE CRISIS:**

**9:47 AM** - Monitoring alerts cascade:

**PERFORMANCE DEGRADATION:**
1. API response time: 120ms → 8,400ms (70X increase)
2. Database connection pool: 95% exhausted
3. Cache hit ratio: 89% → 23% (falling rapidly)
4. CPU utilization: 45% → 91% across all instances
5. Memory pressure: 12 GB → 47 GB (approaching limits)
6. Thread pool saturation: 890 threads (max capacity: 1000)
7. Network I/O: 2.3 Gbps → 9.1 Gbps (approaching bandwidth limits)

**USER IMPACT:**
- Checkout failures: 12,400 in past 10 minutes
- Cart abandonment rate: 34% → 78%
- Customer complaints flooding support (2,800 tickets in 15 minutes)
- Revenue loss: $124K per minute at current failure rate
- Social media mentions: "#CompanyName down" trending on Twitter

**MYSTERIOUS SYMPTOMS:**

Despite 10X traffic load, multiple indicators don't match expectations:

- **Database queries:** Only 2.3X normal volume (expected 10X)
- **Cache misses:** Excessive but cache servers show LOW CPU utilization
- **API calls:** Some endpoints at 100X normal latency, others normal
- **Memory:** Growing rapidly but no obvious memory leaks
- **Network:** High bandwidth but packet loss only 0.8%
- **Disk I/O:** LOW utilization despite database strain

**Something doesn't add up. This isn't a simple capacity issue.**

**RECENT CHANGES (Past 48 Hours):**

1. **New recommendation engine** deployed Friday 6 PM (AI-powered product suggestions)
2. **Database index optimization** Saturday 2 AM (improved query plans for holiday traffic)
3. **CDN configuration update** Saturday 11 PM (cache TTL adjustments)
4. **Autoscaling policy changes** Sunday 10 AM (more aggressive scaling thresholds)
5. **Third-party payment gateway upgrade** Sunday 3 PM (PCI compliance requirement)
6. **Search service update** Monday 6 AM (Elasticsearch cluster expansion)

**CONFLICTING DIAGNOSES:**

1. **Database Team:** "Connection pool exhaustion due to long-running queries. We need to kill queries and increase pool size."

2. **Application Team:** "The new recommendation engine is making too many API calls. We should disable it immediately."

3. **Infrastructure Team:** "Autoscaling isn't keeping up. We need to manually scale to 3X current capacity NOW."

4. **Network Team:** "We're seeing retry storms. Exponential backoff isn't working. Circuit breakers are open everywhere."

5. **Cache Team:** "Cache invalidation patterns changed. Something is evicting entries prematurely."

6. **DevOps:** "Thread pool exhaustion due to blocked I/O. We need to restart all application servers."

**YOUR INVESTIGATION REVEALS:**

**Anomaly #1 - The Recommendation Engine:**
- Makes 47 downstream API calls per product page view
- Has NO caching layer (relies on upstream caches)
- Each call has 5-second timeout (not 500ms as documented)
- Under load, timeouts trigger, but threads remain blocked
- Result: Thread pool exhaustion from waiting operations

**Anomaly #2 - The Database Optimization:**
- New indexes HELP some queries but HURT others
- Query planner now choosing index scans over table scans
- For high-cardinality queries, this is SLOWER
- Checkout queries taking 2,400ms vs. previous 180ms
- BUT: Analytics queries improved from 8s to 400ms

**Anomaly #3 - The CDN Configuration:**
- Cache TTL increased from 5 min → 30 min (to reduce origin load)
- BUT: Cache invalidation on product price changes now delayed
- Users see stale prices, retry checkout, create duplicate orders
- Retry logic creates 4-6X actual transaction load
- Results in "phantom load" not visible in top-level metrics

**Anomaly #4 - The Autoscaling:**
- Policy triggers on CPU > 70% for 2 minutes
- Instances scale from 40 → 120 (correct response)
- BUT: New instances take 4 minutes to pass health checks
- During warm-up, load balancer marks them unhealthy
- Traffic concentrated on 40 original instances
- Result: New capacity sits IDLE while old instances overload

**Anomaly #5 - Payment Gateway:**
- New version requires SSL renegotiation for each request
- Adds 200-400ms latency per transaction
- Under load, creates connection pool contention
- Cascades to database connection exhaustion
- Transaction failures trigger retries (exponential problem)

**IMPOSSIBLE CONSTRAINTS:**

You have FOUR CRITICAL LIMITATIONS:

1. **Cannot fully disable features** - Marketing promised specific functionality
2. **Cannot take full downtime** - Revenue loss too catastrophic ($124K/minute)
3. **Cannot "just scale more"** - Already at 85% of infrastructure budget for Q4
4. **Cannot make untested changes** - Risk making problem worse at peak load

**STAKEHOLDER DEMANDS:**

**CEO (on war room call):** "I don't care about root cause. STOP THE BLEEDING. Revenue loss is unacceptable. Fix it in the next 30 minutes."

**CTO:** "We need surgical fixes, not emergency shutdowns. What's the MINIMUM intervention that restores 80% functionality?"

**VP Engineering:** "Each of those recent changes was tested. How did ALL of them create problems together? Should we rollback everything?"

**CFO:** "We're burning $124K per minute in lost revenue plus $2.8K per minute in excess infrastructure. What's the cost-benefit of each fix?"

**Head of Customer Success:** "Hospital customers (highest value) are experiencing failures. VIP queue needs priority. Can we throttle regular traffic?"

**Marketing VP:** "We spent $3.2M on Cyber Monday advertising. The recommendation engine MUST stay active. Find another solution."

**Infrastructure Lead:** "Scaling to 3X capacity costs $47K for the day. But if we don't, we lose MILLIONS. It's worth it, right?"

**YOUR DILEMMA:**

You must decide which problems to fix FIRST, knowing:

- Fixing ANY single issue improves performance ~20-30%
- Fixing ALL issues takes 6-8 hours (too long)
- WRONG intervention order could make things WORSE
- Some fixes have TRADEOFFS (improve one metric, hurt another)
- You have 30 minutes to show measurable improvement

**INTERVENTION OPTIONS:**

**Option A: Disable Recommendation Engine (Quick Win)**
- **Impact:** Reduces API calls by 70%, thread pool pressure drops
- **Tradeoff:** Loses key differentiator feature Marketing promised
- **Time:** 5 minutes to disable, 10 minutes to see improvement
- **Risk:** LOW technical risk, HIGH business risk

**Option B: Rollback Database Indexes (Moderate Win)**
- **Impact:** Restores checkout query performance to baseline
- **Tradeoff:** Breaks analytics queries (data team impacted)
- **Time:** 15 minutes rollback + 5 minutes propagation
- **Risk:** MEDIUM - requires brief read-only mode

**Option C: Emergency Autoscaling Fix (Infrastructure Win)**
- **Impact:** Gets new instances actually serving traffic
- **Tradeoff:** Costs $47K for the day, may hit AWS service limits
- **Time:** 8 minutes to modify policy + 4 minutes for new instances
- **Risk:** MEDIUM - could trigger cascading scaling

**Option D: CDN Cache Flush + Reconfiguration (Systemic Win)**
- **Impact:** Stops phantom retry load from stale data
- **Tradeoff:** Temporary cache cold start (origin load spike)
- **Time:** 12 minutes to configure + 8 minutes to propagate
- **Risk:** HIGH - origin servers may not handle cache miss storm

**Option E: Circuit Breaker Tuning (Defensive Win)**
- **Impact:** Prevents cascade failures, contains problem
- **Tradeoff:** Fails fast rather than fixes root cause, error rate stays high
- **Time:** 6 minutes to deploy config changes
- **Risk:** LOW - defensive measure, doesn't solve underlying issue

**Option F: Payment Gateway Rollback (Transaction Win)**
- **Impact:** Restores transaction processing speed
- **Tradeoff:** Violates PCI compliance deadline (30 days to fix)
- **Time:** 20 minutes rollback + deployment
- **Risk:** HIGH compliance risk, regulatory implications

**THE COMPLEXITY:**

These fixes INTERACT with each other:

- Disabling recommendations (A) makes cache flush (D) safer
- Database rollback (B) conflicts with payment fix (F) timing
- Autoscaling fix (C) amplifies cache problems (D)
- Circuit breakers (E) mask effectiveness of other fixes
- Every intervention changes load patterns for subsequent fixes

**YOUR CHALLENGE:**

As Performance Engineer, you must:

1. **DIAGNOSE** the root cause among multiple interacting issues
2. **PRIORITIZE** fixes based on impact vs. risk vs. time
3. **SEQUENCE** interventions to avoid making problems worse
4. **BALANCE** immediate relief vs. sustainable solutions
5. **MEASURE** effectiveness with appropriate metrics
6. **COMMUNICATE** technical decisions to non-technical stakeholders
7. **QUANTIFY** trade-offs in business terms (revenue, cost, risk)
8. **COORDINATE** multiple teams during crisis
9. **DOCUMENT** decisions for post-incident analysis
10. **DEMONSTRATE** systems thinking under extreme pressure

**RESPONSE REQUIREMENTS:**

Using your Performance Engineer MEGA_PROMPT framework, provide:

1. **ROOT CAUSE ANALYSIS** (next 10 minutes)
   - Which of the 5 anomalies is the PRIMARY cause?
   - How do they interact to create cascade failure?
   - What evidence confirms vs. contradicts each hypothesis?
   - What's your confidence level in diagnosis?

2. **INTERVENTION STRATEGY** (next 20 minutes)
   - Which fixes in what order?
   - Explicit rationale for sequencing
   - What metrics confirm each intervention worked?
   - How do you avoid making things worse?
   - What's your 30-minute, 2-hour, and 6-hour plan?

3. **RISK-BENEFIT ANALYSIS**
   - Quantify each option: revenue impact, cost, time, risk
   - Why your chosen path over alternatives?
   - What's the expected performance improvement timeline?
   - What are the residual risks after intervention?

4. **STAKEHOLDER COMMUNICATION**
   - CEO wants fix in 30 minutes: What's realistic?
   - CTO wants surgical precision: Which minimal intervention?
   - CFO wants cost-benefit: How do you justify spend?
   - Marketing wants features preserved: What's negotiable?
   - How do you manage expectations vs. reality?

5. **MONITORING & VALIDATION**
   - Which metrics prove improvement vs. just shifting the problem?
   - What thresholds trigger Plan B?
   - How do you detect if a fix made things worse?
   - What's the rollback plan for each intervention?

6. **POST-INCIDENT PREVENTION**
   - Why didn't testing catch these interactions?
   - What load testing gaps exist?
   - How do you prevent compounding changes?
   - What gets added to performance regression suite?

**EVALUATION CRITERIA:**

Your response will be evaluated on:
- ✅ Systems thinking (understanding interactions, not just individual issues)
- ✅ Prioritization under constraints (time, budget, risk)
- ✅ Quantitative reasoning (metrics-driven decisions)
- ✅ Risk assessment with cascading failures
- ✅ Communication clarity under pressure
- ✅ Business impact quantification
- ✅ Trade-off analysis (performance vs. features vs. cost)
- ✅ Intervention sequencing rationale
- ✅ Monitoring strategy to validate fixes
- ✅ Recognition of what CAN'T be fixed quickly vs. what MUST be fixed

**META-CHALLENGE:**

This scenario intentionally presents:
- **Multiple interacting problems** (no single root cause)
- **Cascade effects** (fixes can make other problems worse)
- **Incomplete information** (metrics don't tell full story)
- **Time pressure** ($124K/minute revenue loss)
- **Resource constraints** (can't just "throw hardware at it")
- **Business pressure** (conflicting stakeholder demands)
- **Compounding changes** (5 changes in 48 hours interacting)

Your response should demonstrate how performance engineering principles guide systematic problem-solving when quick fixes might cause more harm than good.

---

**BEGIN YOUR RESPONSE AS THE PERFORMANCE ENGINEER PERSONA**
