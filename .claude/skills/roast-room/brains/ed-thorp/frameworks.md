# Frameworks: Edward O. Thorp

Built from 34 public sources (papers 1961 to 2010, Wilmott and Gambling Times columns, interviews 2010 to 2022). 14 frameworks, roughly most-used first. "Sources" counts distinct sources where the idea appears. Names are his where he named them; otherwise a short name marked *(unnamed)*. The How-to-score lines are scoring guidance for the council built from his own thresholds, not quotes.

---

## 1. The Kelly criterion
- **What it is:** Once you have an edge, bet the fraction of current capital that maximizes the expected logarithm of wealth. That maximizes long-run compound growth and never bets everything, so ruin cannot come from one loss.
- **Parts:** For an even-money bet, f* = 2p - 1, which equals your expected gain per unit. For a bet that pays A to 1, f* = edge / A. For a continuous investment, f* is roughly (excess return) / variance. Recompute the bet as capital changes (fixed fraction betting).
- **When to use:** Any question of "how much": position size, leverage, how much of the account a signal gets.
- **How to score:** 5 if the bet is sized from a measured edge and its variance, at or below half of Kelly; 3 if sized by feel but clearly small against the edge; 1 if the size has no link to the edge, or exceeds full Kelly.
- **Quote:** "bet a fraction of your current capital equal to your expectation." (S004)
- **Quote:** "In the one asset two valued payoff case, the optimal Kelly wager is the edge (expected return) divided by the odds." (S031)
- **Sources:** 10 (S001, S004, S005, S013, S022, S024, S028, S031, S033, S025)

## 2. Fractional Kelly (half Kelly)
- **What it is:** Bet a fraction of the Kelly amount, usually half. Half Kelly keeps about three quarters of the growth rate with about half the volatility, and protects you if the edge is smaller than you think.
- **Parts:** Estimate the edge. Assume the true edge is lower than the estimate. Pick f between half and full of the estimated Kelly. Go lower still if interim drawdowns would make you quit.
- **When to use:** Always in markets, where the edge is an estimate, not a calculation.
- **How to score:** Guidance from S004: if the true edge is half the estimate, full Kelly gives zero growth and wild swings, and 1.5 times Kelly gives ruin. Score 5 at half Kelly or less, 3 between half and full, 1 above full.
- **Quote:** "So I generally recommend that people just bet half-kelly, so they won't get scared." (S022)
- **Quote:** "choosing f in the range .5fe∗ ⩽ f < fe∗ offers protection against" (S004)
- **Sources:** 4 (S001, S004, S022, S031)

## 3. Find the edge first, size it second *(unnamed)*
- **What it is:** Two separate problems in strict order. First prove positive expectation. Only then decide the size. No edge means no bet, however good the story.
- **When to use:** Before any discussion of sizing or leverage.
- **How to score:** 5 if the edge is measured, net of costs, out of sample; 3 if measured in sample only; 1 if asserted.
- **Quote:** "The Kelly system calls for no bet unless you have the advantage." (S033)
- **Sources:** 5 (S002, S004, S025, S027, S033)

## 4. Edge defined net *(unnamed)*
- **What it is:** An edge is excess return after adjusting for risk and after all costs. Gross backtest returns are not an edge.
- **Parts:** Subtract commissions, market impact, spreads, taxes, fees. Adjust for risk taken, such as market beta.
- **How to score:** Guidance from S002: stat arb grossed about 50% a year and netted about 26% after commissions and market impact. If costs would eat half or more of the claimed edge, score 2 or less until they are modeled.
- **Quote:** "By “edge,” I mean excess return after adjusting for risk, net of costs." (S025)
- **Quote:** "Commissions and market impact costs reduced this to about 26%." (S002)
- **Sources:** 4 (S002, S016, S025, S006)

## 5. The devil's advocate test *(unnamed)*
- **What it is:** A claimed edge must be logically demonstrable: you can explain why it exists and defend it against a hostile critic. A pattern without a reason is suspect.
- **When to use:** Any signal from a backtest, a manager's record, or a tip.
- **How to score:** 5 if there is a causal reason the edge exists and the data agree; 3 if the data are strong but the reason is weak; 1 if neither.
- **Quote:** "If you think you have an edge, it needs to be logically demonstrable. You’ve got to be able to defend it against a good devil’s advocate." (S025)
- **Sources:** 3 (S025, S007, S029)

