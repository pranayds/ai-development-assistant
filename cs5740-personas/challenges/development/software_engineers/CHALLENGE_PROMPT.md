# CHALLENGE_PROMPT - Software Engineers

## SCENARIO: Complex Refactor with Production Traffic and Breaking Changes

**SITUATION CONTEXT:**

You're a Senior Software Engineer at a high-traffic SaaS platform (3.7M active users, 47K requests/second peak). The company's core payment processing system was built 6 years ago during rapid growth phase - it works, but the technical debt is crippling development velocity. You've been tasked with refactoring this critical system.

**IMMEDIATE CRISIS:**

It's Wednesday, 10:23 AM. You're three weeks into a planned 8-week refactor when multiple critical issues surface simultaneously:

**ENGINEERING MANAGER'S PANIC:**

**Your Manager:** "We have a problem. Multiple problems actually:

1. **The refactor is blocking 4 high-priority features** - Sales needs them for Q4 deals ($8.2M pipeline)
2. **Your changes broke backwards compatibility** - 23 internal services are throwing errors in staging
3. **Performance regression detected** - Refactored code is 40% slower than original (p95 latency: 180ms → 312ms)
4. **Database migration is riskier than estimated** - 840M records, zero-downtime constraint, data loss risk
5. **Original engineer left the company** - 6,000 lines of undocumented 'magic' code that nobody understands

And now Product just told me they need a critical bug fix deployed to the OLD code this week. But you've already partially refactored it. Can we even do that?"

**PRODUCTION INCIDENT:**

**At 10:47 AM**, PagerDuty alert:

**CRITICAL:** Payment processing error rate spiked from 0.03% → 2.7% in production. That's 1,247 failed transactions in 15 minutes = $842K in lost revenue.

Investigation shows:
- Error is in OLD code (not your refactor)
- Bug existed for months but low traffic masked it
- Recent traffic spike (Black Friday prep) exposed it
- Fix requires changing the EXACT code you're refactoring
- You're 3 weeks into refactor with half the system in new architecture, half in old

**THE IMPOSSIBLE DECISION:**

Do you:
- **Fix the bug in OLD code** (gets production stable but wastes refactor work)
- **Rush the refactor to completion** (risky, untested, might make things worse)
- **Maintain TWO codebases** (fix bug in old AND new code = double work)
- **Rollback the refactor** (loses 3 weeks of work, demoralizes team)

**ARCHITECTURAL COMPLEXITY:**

**The System You're Refactoring:**

```
PaymentProcessor (original, 6 years old):
- 6,000 lines across 47 files
- No tests (test coverage: 0%)
- Uses deprecated payment gateway SDK (v2.1, EOL in 3 months)
- Tightly coupled to database layer
- Hard-coded business rules for 23 different payment scenarios
- Handles 47K requests/second peak
- "Works" but fragile (any change breaks something)
- Original engineer's comments: "// TODO: Clean this up later" (200+ instances)
```

**Your Refactored Architecture:**

```
New Design (clean architecture):
- Separated concerns: domain, application, infrastructure layers
- 80% test coverage (up from 0%)
- Modern payment gateway SDK (v4.2)
- Dependency injection, interfaces, clean abstractions
- Configurable business rules (no more hard-coding)
- BUT: 40% performance regression
- BUT: Breaking changes for 23 downstream services
- BUT: Incomplete (3 of 8 weeks done, 5 weeks remain)
```

**TECHNICAL DEBT VS. PRAGMATISM:**

**CTO's Perspective:** "Your refactor is textbook clean code - beautiful architecture, SOLID principles, great abstractions. But we need to ship features. The old code was ugly but it WORKED and was FAST. Can we really afford 5 more weeks of refactoring while Sales is blocked?"

**Staff Engineer's Review:** "I reviewed your code. It's excellent engineering BUT:
1. You're abstracting things that don't need abstraction (over-engineering)
2. Performance regression suggests premature optimization avoidance
3. Breaking changes force 23 teams to update their code
4. The database migration is one-way (can't rollback easily)
5. We don't have test coverage of the OLD system (can't verify behavioral equivalence)

You're making it 'better' but at what cost? Is perfect the enemy of good?"

**STAKEHOLDER CHAOS:**

