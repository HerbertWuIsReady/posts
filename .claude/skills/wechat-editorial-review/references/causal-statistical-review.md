# Causal and statistical review

Use this reference for growth, retention, experiments, holdouts, targeting, ROI, forecasting, or statements that one intervention produced an outcome.

## Start with the estimand

Require the article to name, at least conceptually:

- population;
- treatment or intervention;
- comparison condition;
- outcome and observation window;
- unit of assignment;
- effect being claimed.

If these are unclear, the reported number cannot carry a causal conclusion.

## Common failure modes

### Significance by sample size

“Thousands per cell” does not guarantee statistical significance. Power depends on baseline rate, expected effect size, variance, assignment ratio, multiple comparisons, attrition, and dependence between observations. Replace certainty with a power-analysis requirement unless those inputs are known.

### Control equals natural behavior

A control-group outcome estimates the counterfactual only under conditions such as credible assignment, comparable measurement, limited contamination, and acceptable non-compliance. “Control retention equals natural retention” is too strong without those conditions.

### Fixed holdout percentages

Ten or twenty percent is not a universal standard. The allocation should follow the decision cost, minimum detectable effect, expected variance, ethical constraints, and required power.

### Segmentation after treatment

Do not segment on variables affected by the intervention and then interpret the segment effect causally. Preserve the assignment logic and use pre-treatment state for stratification.

### Network interference

In social, marketplace, creator, and supply-chain systems, one unit's treatment may affect another unit. Individual randomization can understate or misstate the effect. Consider cluster, geographic, room-level, creator-level, or time-based assignment.

### No individual holdout does not mean no evaluation

Platform-wide or infrequent changes may still support phased rollout, switchback tests, matched markets, regression discontinuity, interrupted time series, synthetic controls, or other quasi-experimental designs. Describe their limitations rather than claiming evaluation is impossible.

### Predictive score presented as diagnosis

A risk score can prioritize attention without identifying the reason or the effective action. Require evidence connecting features to the diagnosis and the diagnosis to an intervention.

### Cost approaching zero

Automation can reduce marginal decision cost while leaving data quality, compute, monitoring, model drift, false positives, exception handling, and governance costs. Specify which cost falls and which remain.

## Numbers and formulas

Check every threshold, half-life, sample size, time window, lift, and ROI value. The article should either:

- source and define it;
- explain how it would be estimated;
- or label it unmistakably as an illustrative number.

For ROI or incremental profit, distinguish observed revenue from incremental revenue. Include treatment cost, diagnosis cost, execution cost, infrastructure cost, and adverse effects when material.

## Minimum repair language

Prefer conditional language that stays useful:

- “是否跑得出显著结果，需要根据基准率和预期效应量做功效分析。”
- “随机留出的对照组可用于估计未干预时的结果，前提是分组和测量条件成立。”
- “这个阈值是示意，实际应根据历史留存曲线标定。”
- “边际诊断成本下降，不等于系统总成本归零。”

Do not bury a fatal methodological caveat in the final section if earlier sections repeatedly rely on the stronger claim.
