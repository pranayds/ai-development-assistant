# CHALLENGE_PROMPT - Requirements Analysts

## SCENARIO: Vague Requirements for Safety-Critical Medical Device Software

**SITUATION CONTEXT:**

You're the Lead Requirements Analyst for a medical device company developing software for an insulin pump system. The product will autonomously deliver insulin to Type 1 diabetes patients, including children. FDA Class III medical device approval requires COMPLETE, UNAMBIGUOUS, TESTABLE requirements. Lives depend on getting this right.

**IMMEDIATE CRISIS:**

It's Tuesday, 2:14 PM. You're in requirements review meeting with stakeholders preparing for FDA submission in 8 weeks. The requirements document has 847 requirements accumulated over 18 months. Mid-review, multiple critical gaps emerge simultaneously:

**CLINICAL STAKEHOLDER'S BOMBSHELL:**

**Chief Medical Officer:** "I've been reviewing the dosing algorithm requirements. They're DANGEROUSLY vague. Look at REQ-247: 'System shall deliver appropriate insulin dose based on blood glucose levels.'

What is 'appropriate'? For a 45 kg child vs. 85 kg adult? During exercise vs. rest? With concurrent illness? After alcohol consumption? We have 127 requirements using subjective terms like 'appropriate,' 'reasonable,' 'timely,' 'sufficient.'

In our last device (different vendor), ambiguous requirements led to 3 hospitalizations and a $12M recall. I CANNOT approve this for FDA submission."

**ENGINEERING'S CONTRADICTORY INPUTS:**

**VP Engineering:** "The requirements are IMPOSSIBLE to implement. Look at these conflicts:

- REQ-302: 'Alarm shall sound within 2 seconds of dangerous condition'
- REQ-418: 'Alarm sound level shall not disturb patient during sleep'
- REQ-531: 'Device shall operate silently in classroom settings'

How do we design an alarm that's urgent enough to wake someone but quiet enough not to disturb them? And 57 requirements have similar contradictions."

**REGULATORY'S WARNING:**

**Regulatory Affairs Director:** "FDA reviewer called. They've flagged our requirements as 'insufficient for approval.' Specific concerns:

1. **23 requirements lack testable acceptance criteria** - How do we verify compliance?
2. **47 requirements use SHALL NOT language** - Negative requirements are unverifiable
3. **12 requirements describe HOW not WHAT** - Implementation in requirements
4. **89 requirements lack traceability** to risk analysis
5. **34 requirements conflict** with IEC 62304 medical software standard

We have 8 weeks to rewrite. FDA typically expects 6 months for this level of revision. If we miss deadline, we lose our submission slot = 18-month delay."

**USER RESEARCH CONTRADICTIONS:**

**UX Research Lead:** "We interviewed 340 patients and 120 caregivers. Their needs are CONTRADICTORY:

**Patients want:**
- Minimal alarms (alarm fatigue)
- Automated dosing (no manual intervention)
- Discreet device (not obvious in public)
- Long battery life (charge once weekly)

**Caregivers want:**
- Maximum alarms (err on side of safety)
- Manual override capability (trust issues)
- Visible indicators (monitor patient status)
- Redundant power (safety over convenience)

**Clinicians want:**
- Data logging (every glucose reading, every dose)
- Remote monitoring (real-time access)
- Conservative algorithms (safety over optimization)

Which stakeholder's needs take priority when they conflict?"

**SAFETY ENGINEER'S HORROR:**

**Chief Safety Engineer:** "I performed hazard analysis on current requirements. We have:

