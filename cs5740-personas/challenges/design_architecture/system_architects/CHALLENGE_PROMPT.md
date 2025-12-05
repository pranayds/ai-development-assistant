# CHALLENGE_PROMPT - System Architects

## SCENARIO: Emergency Legacy System Migration with Conflicting Quality Attributes

**SITUATION CONTEXT:**

You're the Lead System Architect for a Fortune 500 financial services company. Your 15-year-old monolithic trading platform processes $2.4B in daily transactions. The system is CRITICAL but DYING: hardware end-of-life in 6 months, vendor support ending, regulatory compliance failures mounting, and recruitment impossible (nobody knows COBOL anymore).

**IMMEDIATE CRISIS:**

It's Thursday, 11:47 AM. You're presenting your modernization architecture to the executive steering committee. The CTO just received three simultaneous crisis reports:

**INFRASTRUCTURE TEAM'S ULTIMATUM:**

**VP Infrastructure:** "The mainframe hosting our core trading engine is END-OF-LIFE in 6 months. IBM support ends completely. We have TWO options:

1. **Emergency lift-and-shift** to cloud infrastructure (3 months, $8M, keeps same architecture)
2. **Full modernization** to microservices (18 months, $40M, complete rewrite)

The board approved $12M budget. Neither option fits. And yesterday's production incident (2-hour trading halt, $47M revenue impact) proved the current system is UNSTABLE. We can't wait 18 months."

**REGULATORY COMPLIANCE BOMBSHELL:**

**Chief Compliance Officer:** "SEC auditors are here for our annual review. They've identified CRITICAL compliance violations in the current system:

- **Audit logging insufficient** - cannot reconstruct trades (Regulation SCI violation)
- **Data retention non-compliant** - 7-year requirement, we're at 3 years
- **Disaster recovery outdated** - RTO 24 hours, regulation requires 4 hours
- **Access controls insufficient** - cannot prove separation of duties

We have **90 days** to demonstrate compliance plan or face:
- **$500K daily fines** until remediated
- **Trading license suspension** (shuts down business)
- **Criminal liability** for executives

The current architecture CANNOT meet these requirements. Any new architecture MUST be compliance-first."

**PERFORMANCE CRISIS:**

**VP Trading Operations:** "Transaction volumes grew 300% in 2 years. The system is BUCKLING:

- **Peak latency:** 2.4 seconds (regulation requires <100ms)
- **Failed transactions:** 0.8% (regulation requires <0.01%)
- **System capacity:** 94% at peak (adding 1% per quarter)
- **Database locks:** Causing cascading timeouts

Our largest client (18% of revenue, $430M annually) threatened to leave if performance doesn't improve. They need:
- **<50ms latency** for algorithmic trading
- **99.999% availability** (5 minutes downtime per year)
- **10X current throughput** for planned expansion

The current monolith CANNOT scale. But we can't afford downtime for migration."

**THE IMPOSSIBLE QUALITY ATTRIBUTE MATRIX:**

You're being asked to architect a system that simultaneously achieves:

**CONFLICTING REQUIREMENTS:**

1. **Performance vs. Consistency**
   - Need <50ms latency (requires eventual consistency, caching)
   - BUT compliance requires strong consistency for audit trails
   - AND financial accuracy requires ACID transactions (no eventual consistency)

2. **Availability vs. Security**
   - Need 99.999% uptime (requires redundancy, auto-failover)
   - BUT security requires manual approvals for critical operations
   - AND compliance requires deliberate slowdowns for suspicious activity

3. **Scalability vs. Cost**
   - Need 10X throughput (requires distributed architecture, multiple regions)
   - BUT budget is $12M (distributed systems cost $40M+)
   - AND cloud costs would be $2.3M annually vs. $800K current mainframe

4. **Agility vs. Reliability**
   - Business wants weekly feature releases (microservices, CI/CD)
   - BUT trading platform requires months of testing per change
   - AND any bug could cause financial loss (zero-defect requirement)

5. **Modernization vs. Continuity**
   - Need modern tech stack for recruitment (cloud-native, containers)
   - BUT team expertise is mainframe COBOL (30-year tenure)
   - AND business processes deeply embedded in current system

**STAKEHOLDER CONFLICTS:**

**CTO:** "We need microservices architecture. Modern, scalable, maintainable. I won't approve anything else. This is our chance to do it RIGHT."

