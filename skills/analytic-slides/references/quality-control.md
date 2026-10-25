# Quality control

Mandatory (scientific integrity, separate from style preferences):
1. Synthetic or placeholder geometry/values are labeled in the footer AND by a status chip.
2. Observed data, analytical constructs and official features are distinguishable.
3. Every claim has its caveat or "Not" line; uncertainty is shown or stated.
4. Data source, vintage and basemap are in the footer.

Five audience tests (human, before presenting):

| Test | Question |
|---|---|
| 10-second comprehension | Can the intended audience state the main message quickly? |
| Visual hierarchy | Does the eye meet the most important evidence first? |
| Geographic interpretation | Can a viewer say where this happens (inset/labels if not)? |
| Scientific integrity | Are data, assumptions, boundaries and uncertainty represented accurately? |
| Readability | Can symbols and text be read at the intended display size (view the PNG at 50%)? |

The builder prints `[qa]` lines for what it can automate (missing "Not" line, synthetic content not disclosed, long title) plus the style guidance for the brief. It does not judge the five tests above.