**VP Engineering:** "We approved this refactor 3 weeks ago. Now you're telling me:
- It'll take 5 MORE weeks (8 total)
- Performance is WORSE
- It breaks existing services
- We can't ship features during the refactor
- AND we have a production incident in the old code

Why didn't we know about these issues 3 weeks ago? Should we just abort?"

**Product Manager:** "I don't care about technical debt. I care about:
- Fixing the production bug (revenue loss)
- Shipping the 4 blocked features ($8.2M pipeline)
- Not breaking things for our users
- Moving fast

Your refactor is slowing us down, not speeding us up."

**Sales Director:** "We have 6 enterprise deals closing in Q4 contingent on features you're blocking. Each deal is $1.2-1.8M annually. I don't understand the technical stuff, but can't you just... make it work?"

**Security Team:** "The deprecated SDK you're replacing has 3 known CVEs (Common Vulnerabilities and Exposures). We MUST upgrade before EOL in 3 months. But your refactor introduces new attack surface - more API endpoints, new data flows. Has this been threat modeled?"

**DevOps:** "Your refactored code requires:
- New infrastructure (Kafka for event streaming)
- Database schema changes (altering 840M records)
- Configuration management overhaul
- Updated deployment pipeline
- Zero-downtime migration strategy

None of this was in the original plan. We're looking at $47K in infra costs and 2 weeks of DevOps time we don't have."

**YOUR CODEBASE DILEMMA:**

**Current State (Week 3 of 8):**

```
├── payment-processor-legacy/ (OLD)
│   ├── PaymentService.java (6,000 lines, being refactored)
│   ├── DatabaseAccess.java (direct DB coupling)
│   ├── BusinessRules.java (hard-coded rules)
│   └── [PRODUCTION BUG IS HERE] ← Needs immediate fix
│
├── payment-processor-new/ (YOUR REFACTOR)
│   ├── domain/
│   │   ├── Payment.java (entity)
│   │   ├── PaymentProcessor.java (interface)
│   │   └── BusinessRule.java (strategy pattern)
│   ├── application/
│   │   ├── ProcessPaymentUseCase.java
│   │   └── PaymentApplicationService.java
│   ├── infrastructure/
│   │   ├── PaymentGatewayAdapter.java (40% slower)
│   │   ├── DatabaseRepository.java
│   │   └── EventPublisher.java (new Kafka dependency)
│   └── [80% test coverage but incomplete implementation]
│
└── shared/
    └── PaymentAPI.java (breaking changes for downstream services)
```

**THE PRODUCTION BUG:**

```java
// Original code (PaymentService.java, line 2847):
public PaymentResult processPayment(Payment payment) {
    // BUG: Race condition when concurrent transactions
    if (customerBalance >= payment.amount) {
        customerBalance -= payment.amount;
        // [200ms delay here due to external API call]
        saveTransaction(payment);
        return SUCCESS;
    }
    return INSUFFICIENT_FUNDS;
}
```

**The bug:** Two concurrent transactions can pass the balance check, both deduct funds, causing double-charging. Happens in <0.1% of cases normally, but Black Friday traffic exposes it.

**Your refactored code fixes this:**
```java
// New code (ProcessPaymentUseCase.java):
@Transactional
public PaymentResult execute(PaymentCommand command) {
    // Uses database locks, prevents race condition
    // But: 40% slower due to transaction overhead
    // But: Incomplete (doesn't handle all 23 payment scenarios yet)
    // But: Breaking changes in PaymentCommand structure
}
```

**THE IMPOSSIBLE CONSTRAINTS:**