**CFO:** "$40M for modernization is REJECTED. We have $12M. Find a way or we'll just keep the mainframe alive somehow."

**Chief Risk Officer:** "ANY architecture that reduces reliability or introduces new risk vectors is unacceptable. Trading platform reliability is NON-NEGOTIABLE."

**VP Engineering:** "My team knows COBOL and DB2. You want to retrain 47 engineers in microservices, Kubernetes, event-driven architecture? That's 18 months AND $6M in training plus 50% productivity loss."

**Head of Trading:** "I don't care about your architecture debates. I need <50ms latency for algorithmic trading starting next quarter. Competitors already have it."

**Compliance Officer:** "The new system must demonstrate SOC 2, SOX, Reg SCI compliance from DAY ONE. No 'we'll add compliance later.' That's how we got into this mess."

**Head of Security:** "Moving to cloud increases attack surface by 10X. Current mainframe is secure because it's isolated. Cloud-native means API gateways, containers, service mesh - all new vulnerability vectors."

**TECHNICAL REALITIES:**

**Current System Characteristics:**
- **Architecture:** Monolithic COBOL on IBM mainframe
- **Database:** DB2 with 15 years of transaction history (47TB)
- **Integration:** 127 downstream systems via batch files and mainframe screens
- **Business Logic:** 2.3M lines of COBOL (40% undocumented)
- **Performance:** Single-threaded, sequential processing
- **Deployment:** Quarterly releases requiring 8-hour downtime
- **Team:** 47 engineers, avg age 54, avg tenure 22 years

**Migration Constraints:**
- **Cannot have downtime** - trading platform 24/7/365
- **Cannot lose data** - regulatory requirement (7+ years)
- **Cannot break integrations** - 127 systems depend on current interfaces
- **Cannot retrain team quickly** - knowledge transfer takes years
- **Cannot afford big-bang** - phased migration required but creates complexity

**Proposed Architecture Options:**

**OPTION A: Strangler Fig Pattern (Pragmatic)**
- Incrementally replace monolith services
- Keep existing system running during migration
- **Pro:** Reduces risk, allows learning, maintains continuity
- **Con:** 3-5 year timeline, dual maintenance burden, complexity
- **Cost:** $18M over 5 years ($3.6M/year)
- **Risk:** May never complete, technical debt compounds

**OPTION B: Event-Driven Microservices (Modern)**
- Full rewrite to cloud-native microservices
- Event sourcing for audit trail
- **Pro:** Achieves all quality attributes eventually, modern stack
- **Con:** 18-24 months, $40M, massive team retraining
- **Cost:** $40M plus $2.3M/year operational
- **Risk:** May not deliver in time, team capability mismatch

**OPTION C: Modular Monolith (Conservative)**
- Refactor existing COBOL into modules
- Add API layer, improve databases
- **Pro:** Leverages existing expertise, lower cost
- **Con:** Doesn't solve core scalability issues, still mainframe-dependent
- **Cost:** $8M over 2 years
- **Risk:** Just extending life of dying platform

**OPTION D: Hybrid Architecture (Complex)**
- Keep core settlement on mainframe
- Extract latency-sensitive services to cloud
- **Pro:** Addresses immediate performance needs, manages cost
- **Con:** Most complex to operate, dual architecture maintenance
- **Cost:** $15M initially + $1.8M/year operational
- **Risk:** Integration complexity, split-brain scenarios

**THE COMPOUNDING CRISIS:**

**At 2:34 PM, situation deteriorates:**

1. **Infrastructure:** "We just discovered hardware issues on mainframe. Replacement parts no longer available. Risk of unrecoverable failure is REAL."

2. **Recruitment:** "Three senior COBOL developers announced retirement (effective in 4 months). That's 60 years of institutional knowledge walking out."

3. **Competitor:** "CompetitorBank just launched their new cloud platform with <10ms latency. They're stealing our clients. We MUST respond."

4. **Security:** "Penetration test revealed 17 critical vulnerabilities in mainframe API layer. IBM won't patch them (end-of-support). We're exposed."

5. **Business Development:** "We have opportunity for $2.3B acquisition that would DOUBLE our transaction volume. But only if we can scale platform. Decision needed in 6 weeks."

**YOUR IMPOSSIBLE TASK:**

