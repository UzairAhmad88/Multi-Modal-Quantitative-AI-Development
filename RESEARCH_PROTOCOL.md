# Research Protocol

## Central Hypothesis

A multi-modal representation combining market behavior, financial news and company fundamentals may provide more useful predictive information than a market-only baseline.

## Required Ablation Groups

1. Market only
2. Market + News
3. Market + Fundamentals
4. Market + News + Fundamentals

## Controls

- same evaluation periods
- chronological splits
- identical transaction-cost assumptions
- identical benchmark
- documented preprocessing
- fixed seed where applicable
- no test-set model selection

## Required Reporting

For every experiment record:

- hypothesis
- dataset version
- universe
- feature set
- model
- training period
- validation period
- test period
- hyperparameters
- prediction metrics
- trading metrics
- risk metrics
- runtime
- limitations

## Model Selection

Use validation data for model and parameter selection. Keep the final test period untouched until final evaluation.