## 6. Regression of estimated edges *(unnamed)*
- **What it is:** Estimated edges are biased high. Expect the live edge to come in below the backtest because of data mining, non-stationary markets, rule changes, and capital crowding in.
- **Parts:** Data mining; regression to the mean; regime and rule changes; crowding.
- **How to score:** Guidance: haircut a backtested edge by at least half before sizing, more if many variants were tried.
- **Quote:** "To the extent me is an uncertain estimate of mt , it is wise to assume mt < me and" (S004)
- **Quote:** "Systems that do work attract capital," (S004)
- **Sources:** 4 (S004, S002, S025, S029)

## 7. The Heraclitus principle
- **What it is:** Markets give you one history. You cannot replay them a million times as you can a card game, so every number is an estimate with error bars.
- **Quote:** "Unlike blackjack and gambling games, you only have one history from which to use" (S002)
- **Quote:** "It’s much more difficult in the securities markets because we just have one history from which we have to infer what’s going on, and the probabilities that we have are not exact" (S025)
- **Sources:** 3 (S002, S025, S027)

## 8. Overbetting causes the disasters *(unnamed)*
- **What it is:** Betting more than Kelly lowers growth and raises risk at once. Consistent overbetting leads to ruin. He reads 1929, 1987, LTCM and 2008 as leverage disasters.
- **How to score:** 1 if the plan uses leverage sized from a calm-period backtest; 5 if leverage is capped well below the Kelly figure because prices jump.
- **Quote:** "And the Kelly criteria when you work through the theory shows you that if you bet too much consistently, you will be ruined eventually." (S022)
- **Quote:** "Hence it never pays to bet more than the Kelly strategy because then risk increases (lower security) and growth decreases" (S031)
- **Sources:** 5 (S002, S004, S022, S031, S001)

## 9. Local risk versus global risk
- **What it is:** Hedge normal fluctuations; separately cap exposure to sudden jumps. Ask extreme what-if questions. Do not trust historical limits or normal tails.
- **Parts:** Two questions for any investment: factor exposures, and extreme-event risk.
- **How to score:** 5 if the plan survives a move twice the worst day on record; 1 if the worst case is taken from the backtest.
- **Quote:** "Our rule was to limit global risk to acceptable levels, while" (S002)
- **Quote:** "What are the factor exposures”, and “What are the risks from extreme events?”." (S002)
- **Sources:** 2 (S002, S004)

## 10. Three steps of a market-beating model
- **What it is:** Idea, development into a testable model, then real-world verification with real money. Skills: visionary, quantitative, entrepreneurial.
- **Quote:** "To recap, the three steps for a successful market-beating model are (1) idea, (2) development," (S002)
- **Sources:** 3 (S002, S010, S025)

## 11. Index by default (burden of proof on active) *(unnamed)*
- **What it is:** Anyone who cannot demonstrate an edge should hold a low-cost index fund. Active investing in aggregate is the index minus costs.
- **Quote:** "People should be putting money into index funds when they can’t demonstrate that an investment with similar characteristics is better." (S025)
- **Quote:** "I would say that the burden of proof is on the non-index manager." (S025)
- **Sources:** 5 (S006, S007, S025, S027, S029)

## 12. Edges decay *(unnamed)*
- **What it is:** Once found, an edge draws money that prices it away. Stat arb lost power as Morgan Stanley and others piled in. Keep researching.
- **Quote:** "Also, when an edge is discovered, the money that’s poured into it makes the edge go away, because it moves prices toward correct pricing." (S025)
- **Quote:** "Then it began to lose some of its power as Morgan Stanley and others spread the idea and also put more money into it." (S029)
- **Sources:** 4 (S002, S025, S029, S020)

## 13. Diversification across many small bets *(unnamed)*
- **What it is:** Splitting an edge across many independent bets raises the safe bet size and growth rate. Hundreds of positions and a million bets turn skill into a reliable result.
- **Quote:** "Such is the power of diversification." (S033)
- **Quote:** "As I have a collection of them, the deviations between my discrete adjustments and continuous adjustment are like a diversified pool of random noise." (S026)
- **Sources:** 4 (S002, S004, S026, S033)

## 14. Volatility drag and the Mr. Market coin flip
- **What it is:** Compound growth is below average return because of fluctuations (arithmetic about 12.5%, geometric about 10.5% for stocks). Each day is a coin flip with a small drift in your favor.
- **Quote:** "The historical geometric growth is about 10.5%, because of the fluctuations." (S027)
- **Sources:** 2 (S027, S023)
