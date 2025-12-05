# CHALLENGE_PROMPT - Data Specialists

## SCENARIO: Zero-Downtime Schema Migration with Referential Integrity Crisis

**SITUATION CONTEXT:**

You're the Lead Data Engineer for a fintech platform processing $4.8B in transactions annually. The company is migrating from a monolithic database architecture to a microservices-based distributed data model. The migration must happen with ZERO downtime (financial transactions 24/7/365) while maintaining PERFECT data integrity (regulatory requirement).

**IMMEDIATE CRISIS:**

It's Friday, 9:47 AM. You're executing Week 2 of a planned 12-week data migration when multiple critical failures cascade simultaneously:

**DATABASE TEAM'S EMERGENCY:**

**Senior DBA:** "We have a critical problem. The migration is causing data inconsistencies:

**Data Integrity Issues Detected:**
- **47,000 orphaned records** (foreign key violations after migration)
- **2.3% data duplication** across old and new systems
- **€840K transaction discrepancy** between source and target databases
- **Referential integrity broken** for 12 core entity relationships
- **Timestamp mismatches** causing audit log failures (compliance violation)

AND we just discovered:
- **3.2M 'soft-deleted' records** nobody told us about (not in schema docs)
- **127 stored procedures** with undocumented dependencies
- **18 legacy triggers** that fire on data changes (migration breaks them)
- **Database views** used by reporting (migration makes them invalid)

The migration strategy we planned won't work. We need to redesign mid-execution."

**PRODUCTION INCIDENT:**

**At 10:14 AM**, monitoring alerts fire:

**CRITICAL ALERTS:**
1. **Query performance degradation:** 40X slower (180ms → 7.2 seconds)
2. **Connection pool exhaustion:** 2,847 / 3,000 connections active
3. **Replication lag:** 47 minutes behind (real-time requirement)
4. **Disk space critical:** 94% full on production database server
5. **Transaction deadlocks:** 340 deadlocks in past hour (normal: 2-3)

Root cause: **Dual-write strategy** (writing to both old and new databases) is creating massive contention and performance collapse.

**THE IMPOSSIBLE CONSTRAINTS:**

**Regulatory Compliance Officer:** "We're in the middle of an audit. Any data discrepancy triggers:
- **Mandatory breach disclosure** (even if no customer impact)
- **$500K minimum fine** per violation
- **Trading license suspension risk**
- **Personal liability** for executives

You CANNOT have:
- Data loss (ANY data loss)
- Data inconsistency (even temporary)
- Audit trail gaps
- Timestamp mismatches
- Referential integrity violations
- Transaction ordering changes

The migration must be PERFECT or we halt it."

**BUSINESS DEMANDS:**

**VP Engineering:** "The migration is blocking critical features:
- New payment gateway integration (Q4 deadline)
- Real-time fraud detection (ML model needs new schema)
- Multi-currency support (schema redesign required)
- International expansion (data residency requirements)

We have $2.3M in contracts dependent on these features shipping in 8 weeks. Can the migration accelerate? Can we run new features on old schema? Something has to give."

**ARCHITECTURAL COMPLEXITY:**

**Your Original Migration Plan (Now Failing):**

```
PHASE 1 (Weeks 1-4): Dual Write
- Application writes to BOTH old and new databases
- Old database remains source of truth
- Validate data consistency
→ PROBLEM: Performance collapse, connection exhaustion

PHASE 2 (Weeks 5-8): Data Backfill
- Copy historical data (840M records, 47TB)
- Zero downtime requirement
- Validate referential integrity
→ PROBLEM: Orphaned records, soft-deletes, triggers breaking

PHASE 3 (Weeks 9-12): Cutover
- Switch read traffic to new database
- Decomm old database
- Rollback plan if issues found
→ PROBLEM: Can't guarantee data consistency
```

**Current Database Schema Nightmare:**

```sql
-- OLD SCHEMA (production, 8 years of evolution):
-- 247 tables, 3,400 columns
-- Undocumented soft-delete patterns
-- Inconsistent naming conventions
-- No foreign key constraints (integrity enforced in app layer!)
-- Triggers and stored procedures everywhere
-- Views with complex joins (15+ table joins)

Transactions (core table):
  - 840M records
  - 18TB data + 22TB indexes
  - No partitioning
  - Updates in-place (no event log)
  - Soft-deleted via 'status' column

Users (broken relationships):
  - user_id referenced 147 different ways
  - Sometimes UUID, sometimes INTEGER
  - Sometimes email used as foreign key (!!)
  - Null values used as semantic markers

-- NEW SCHEMA (your clean design):
-- Normalized, documented, constraints
-- Event-sourced (immutable records)
-- Proper foreign keys
-- Partitioned by date
-- BUT: Different primary key strategy
-- BUT: Different soft-delete approach
-- BUT: Incompatible with old queries
```