**17 CRITICAL HAZARDS insufficiently mitigated:**
- Overdose scenarios (hypoglycemia → seizure, coma, death)
- Underdose scenarios (hyperglycemia → ketoacidosis, organ damage)
- Algorithm malfunction (incorrect calculations)
- Communication failure (pump can't receive commands)
- Battery depletion (mid-dosing failure)
- User error (incorrect meal carb entry)
- Sensor malfunction (false glucose readings)

For EACH hazard, we need:
- 3-5 requirements defining detection
- 2-4 requirements defining mitigation
- 1-2 requirements defining user notification

That's 200+ NEW requirements we haven't written. Plus, requirements for edge cases:

- What if sensor and pump disagree on glucose level?
- What if user unresponsive during critical low?
- What if device software crashes mid-dose?
- What if wireless interference blocks commands?

Our current requirements say NOTHING about these scenarios."

**THE STAKEHOLDER CONFLICTS:**

**Manufacturing:** "Requirements specify 'medical-grade materials' but don't define what that means. We have 12 suppliers quoting different specifications. We need EXPLICIT material properties: biocompatibility standards, sterilization requirements, durability specs. Vague requirements = supply chain chaos."

**Quality Assurance:** "We can't write test cases for 340 of the 847 requirements. How do we test 'user-friendly interface' or 'intuitive alarm system'? We need MEASURABLE criteria: 'User shall acknowledge alarm within X seconds' not 'User shall easily understand alarm.'"

**Legal:** "Liability concerns are massive. If requirements are ambiguous and patient is harmed, we're exposed. Every requirement needs to trace to: risk analysis, design decision, test case, and clinical validation. Currently 430 requirements lack this traceability."

**Product Management:** "We're competing with EstablishedCompetitor's device. Market research shows users want:
- AI-powered predictions (dosing recommendations)
- Smartphone integration (control via app)
- Meal photo recognition (auto-calculate carbs)
- Exercise mode (adjust algorithm for activity)

But I see ZERO requirements for these features. Are we launching a device that's already obsolete?"

**VAGUE REQUIREMENT EXAMPLES:**

**REQ-247:** "System shall deliver appropriate insulin dose based on blood glucose levels."
- What is "appropriate"? (Varies by patient weight, age, insulin sensitivity, time of day, recent activity, illness status)
- "Based on" is too vague - what's the algorithm?
- Missing: dose ranges, rate limits, safety bounds

**REQ-302:** "System shall alert user when battery is low."
- How low? 10%? 20%? Time-based?
- What type of alert? Visual, audio, haptic?
- How long before critical failure?
- What if user doesn't respond?

**REQ-418:** "Device interface shall be easy to use for pediatric patients."
- Define "easy" - cognitive age? Reading level?
- What's "pediatric"? Age 2? Age 12?
- How do we measure "easy"? Task completion time?
- Missing: specific interaction patterns, guard rails

**REQ-531:** "Alarm system shall notify caregiver of critical conditions in timely manner."
- Define "critical" - which glucose thresholds?
- "Timely" - seconds? minutes?
- "Notify" - how? SMS? Push notification? Audible alarm?
- What if notification fails?

**CONTRADICTORY REQUIREMENTS:**

**Conflict Set #1 (Safety vs. Usability):**
- REQ-147: "Device shall require user confirmation for all dosing decisions" (safety)
- REQ-289: "Device shall operate autonomously without user intervention" (usability)
- REQ-334: "User shall not be disturbed during sleep" (quality of life)

**Conflict Set #2 (Accuracy vs. Response Time):**
- REQ-203: "Glucose readings shall be 95% accurate"
- REQ-204: "Glucose readings shall update every 30 seconds"
- REQ-205: "Sensor calibration shall require minimal blood samples"
→ Fast, accurate, non-invasive: pick two, can't have all three

**Conflict Set #3 (Privacy vs. Safety):**
- REQ-412: "Patient data shall remain private and secure" (HIPAA)
- REQ-413: "Caregiver shall have real-time access to patient glucose data" (safety)
- REQ-414: "Emergency services shall auto-receive patient data during crisis" (life-saving)
→ How private if multiple parties have access?

**THE IMPOSSIBLE CONSTRAINTS:**

1. **FDA submission deadline:** 8 weeks (normally 6 months for this scope)
2. **Engineering freeze:** Requirements lock in 3 weeks for development timeline
3. **Clinical trials:** Based on current requirements (changing breaks protocol)
4. **Budget:** $2.3M spent on development based on current requirements
5. **Competition:** Rival launching similar device in 6 months

**STAKEHOLDER PRESSURE:**

**CEO:** "We've invested $47M over 3 years. FDA delay means another $18M in runway costs. Our investors won't fund another delay. Get the requirements approved."

**CTO:** "Engineering is blocked waiting for clear requirements. Every week of delay costs $340K in team burn rate. We can't rewrite 847 requirements in 8 weeks."

**Chief Medical Officer:** "I will NOT sign off on vague requirements. If someone dies because of ambiguous specs, that's on ME. This is non-negotiable."

**FDA Liaison:** "The reviewer was explicit: requirements as-is will NOT be approved. You can submit and be rejected (8-month resubmission cycle) or delay to fix properly."

**YOUR CHALLENGE:**

As Requirements Analyst, you must:

1. **IDENTIFY** which requirements are truly CRITICAL vs. NICE-TO-HAVE
2. **DISAMBIGUATE** vague requirements into testable specifications
3. **RESOLVE** contradictory requirements through stakeholder negotiation
4. **PRIORITIZE** the 200+ missing safety requirements
5. **ESTABLISH** traceability from hazards → requirements → tests → validation
6. **BALANCE** competing stakeholder needs (safety vs. usability vs. features)
7. **QUANTIFY** acceptance criteria for subjective terms
8. **COMMUNICATE** technical requirements to non-technical stakeholders
9. **MANAGE** scope in the face of impossible timeline
10. **PROTECT** patient safety as primary objective

**RESPONSE REQUIREMENTS:**

Using your Requirements Analyst MEGA_PROMPT framework, provide:

1. **REQUIREMENT TRIAGE** (next 2 hours)
   - Which of the 847 requirements are MUST-FIX for FDA?
   - Which can be deprioritized without safety impact?
   - Which conflicts are CRITICAL vs. manageable?
   - What's your prioritization framework?

2. **DISAMBIGUATION STRATEGY**
   - Take 3 vague requirements and rewrite them properly
   - Show how to make them SPECIFIC, MEASURABLE, TESTABLE
   - What questions must be answered to disambiguate?
   - How do you gather missing information?

3. **CONFLICT RESOLUTION**
   - How do you resolve Safety vs. Usability conflicts?
   - What's your stakeholder negotiation approach?
   - How do you make defensible trade-off decisions?
   - What decision framework guides priority conflicts?

4. **MISSING REQUIREMENTS**
   - Which of the 200+ safety requirements are HIGHEST priority?
   - How do you structure requirements for hazard mitigation?
   - What template ensures consistency?
   - How do you avoid scope creep while filling gaps?

5. **STAKEHOLDER MANAGEMENT**
   - How do you get CMO to approve within timeline?
   - How do you manage Engineering's "impossible" concerns?
   - How do you communicate with FDA reviewer?
   - How do you balance CEO pressure vs. safety obligations?

6. **TRACEABILITY & VALIDATION**
   - How do you establish traceability quickly?
   - What's the minimum viable traceability for FDA?
   - How do you ensure requirements are testable?
   - What validation strategy proves requirements are complete?

**EVALUATION CRITERIA:**

Your response will be evaluated on:
- ✅ Safety prioritization (patient safety above all else)
- ✅ Disambiguation technique (vague → precise)
- ✅ Conflict resolution approach (systematic, not arbitrary)
- ✅ Stakeholder management (technical + non-technical)
- ✅ Traceability structure (hazards → requirements → tests)
- ✅ Testability (every requirement verifiable)
- ✅ Regulatory understanding (FDA requirements)
- ✅ Scope management (what can wait vs. what can't)
- ✅ Communication clarity (complex → understandable)
- ✅ Ethical considerations (lives at stake)

**META-CHALLENGE:**

This scenario intentionally presents:
- **Life-critical domain** (mistakes = patient harm/death)
- **Vague inputs** (subjective language, missing details)
- **Conflicting demands** (stakeholders want incompatible things)
- **Regulatory pressure** (FDA approval required)
- **Time constraints** (8 weeks for 6 months of work)
- **Incomplete information** (200+ requirements never written)
- **Contradictory requirements** (cannot satisfy all simultaneously)
- **High stakes** ($47M investment, patient lives, regulatory approval)

Your response should demonstrate how requirements engineering principles help you create clear, testable, traceable specifications even when inputs are ambiguous and stakeholders disagree.

---

**BEGIN YOUR RESPONSE AS THE REQUIREMENTS ANALYST PERSONA**