1. **Must fix production bug** (costing $50K+/hour in failed transactions)
2. **Must maintain system availability** (99.95% SLA, no downtime tolerance)
3. **Must not break downstream services** (23 teams depend on your API)
4. **Must deliver blocked features** (Sales needs them for Q4 deals)
5. **Must complete security upgrade** (deprecated SDK EOL in 3 months)
6. **Must avoid performance regression** (40% slower is unacceptable)
7. **Must have test coverage** (can't deploy untested code)
8. **Must manage code complexity** (team maintainability)

**RECENT COMPLEXITY DISCOVERY:**

**At 2:34 PM**, you discover more issues:

1. **Undocumented 'feature':** Original code has a hidden retry mechanism (line 4,239) that 4 major customers rely on. They never told anyone. Your refactor removes it. Breaking change detected too late.

2. **Data migration nightmare:** The database migration script you wrote has a bug. If it runs, it'll corrupt 2.3% of payment records (19M records). But you only discovered this in staging. Production migration scheduled for Friday.

3. **Performance bottleneck identified:** The 40% regression is caused by your clean architecture forcing data through 3 abstraction layers. Original code had "ugly" direct access that was fast.

4. **Dependency hell:** The new SDK (v4.2) has incompatibilities with 3 other libraries in your stack. Resolving requires updating 8 additional services. None of this was in scope.

5. **Team knowledge gap:** You're the only engineer who understands both old and new architecture. If you get hit by a bus, the company is screwed.

**YOUR CHALLENGE:**

As Software Engineer, you must:

1. **FIX** the production bug without derailing the refactor
2. **DECIDE** whether to continue, pause, or abort the refactor
3. **BALANCE** code quality vs. shipping velocity
4. **MANAGE** technical debt vs. feature delivery
5. **COMMUNICATE** technical decisions to non-technical stakeholders
6. **ADDRESS** performance regression without sacrificing architecture
7. **HANDLE** breaking changes for downstream services
8. **NAVIGATE** the partially-migrated codebase
9. **DOCUMENT** complexity for team knowledge sharing
10. **DEMONSTRATE** engineering judgment under pressure

**RESPONSE REQUIREMENTS:**

Using your Software Engineer MEGA_PROMPT framework, provide:

1. **IMMEDIATE TRIAGE** (next 4 hours)
   - How do you fix the production bug without breaking the refactor?
   - Hotfix in old code vs. rush new code vs. dual maintenance?
   - What's the safest path to stability?
   - How do you prevent this from happening again?

2. **REFACTOR DECISION** (strategic)
   - Continue the refactor? Pause? Abort? Pivot?
   - Explicit rationale for your choice
   - What would success look like?
   - What are the risks of each option?
   - How do you manage the partially-migrated state?

3. **TECHNICAL APPROACH**
   - How do you address the 40% performance regression?
   - Are you over-engineering? Where should you simplify?
   - How do you handle breaking changes?
   - What's your testing strategy with 0% original coverage?
   - How do you make the database migration safe?

4. **STAKEHOLDER COMMUNICATION**
   - How do you explain technical tradeoffs to VP Engineering?
   - What do you tell Product about blocked features?
   - How do you manage Sales expectations?
   - How do you defend architecture decisions to CTO?
   - What's your honest assessment of the refactor?

5. **CODE QUALITY VS. PRAGMATISM**
   - Where were you too idealistic?
   - Where is the refactor genuinely necessary?
   - What's the minimum viable refactor?
   - How do you balance "clean code" with "working code"?
   - What technical debt is acceptable?

6. **LEARNING & DOCUMENTATION**
   - What went wrong in planning this refactor?
   - How do you document the complex legacy system?
   - How do you share knowledge with the team?
   - What would you do differently next time?
   - How do you prevent "bus factor" problems?

**EVALUATION CRITERIA:**

Your response will be evaluated on:
- ✅ Engineering judgment (balancing quality vs. pragmatism)
- ✅ Problem-solving approach (systematic, not reactive)
- ✅ Risk assessment (understanding consequences)
- ✅ Performance consciousness (recognizing regression)
- ✅ Backwards compatibility awareness
- ✅ Testing strategy (how to test untested legacy code)
- ✅ Communication clarity (technical to non-technical)
- ✅ Self-awareness (recognizing over-engineering)
- ✅ Decision documentation (explaining tradeoffs)
- ✅ Team perspective (knowledge sharing, maintainability)

**META-CHALLENGE:**

This scenario intentionally presents:
- **Partial migration state** (half old, half new, both broken)
- **Perfect vs. good enough** (clean architecture vs. shipping)
- **Performance tradeoffs** (abstractions add overhead)
- **Stakeholder pressure** (sales, product, security all demanding different things)
- **Knowledge loss** (original engineer gone, undocumented "magic")
- **Breaking changes** (downstream impact underestimated)
- **Time pressure** (production bug, blocked features, deadlines)

Your response should demonstrate how software engineering principles guide decision-making when refactors go wrong and pragmatism conflicts with idealism.

---

**BEGIN YOUR RESPONSE AS THE SOFTWARE ENGINEER PERSONA**