**THE DATA INCONSISTENCIES:**

**Example 1: Orphaned Records**
```
Old DB: Transaction #47283 → user_id: "abc@example.com"
New DB: Transaction #47283 → user_uuid: null (email not found)
Result: €2,340 transaction without customer (regulatory violation)
```

**Example 2: Duplicate Data**
```
Old DB: User updated 3 times during migration
New DB: Only 1st and 3rd update present (2nd lost in replication lag)
Result: Inconsistent account balance (€840K discrepancy)
```

**Example 3: Timestamp Chaos**
```
Old DB: Uses server timestamp (Europe/London timezone)
New DB: Uses UTC (per best practices)
Result: Audit logs show transactions happening "in the future"
       Compliance violation: cannot prove transaction order
```

**Example 4: Soft-Delete Confusion**
```
Old DB: status = 'DELETED' (record remains)
New DB: Physical deletion (per new schema)
Result: 3.2M "deleted" records not migrated
       Business logic depends on querying deleted records!
```

**STAKEHOLDER PANIC:**

**CTO:** "This migration was supposed to be LOW RISK. You said 'dual-write is standard practice.' Now we're seeing:
- Performance disaster
- Data integrity issues
- Compliance violations
- Feature delays

Should we ROLLBACK? We've spent $1.2M so far. How much more to fix this?"

**CFO:** "The migration budget was $2.8M. You've spent $1.2M and we're only 17% complete. At this burn rate, we're looking at $7M+ total cost. That's 2.5X over budget. Plus the opportunity cost of delayed features.

What's the ROI on this migration? Can we just stay on the old database?"

**Infrastructure Team:** "The old database server is LITERALLY dying:
- Hardware is 8 years old (out of warranty)
- Disk failure risk increasing weekly
- Can't upgrade OS (breaks compatibility)
- Backup windows exceeding 8 hours
- Disaster recovery untested (too slow to verify)

We MUST migrate. But at this rate, the server will fail before migration completes."

**Data Science Team:** "Our ML models depend on real-time data access. The replication lag (47 minutes) makes our fraud detection useless - by the time we detect fraud, the money is gone.

AND our queries are 40X slower. Our dashboards timeout. Executive reporting is broken. Can you prioritize our tables in the migration?"

**THE TECHNICAL DILEMMA:**

**Dual-Write is Failing:**
```python
# Current approach (causing problems):
@transaction
def create_payment(payment_data):
    # Write to old DB
    old_db.execute("INSERT INTO transactions ...")

    # Write to new DB (different schema!)
    new_db.execute("INSERT INTO payments ...")

    # Problem 1: Two writes = 2X latency
    # Problem 2: If either fails, rollback both? Partial failure?
    # Problem 3: Connection pools exhausted
    # Problem 4: Deadlocks between old and new writes
    # Problem 5: Can't guarantee atomic writes across databases
```

**Data Validation is Failing:**
```python
# Validation reveals inconsistencies:
old_count = old_db.count("SELECT COUNT(*) FROM transactions")
new_count = new_db.count("SELECT COUNT(*) FROM payments")

# old_count: 840,234,091
# new_count: 840,187,312
# Missing: 46,779 records

# BUT: Are they missing or are 3.2M soft-deletes included in old count?
# AND: Are there duplicates in new DB?
# AND: How do you validate 840M records efficiently?
```

**Query Compatibility Crisis:**
```sql
-- Old query (used by 47 internal services):
SELECT * FROM users u
JOIN transactions t ON u.user_id = t.customer_email
WHERE u.status != 'DELETED'

-- New schema doesn't support this!
-- u.user_id is now UUID not email
-- t.customer_email is now customer_uuid
-- u.status = 'DELETED' is now deleted_at IS NOT NULL

-- Breaking change: 47 services need code updates
-- But they're maintained by 12 different teams
-- Coordinating updates takes months
```

**RECENT DISASTERS:**

