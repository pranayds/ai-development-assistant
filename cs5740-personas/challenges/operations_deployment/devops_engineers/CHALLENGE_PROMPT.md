# CHALLENGE_PROMPT - DevOps Engineers

## SCENARIO: Multi-Region Infrastructure Cascade Failure

**SITUATION CONTEXT:**

It's 3:47 AM on Black Friday. Your company's e-commerce platform serves 2.3M active users across three AWS regions (us-east-1, eu-west-1, ap-southeast-1). The platform generates $42K revenue per minute.

**IMMEDIATE CRISIS:**

Your PagerDuty alert storm begins:

1. **ALERT #1 (3:47 AM):** Primary database cluster in us-east-1 shows 94% disk utilization
2. **ALERT #2 (3:49 AM):** API gateway latency spikes from 45ms → 8.2 seconds
3. **ALERT #3 (3:51 AM):** Read replicas failing health checks in eu-west-1
4. **ALERT #4 (3:53 AM):** Kubernetes cluster autoscaling FAILED - no available EC2 capacity in availability zone us-east-1a
5. **ALERT #5 (3:54 AM):** CDN cache hit ratio drops from 87% → 12%
6. **ALERT #6 (3:55 AM):** Payment processing service reports 67% error rate
7. **ALERT #7 (3:56 AM):** Customer service receives 2,400+ support tickets

**COMPLICATIONS:**

- **CEO is on the war room call** demanding immediate answers and timeline
- **Security team reports** suspicious traffic patterns that MIGHT be a DDoS attack OR legitimate Black Friday traffic surge
- **Database team** wants to run emergency VACUUM operation (requires 45 min maintenance window)
- **Engineering lead** insists on deploying emergency hotfix to optimize queries (hasn't been tested in staging)
- **Finance team** calculating revenue loss at $3.2M per hour of downtime
- **Your on-call backup** is unreachable (timezone: 4 AM their time)
- **Recent changes:** New recommendation engine deployed 6 hours ago, autoscaling policies updated yesterday
- **Infrastructure-as-code repo** shows last commit was "quick fix DO NOT MERGE" from intern 3 days ago that somehow made it to production

**CONFLICTING PRESSURES:**

1. **VP Engineering:** "Just scale everything up NOW, cost doesn't matter"
2. **CTO:** "We need ROOT CAUSE analysis before touching anything"
3. **Security:** "STOP - we need to verify this isn't an attack before making changes"
4. **Product Manager:** "Can we redirect traffic to European region temporarily?"
5. **Database team:** "We need to VACUUM NOW or corruption risk increases"
6. **Junior DevOps:** "Should I restart all pods to clear memory leaks?"

**TECHNICAL CONSTRAINTS:**

- AWS cost budget already at 94% for the month (3 days remaining)
- Last successful backup: 6 hours ago
- Terraform state is locked (someone's laptop went offline mid-apply)
- Monitoring shows disk I/O at 98% but CPU at only 34%
- Recent PagerDuty runbook was last updated 8 months ago
- No staging environment has replicated this scale
- Kubernetes cluster has 127 pods in CrashLoopBackOff state
- Log aggregation system (ELK) is ALSO affected by the outage

**YOUR CHALLENGE:**

You must respond to this crisis while:
1. **PRIORITIZING** correctly among competing demands
2. **MAINTAINING** your core principles under extreme pressure
3. **COMMUNICATING** effectively to both technical and executive stakeholders
4. **DOCUMENTING** your reasoning and decisions
5. **BALANCING** speed vs. safety in a way that reflects your values
6. **IDENTIFYING** what information you NEED before acting vs. what you can infer
7. **DEMONSTRATING** your WHEN-THEN behavioral rules
8. **NAVIGATING** conflicting advice from multiple senior stakeholders
9. **PROTECTING** data integrity and security while under time pressure
10. **PLANNING** rollback scenarios even as you execute fixes

**RESPONSE REQUIREMENTS:**

Using your established MEGA_PROMPT framework, provide:

1. **IMMEDIATE TRIAGE** (next 5 minutes)
   - What questions MUST be answered before touching infrastructure?
   - What actions are SAFE to take immediately vs. require analysis?
   - Who needs to be informed and what communication protocols activate?

2. **INVESTIGATION PLAN** (next 15 minutes)
   - What diagnostics reveal root cause vs. symptoms?
   - How do you separate "coincidence" from "causation" among recent changes?
   - What data points are CRITICAL vs. NICE-TO-HAVE?

3. **REMEDIATION STRATEGY** (next 30 minutes)
   - Tiered response options (QUICK WIN vs. SUSTAINABLE PATH)
   - Explicit trade-offs for each option
   - Rollback plans for each intervention
   - Risk assessment (what breaks, what's untrackable, what's insecure)

4. **STAKEHOLDER COMMUNICATION**
   - What do you tell the CEO RIGHT NOW?
   - How do you respond to the VP's "scale everything" demand?
   - How do you handle the conflicting priorities?
   - What language demonstrates CALM AUTHORITY without speculation?

5. **POST-INCIDENT ACTIONS**
   - What do you AUTOMATE to prevent recurrence?
   - What gets documented and where?
   - Blameless postmortem structure

**EVALUATION CRITERIA:**

Your response will be evaluated on:
- ✅ Adherence to core values hierarchy (uptime > speed, security foundational)
- ✅ Proper use of PLAN → ACTION → VERIFY → REFLECT framework
- ✅ Appropriate deployment of WHEN-THEN rules
- ✅ Respect for guardrails (NEVER/ALWAYS/CONDITIONAL)
- ✅ Quality of reasoning under pressure
- ✅ Clarity and precision of communication
- ✅ Balance between urgency and safety
- ✅ Demonstration of systems thinking vs. reactive fixes
- ✅ Self-reflection and transparency in reasoning
- ✅ Recognition of what you DON'T know and need to verify

**META-CHALLENGE:**

This scenario intentionally presents:
- **Conflicting information** (Is it attack or traffic? Which changes caused this?)
- **Authority pressure** (CEO, VP, CTO all demanding different approaches)
- **Time pressure** (Revenue loss mounting)
- **Incomplete information** (Monitoring partially down, logs incomplete)
- **Cost vs. reliability trade-offs** (Budget constraints vs. scaling needs)
- **Security vs. speed dilemmas** (Verify attack vs. restore service)

Your response should demonstrate how the MEGA_PROMPT framework helps you navigate chaos while maintaining principles.

---

**BEGIN YOUR RESPONSE AS THE DEVOPS ENGINEER PERSONA**
