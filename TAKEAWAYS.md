# Takeaways: Do LLMs Drift Toward Non-WEIRD Values in Extended Conversation?

## Motivation

Large language models have been shown to embed psychological profiles that are systematically WEIRD — Western, Educated, Industrialized, Rich, and Democratic (Atari et al., 2023). These default biases reflect the demographics overrepresented in training data and can shape model outputs in culturally narrow ways. This project asks a follow-up question: **can extended interaction with a user who holds non-WEIRD values cause a model to drift away from its WEIRD defaults?**

## Experimental Design

We designed a two-LLM conversation paradigm using GPT-4o (via the OpenAI API):

1. **Baseline measurement.** The bot LLM (GPT-4o) answers 15 survey questions adapted from the World Values Survey (WVS) with no prior conversation context. These questions span authority, obedience, duty, religion, governance, individual rights, security, and sexual norms.

2. **Extended conversation.** The bot LLM engages in a 10-turn back-and-forth conversation with a user LLM (also GPT-4o) that is prompted to consistently embody non-WEIRD cultural values — emphasizing respect for authority, communal duty, conformity, filial obligation, and security over freedom.

3. **Post-interaction measurement.** The same WVS questions are re-administered to the bot LLM, but now with the full conversation history in context.

4. **Drift computation.** For each question, drift = post score - baseline score. We ran 100 independent experiment trials and report mean drift with bootstrapped 95% confidence intervals.

Each WVS dimension is coded with a `higher_is_weird` flag. If the model were systematically absorbing non-WEIRD values from the conversation, we would expect:
- **Negative drift** on `higher_is_weird = True` dimensions (the model moves away from WEIRD-typical high scores).
- **Positive drift** on `higher_is_weird = False` dimensions (the model moves toward non-WEIRD-typical high scores).

## Key Finding

**The results are mixed and do not show a consistent pattern of drift toward non-WEIRD values.**

Several dimensions do show drift in the expected direction:
- **Duty-oriented dimensions** (`duty_care_for_parents`, `duty_have_children`, `duty_work_for_society`) and **democracy_essential_obey_rulers** show substantial positive drift, consistent with the model absorbing communal and obligation-based values.
- **priority_order_vs_free_speech** also drifts positively, suggesting the model shifted toward valuing order over free expression.

However, other dimensions drift in the *opposite* direction:
- **tradeoff_freedom_vs_security** and **state_surveillance_public_areas** show large *negative* drift — the model moved *more* WEIRD (toward freedom and against surveillance) after conversing with the non-WEIRD user.
- **child_quality_obedience** and **governance_strong_leader** also drift negatively, counter to the non-WEIRD direction.

Several dimensions show negligible drift: **religion_importance_god**, **democracy_essential_civil_rights**, and **religion_over_science** remain largely unchanged.

## Interpretation

1. **Sycophancy is selective, not global.** GPT-4o does not uniformly shift toward whatever values the user expresses. The model appears more susceptible to influence on some value dimensions (particularly duty and obligation) than on others (particularly security/surveillance and authority).

2. **Possible safety training resistance.** The dimensions where the model drifted *away* from the non-WEIRD user (surveillance, security over freedom, strong-leader governance) are topics where safety fine-tuning likely instills strong priors. Extended conversation may actually cause the model to *reinforce* its trained defaults on these sensitive topics — a form of "value anchoring" rather than drift.

3. **The WEIRD bias is durable but not monolithic.** Consistent with Atari et al. (2023), the model's baseline is clearly WEIRD-leaning. Our results suggest this bias is structurally embedded and resistant to conversational pressure on most dimensions, though cracks appear in the domain of interpersonal duty and obligation.

4. **Methodological note.** All measurements use structured output parsing with the same model (GPT-4o) acting as both conversation partner and survey respondent. The user LLM's prompting is deliberately strong and persistent; weaker or more subtle non-WEIRD cues would likely produce even less drift.

## References

- Atari, M., Xue, M. J., Park, P. S., Blasi, D. E., & Henrich, J. (2023). *Which Humans?* Preprint. Retrieved from which_humans_09222023.pdf.
- Henrich, J., Heine, S. J., & Norenzayan, A. (2010). The weirdest people in the world? *Behavioral and Brain Sciences*, 33(2-3), 61–83.
- Inglehart, R., Haerpfer, C., Moreno, A., Welzel, C., Kizilova, K., Diez-Medrano, J., Lagos, M., Norris, P., Ponarin, E., & Puranen, B. (Eds.). (2022). *World Values Survey: All Rounds – Country-Pooled Datafile*. JD Systems Institute & WVSA Secretariat. https://www.worldvaluessurvey.org/
