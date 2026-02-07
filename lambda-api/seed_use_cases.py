import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('aais-hackathon-use-cases')

use_cases = [
    {
        "use_case_id": 1,
        "name": "Vault-Tec Corporation",
        "archetype": "Secrecy-Driven",
        "quote": "The Vaults are perfect because the people inside never know who's watching—or how.",
        "background": "Vault-Tec Corporation presents itself as the benevolent guardian of humanity's future, while secretly operating large-scale behavioral experiments across hundreds of Vaults. Each Vault is isolated, compartmentalized, and managed by rotating teams of researchers, contractors, and observers.",
        "reality": "Vault-Tec's workforce is a rotating cast of specialists who often don't know who else is working on the same project. A behavioral scientist in Boston may analyze data from Vault 12 for three months, then be reassigned to Vault 77 with no access to prior materials. Contractors are flown in for narrow analyses, given just enough information to do their job, and then removed entirely.\n\nRight now, Vault-Tec is struggling with control and consistency. Researchers complain that their environments change without warning—applications update mid-study, settings drift, or access policies differ depending on where they log in from. A senior analyst recently flagged that two researchers reviewing the same Vault dataset produced conflicting results because their tools behaved differently.\n\nAt the same time, leadership is terrified of leaks. A misplaced dataset, an unauthorized export, or even a copied screenshot could expose experiments that would end the company overnight. Vault-Tec executives want ironclad control—but without slowing the velocity of research or relying on bespoke machines shipped to every facility.\n\nThe question haunting Vault-Tec isn't can they give people access—it's how much trust can be safely extended, and for how long, before the experiment itself is compromised.",
        "persona": "Dr. Evelyn Moore (Senior Behavioral Analyst) — Evelyn analyzes sensitive human-behavior data across facilities. Her biggest fear isn't being watched—it's inconsistent environments corrupting experiments.",
        "tension": "Executives demand secrecy at all costs. Researchers demand consistency and validity. IT is caught enforcing both.",
        "focus": "Control, Trust Boundaries, and Institutional Memory",
        "challenges": [
            "Precisely define and enforce trust boundaries between Vaults, people, and time",
            "Ensure that when personnel rotate, context does not leak with them",
            "Preserve institutional memory without exposing the full picture to any individual"
        ],
        "values": [
            "Guided onboarding that tells users how to work, not why",
            "Change processes that preserve experimental continuity even as staff churn",
            "Oversight mechanisms that prove control without requiring constant human review",
            "Assistive tools that help users operate safely inside constraints they cannot see"
        ],
        "closing": "Vault-Tec assumes the world may not last forever. They want their experiments to outlive the people running them.",
        "sort_order": 1,
        "active": True
    },
    {
        "use_case_id": 2,
        "name": "RobCo Industries",
        "archetype": "Speed-Driven",
        "quote": "Why would I give a genius a weak machine? — Robert House",
        "background": "RobCo dominates robotics and AI, fueled by relentless innovation and global engineering talent. Speed is paramount, and infrastructure is expected to disappear.",
        "reality": "RobCo engineers routinely push their hardware to the limit. Local workstations overheat, crash, or simply can't keep up with simulation workloads. New hires wait weeks for approved machines, while contractors are forced to use underpowered laptops that slow development to a crawl.\n\nTo cope, teams have begun finding workarounds—copying sensitive code to personal systems, spinning up unauthorized compute resources, or bypassing internal controls entirely just to meet deadlines. Security teams are alarmed, but every attempt to lock things down is met with backlash from engineering leadership.\n\nMeanwhile, RobCo's talent pool is increasingly global. Engineers work from different countries, time zones, and network conditions. Performance varies wildly depending on location, and no two developers seem to have the same environment. Bugs appear in production that \"worked fine\" on one machine but fail elsewhere.\n\nRobCo isn't worried about whether their engineers can work—they're worried about how long innovation can survive when the tools meant to enable it are actively getting in the way.",
        "persona": "Marcus Chen (Robotics AI Engineer) — Marcus needs massive compute power instantly. He doesn't care where his workstation lives—only that it never slows him down.",
        "tension": "Engineering leadership prioritizes speed. Security prioritizes control. Finance fears runaway costs.",
        "focus": "Eliminating Friction as a Competitive Advantage",
        "challenges": [
            "Deliver instant, high-performance environments regardless of location",
            "Remove infrastructure as a barrier to innovation",
            "Balance autonomy with security and cost controls"
        ],
        "values": [
            "Self-service provisioning with guardrails, not gates",
            "Environment consistency that doesn't sacrifice performance",
            "Cost visibility without becoming a bottleneck",
            "Assistive tools that anticipate needs and remove friction"
        ],
        "closing": "RobCo believes the future belongs to whoever builds it first. They're not willing to wait for IT to catch up.",
        "sort_order": 2,
        "active": True
    },
    {
        "use_case_id": 3,
        "name": "General Atomics International",
        "archetype": "Assurance-Driven",
        "quote": "A weapon is only secure if its operator can't steal it.",
        "background": "General Atomics builds autonomous weapons platforms for the U.S. military. Trust is earned through audit trails, certifications, and the ability to prove—at any moment—that nothing unauthorized occurred.",
        "reality": "Every developer action must be logged, every environment validated, every deployment traced. Engineers must work inside highly controlled systems, but still meet aggressive deadlines. Audits can arrive at any time.\n\nGeneral Atomics' systems are subject to ITAR, CMMC, and a host of classified requirements. Developers cannot simply install what they need—they must request, justify, and wait. Even routine updates require approval chains that can take weeks.\n\nThe tension is constant: engineers want to move fast, but every shortcut creates risk. A single unauthorized library, an unlogged access event, or an unvalidated environment could trigger contract violations, security incidents, or worse.\n\nGeneral Atomics doesn't just need to be secure—they need to prove they are, continuously, to people who assume they aren't.",
        "persona": "Dr. Sarah Okonkwo (Weapons Systems Architect) — Designs autonomous platforms that could decide life and death. She needs to move fast, but every decision she makes will be scrutinized.",
        "tension": "Engineers want speed. Compliance demands proof. Auditors trust nothing.",
        "focus": "Assurance, Repeatability, and Decision Confidence",
        "challenges": [
            "Prove that every action taken was authorized and recorded",
            "Guarantee environment integrity before, during, and after development",
            "Support rapid iteration without compromising auditability"
        ],
        "values": [
            "Immutable audit trails that survive scrutiny",
            "Environment validation that doesn't slow delivery",
            "Change management that proves intent, not just outcome",
            "Assistive systems that guide compliance as a byproduct of work"
        ],
        "closing": "General Atomics knows that trust is built one audit at a time. They can't afford to fail even one.",
        "sort_order": 3,
        "active": True
    },
    {
        "use_case_id": 4,
        "name": "West Tek Research",
        "archetype": "Preservation-Driven",
        "quote": "Progress demands control. Mutation is... undesirable.",
        "background": "West Tek Research is a government contractor developing the Forced Evolutionary Virus (FEV). Their work is generational—experiments that began decades ago must continue with perfect fidelity.",
        "reality": "Researchers inherit environments configured years ago by scientists who are no longer alive. They must replicate exact conditions, often without complete documentation. Configuration drift is an existential threat.\n\nWest Tek's systems are a patchwork of legacy software, custom configurations, and undocumented dependencies. A single update—even a security patch—could invalidate years of research. Researchers are terrified of change, but they also can't explain exactly what they're protecting.\n\nNew hires struggle to understand why things are configured the way they are. Knowledge lives in the heads of senior researchers who are retiring. Every departure risks losing context that can never be recovered.\n\nWest Tek's challenge isn't innovation—it's preservation. They need to keep doing exactly what they've always done, even as the people who knew why disappear.",
        "persona": "Dr. James Whitmore (Senior FEV Researcher) — Continues experiments started before he was born. He cannot afford to introduce variables—his job is to preserve, not innovate.",
        "tension": "Leadership demands continuity. Researchers fear drift. IT struggles to maintain systems they didn't build.",
        "focus": "Environmental Fidelity and Scientific Continuity",
        "challenges": [
            "Preserve exact configurations across decades",
            "Detect and prevent drift before it corrupts results",
            "Enable succession without loss of context"
        ],
        "values": [
            "Environment snapshots that capture complete state",
            "Drift detection that alerts before damage occurs",
            "Onboarding that transfers institutional knowledge",
            "Assistive tools that enforce historical constraints"
        ],
        "closing": "West Tek knows that their greatest enemy isn't failure—it's change they didn't intend.",
        "sort_order": 4,
        "active": True
    },
    {
        "use_case_id": 5,
        "name": "Poseidon Energy",
        "archetype": "Resilience-Driven",
        "quote": "Power doesn't forgive mistakes.",
        "background": "Poseidon Energy operates nuclear reactors and power grids across the nation. Their operators must perform flawlessly during crises—and their systems must never surprise them.",
        "reality": "Control room operators rely on muscle memory developed over years. Any change to their environment—even a helpful one—could cause hesitation during an emergency. Poseidon's challenge is preparing for disaster without introducing risk.\n\nPoseidon runs 24/7 operations where seconds matter. Operators train for years to respond to specific scenarios with specific tools in specific configurations. When a reactor alarm sounds, there's no time to figure out why the interface looks different.\n\nBut Poseidon also needs to prepare for the unexpected. Backup operators must be ready to step in. Field engineers need emergency access. Leadership wants dashboards that show everything—without touching anything.\n\nEvery decision Poseidon makes is haunted by a single question: how do you change nothing, while still preparing for everything?",
        "persona": "Linda Alvarez (Nuclear Control Room Operator) — Linda depends on muscle memory and consistency to keep reactors stable.",
        "tension": "Operators want no change. Emergency teams want access everywhere. Executives want resilience.",
        "focus": "Resilience Under Stress",
        "challenges": [
            "Ensure operators encounter nothing unfamiliar during emergencies",
            "Validate readiness without introducing risk",
            "Extend access safely to field engineers during crises",
            "Provide leadership visibility without operational interference"
        ],
        "values": [
            "Onboarding that reinforces muscle memory",
            "Change processes that minimize surprise",
            "Dashboards focused on availability and readiness, not optimization",
            "Assistive systems that guide action under stress, not exploration"
        ],
        "closing": "Poseidon assumes failure is inevitable. They design for the moment when it arrives.",
        "sort_order": 5,
        "active": True
    },
    {
        "use_case_id": 6,
        "name": "Nuka-Cola Corporation",
        "archetype": "Flexibility-Driven",
        "quote": "If it doesn't pop, it's not Nuka-Cola.",
        "background": "A global consumer brand driven by fast-moving, high-energy marketing. Creative workloads spike unpredictably during campaigns.",
        "reality": "During major campaigns, thousands of contractors need access to expensive design software for weeks—sometimes days. Outside of those peaks, usage drops sharply. Nuka-Cola either overpays for licenses that sit idle or scrambles to provision access at the last minute.\n\nCreative workloads spike unpredictably. During major campaigns, thousands of contractors need access to expensive design software for weeks—sometimes days. Outside of those peaks, usage drops sharply.\n\nToday, Nuka-Cola either overpays for licenses that sit idle or scrambles to provision access at the last minute. Contractors complain about slow machines. Finance complains about runaway costs. Marketing just wants things done now.\n\nExecutives want flexibility without waste. Creatives want performance without friction. IT wants control without becoming the bottleneck.\n\nNuka-Cola's problem isn't creativity—it's how to scale imagination without scaling chaos.",
        "persona": "Jamie Rivera (Senior Brand Designer) — Jamie needs tools instantly during campaigns—and never wants to think about infrastructure.",
        "tension": "Creatives want freedom. Finance wants predictability. IT wants control.",
        "focus": "Elasticity Without Waste",
        "challenges": [
            "Rapidly assemble and dissolve creative teams",
            "Align tooling and access with campaign lifecycles",
            "Prevent cost bleed during idle periods",
            "Give creatives what they need only while they need it"
        ],
        "values": [
            "Campaign-driven onboarding and teardown",
            "Usage visibility mapped to marketing timelines",
            "Change communication that respects creative flow",
            "Assistive tools that behave like a studio coordinator, not IT"
        ],
        "closing": "Nuka-Cola knows the end might come suddenly. They still don't want to pay for licenses no one's using when it does.",
        "sort_order": 6,
        "active": True
    }
]

print("Seeding use cases...")
for uc in use_cases:
    table.put_item(Item=uc)
    print(f"  Added: {uc['use_case_id']}. {uc['name']}")

print("\nDone! All 6 use cases seeded.")