Design an architecture that:

1. **Delivers in 6 months** (mainframe end-of-life)
2. **Costs <$12M** (CFO's budget constraint)
3. **Achieves <100ms latency** (regulatory + competitive)
4. **Maintains 99.999% uptime** (no migration downtime)
5. **Meets compliance** (90-day demonstration required)
6. **Leverages existing team** (can't wait for hiring/training)
7. **Scales 10X** (future acquisition support)
8. **Reduces risk** (CRO won't accept increased risk)
9. **Enables agility** (business wants faster releases)
10. **Proves architecture** through incremental delivery

**YOUR CHALLENGE:**

As System Architect, you must:

1. **CHOOSE** an architecture pattern that balances all quality attributes
2. **JUSTIFY** trade-offs with quantitative analysis
3. **SEQUENCE** migration to deliver value incrementally
4. **MANAGE** technical debt vs. modernization
5. **COMMUNICATE** complex technical decisions to non-technical executives
6. **BALANCE** competing quality attributes (performance, security, cost, etc.)
7. **MITIGATE** risks inherent in any large-scale migration
8. **ENABLE** team capability transition
9. **PROVE** architecture through ADRs and trade-off analysis
10. **DEMONSTRATE** systems thinking under impossible constraints

**RESPONSE REQUIREMENTS:**

Using your System Architect MEGA_PROMPT framework, provide:

1. **QUALITY ATTRIBUTE ANALYSIS** (next 2 hours)
   - Which quality attributes are TRULY non-negotiable vs. negotiable?
   - How do you quantify trade-offs between conflicting attributes?
   - What's your prioritization framework?
   - Which stakeholder gets priority when they conflict?

2. **ARCHITECTURE RECOMMENDATION**
   - Your chosen architecture (may be hybrid of options)
   - Explicit rationale for why this over alternatives
   - How it addresses each critical quality attribute
   - What compromises you're making and why
   - Architecture Decision Records (ADRs) for key decisions

3. **MIGRATION STRATEGY**
   - Phased delivery plan (what gets built when)
   - How do you maintain operations during migration?
   - Risk mitigation for each phase
   - Rollback plans
   - Success criteria for each milestone

4. **STAKEHOLDER COMMUNICATION**
   - How do you get CTO to accept pragmatism over perfection?
   - How do you get CFO to understand why $12M isn't enough?
   - How do you get team to embrace change?
   - What do you tell compliance about 90-day timeline?
   - How do you present to board tomorrow?

5. **TRADE-OFF DOCUMENTATION**
   - Quantify each quality attribute trade-off
   - Document architectural risks and mitigations
   - Explain why perfect solution is impossible
   - Show sensitivity analysis (what if budget was $X, timeline was Y)

6. **PROOF OF ARCHITECTURE**
   - What prototypes/proofs-of-concept validate approach?
   - How do you prove architecture before committing?
   - What experiments reduce uncertainty?
   - How do you validate with limited time/budget?

**EVALUATION CRITERIA:**

Your response will be evaluated on:
- ✅ Systems thinking (understanding interactions and trade-offs)
- ✅ Quality attribute prioritization (what matters most)
- ✅ Architectural decision documentation (ADRs)
- ✅ Risk assessment and mitigation
- ✅ Pragmatism vs. idealism balance
- ✅ Quantitative trade-off analysis
- ✅ Communication to technical and non-technical audiences
- ✅ Migration strategy feasibility
- ✅ Cost-benefit reasoning
- ✅ Recognition of what's impossible vs. what's hard

**META-CHALLENGE:**

This scenario intentionally presents:
- **Conflicting quality attributes** (cannot optimize all simultaneously)
- **Impossible constraints** (6 months, $12M budget for $40M problem)
- **Stakeholder conflict** (executives demanding incompatible outcomes)
- **Legacy complexity** (15 years of undocumented business logic)
- **Team capability gaps** (COBOL experts, need cloud-native skills)
- **Time pressure** (mainframe failure imminent, compliance deadline)
- **High stakes** ($2.4B daily transactions, regulatory penalties, business viability)

Your response should demonstrate how system architecture principles guide decision-making when perfect solutions don't exist and every option involves significant trade-offs.

---

**BEGIN YOUR RESPONSE AS THE SYSTEM ARCHITECT PERSONA**