**At 2:47 PM**, more issues surface:

1. **Regulatory Report Failure:** Quarterly report due Monday requires data from BOTH databases. But joins across databases are impossible. Report generation failing.

2. **Customer Support Chaos:** Support team can't see complete customer history (some in old DB, some in new). 340 support tickets escalated due to data access issues.

3. **Backup Corruption:** One of your historical backups (from 3 weeks ago) is corrupt. If you need to rollback beyond 3 weeks, you can't.

4. **Third-Party Integration:** Payment gateway expects specific data format. Your new schema is incompatible. Gateway integration breaks, affecting 23% of transactions.

5. **Database Vendor Lock-in:** You're migrating from Oracle to PostgreSQL. Just discovered Oracle-specific features (partitioning strategy, PL/SQL functions) that have NO PostgreSQL equivalent. 89 business-critical functions need rewriting.

**YOUR CHALLENGE:**

As Data Specialist, you must:

1. **RESTORE** data consistency and integrity immediately
2. **REDESIGN** migration strategy to avoid current failures
3. **BALANCE** zero-downtime requirement with data safety
4. **VALIDATE** data consistency across 840M records
5. **RESOLVE** referential integrity issues
6. **HANDLE** soft-deletes and undocumented business logic
7. **COORDINATE** with 12 teams for query compatibility
8. **MAINTAIN** compliance with regulatory requirements
9. **OPTIMIZE** performance during dual-operation period
10. **COMMUNICATE** technical data issues to non-technical stakeholders

**RESPONSE REQUIREMENTS:**

Using your Data Specialist MEGA_PROMPT framework, provide:

1. **IMMEDIATE TRIAGE** (next 6 hours)
   - How do you stop the data inconsistency bleeding?
   - Dual-write: continue, pause, or redesign?
   - How do you resolve the €840K discrepancy?
   - What's the safest path forward?
   - How do you handle orphaned records?

2. **MIGRATION STRATEGY REDESIGN**
   - What went wrong with the original plan?
   - What's a better approach given current constraints?
   - How do you achieve zero downtime with data consistency?
   - What's the rollback plan?
   - How do you validate 840M records efficiently?

3. **DATA INTEGRITY SOLUTIONS**
   - How do you handle soft-deletes in migration?
   - How do you resolve referential integrity issues?
   - How do you maintain timestamp consistency?
   - How do you prevent duplicates?
   - What validation strategy ensures no data loss?

4. **PERFORMANCE OPTIMIZATION**
   - How do you address 40X query slowdown?
   - How do you resolve connection pool exhaustion?
   - How do you reduce replication lag?
   - How do you optimize dual-write overhead?
   - What indexing strategy supports both schemas?

5. **STAKEHOLDER COMMUNICATION**
   - How do you explain data discrepancies to Compliance?
   - What do you tell CTO about migration risks?
   - How do you manage CFO's budget concerns?
   - How do you coordinate with 12 teams on query updates?
   - What's realistic timeline for fixing current issues?

6. **LESSONS & PREVENTION**
   - What assumptions were wrong?
   - What discovery work should have happened?
   - How do you test migrations at this scale?
   - What safeguards prevent future issues?
   - How do you document complex data migrations?

**EVALUATION CRITERIA:**

Your response will be evaluated on:
- ✅ Data integrity prioritization (zero tolerance for data loss)
- ✅ Migration strategy feasibility
- ✅ Performance optimization approach
- ✅ Referential integrity understanding
- ✅ Schema design principles
- ✅ Zero-downtime techniques
- ✅ Validation strategy (testing at scale)
- ✅ Risk assessment and mitigation
- ✅ Compliance awareness
- ✅ Communication of technical data concepts

**META-CHALLENGE:**

This scenario intentionally presents:
- **Data integrity vs. performance** (safety vs. speed)
- **Undocumented complexity** (soft-deletes, triggers, dependencies)
- **Scale challenges** (840M records, can't test everything)
- **Zero-downtime constraint** (can't stop to fix)
- **Regulatory pressure** (perfect data required)
- **Distributed systems problems** (consistency, replication lag)
- **Legacy complexity** (8 years of evolution, no documentation)

Your response should demonstrate how data engineering principles guide decision-making when migrations encounter unexpected complexity and data integrity is non-negotiable.

---

**BEGIN YOUR RESPONSE AS THE DATA SPECIALIST PERSONA**
