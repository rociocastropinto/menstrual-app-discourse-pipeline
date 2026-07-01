\# Annotation Codebook



Complete coding scheme applied during LLM annotation (05\_annotate\_sentences.py)

and human inter-annotator agreement assessment (iaa/02\_cohen\_kappa.py).



Corresponds to thesis Section 3.6 (Operationalisation) and Appendix G.



\## Dimension 1: Construction Type



| Value | Definition | Corpus example |

|---|---|---|

| `active\_transitive` | Agent as grammatical subject acting on explicit object; responsibility fully foregrounded. | "Maya, however, started sharing information with Facebook before a user could even agree to the privacy policy." \[NU\_000859] |

| `passive` | Patient as subject; agent deleted or demoted to oblique by-phrase. | "But no, that information is shared with Facebook." \[NU\_000787] |

| `nominalization` | Verbal process encoded as noun; agent and patient both suppressed. | "There's the risk of a malicious data breach." \[NU\_000028] |

| `intransitive` | No patient expressed; event presented as spontaneous occurrence without named agent. | "This happened to fitness tracking app Fitbit, revealing users' locations..." \[NU\_000028] |

| `other` | Descriptive or contextual sentence without a recoverable responsibility frame. | "Founded in 2015, Flo offers users tools to track menstrual cycles..." \[NU\_003132] |



\## Dimension 2: Actor Category



| Value | Definition | Corpus example |

|---|---|---|

| `corporate` | App companies, technology platforms, and tech firms. | "Free apps need to make money and most of them do it by trading our data." \[NU\_000028] |

| `regulatory` | Governments, courts, regulators, police, and legislative bodies. | "Officials holding anti-abortion views have leveraged period-tracking information in the past." \[NU\_000126] |

| `user` | Individual users, women, consumers, and patients positioned as actors. | "She uses the app Period Log but didn't read its privacy policy." \[NU\_000028] |

| `technological\_system` | Algorithms, AI systems, or data infrastructures framed as autonomous agents. | "The Facebook SDK is designed to automatically transmit event data to Facebook." \[NU\_000378] |

| `expert\_civil\_society` | Researchers, NGOs, advocacy organizations, and report authors. | "Consumer Reports did its own security audit of Glow and found several problems." \[NU\_000039] |

| `suppressed` | No grammatical subject present; agent absent due to passivization or nominalization. | "This data is bought, sold, and distributed without the explicit awareness or consent of users." \[NU\_002954] |

| `other` | Residual category for subjects not fitting any of the above. | "In effect, it's a form of the rhythm or calendar method." \[NU\_000283] |



\## Dimension 3: Responsibility Direction



| Value | Definition | Corpus example |

|---|---|---|

| `structural` | Blame or obligation directed toward corporations, institutions, or systemic conditions. | "Glow, another women's health app, separately came under fire and paid a $250,000 settlement..." \[NU\_000125] |

| `individualizing` | Blame or obligation directed toward users, individuals, or personal behavior. | "Ultimately, people who use period-tracking apps should be aware of the risk..." \[NU\_000126] |

| `diffuse` | Responsibility spread across multiple actors or attributed to the system as a whole. | "Goolden's not alone in skipping past the T\&Cs and privacy policies..." \[NU\_000028] |

| `neutral` | No clear direction; descriptive or contextual without directional accountability. | "It's estimated that millions of people in the US use period-tracking apps..." \[NU\_000124] |



\## Dimension 4: Agent Suppressed



Binary dimension (`true`/`false`) identifying sentences where the grammatical

construction obscures or omits the responsible actor. Coded `true` if the

sentence uses a passive construction without an explicit by-phrase, a

nominalization that transforms an agentive process into a noun phrase, or an

intransitive construction presenting an event as self-caused. Coded `false`

if the agent is explicitly named as grammatical subject.



\## Dimension 5: Modal Responsibility Language



Captures explicit normative attribution through deontic modals (\*should\*,

\*must\*, \*need to\*) and evaluative predicates (\*failed to\*, \*refused to\*). High

density directed at corporate actors indicates structural accountability

framing; high density directed at users reflects prescriptive

individualization.



\## Inter-annotator agreement results



| Dimension | n | Po | κ | Interpretation |

|---|---|---|---|---|

| construction\_type | 100 | 0.470 | 0.239 | fair |

| actor\_category | 100 | 0.760 | 0.700 | substantial |

| responsibility\_direction | 100 | 0.770 | 0.591 | moderate |

| agent\_suppressed | 100 | 0.810 | 0.207 | fair |



Full confusion matrices: see thesis Appendix D.

