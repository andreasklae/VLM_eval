The output of this should be a jupytr notbook using pandas, matplot, numpy and/or similar libraries. Use python as language

Split by difficulty

split by image category (note that same image can have 1 or more categories)


Split by gps/without gps

Score should be averaged per image per approach, but split by location and entities. 

Think of the best way to calculate score from correctness and specificity (and importance for entities).

For location photographer_position (or both), just pick the 1 most correct score. It should not be punished for making a more generalizable claim when it got the correct specific one. It should be punished for wrong claims though. and depicted subject can be multiple. Averege out depicted subjects, and pick one for photographer postion. Note that an evaluation can be mark it as both.

For entities, do the same for each entity. per entity a claim is connected to, pick the 1 claim that is most correct. When calculating scores (and precision etc.) include incorrect claims. It is just that for correct claims that are linked to the same GT entity, pick the 1 that is most correct given the confidence threshold.

Find the perfect confidence threshold for score for each approach for both location and entities. Make a graph for this, on line per approach
Precision, Recall, F1 etc. and PR curves. Both for location and entities and both combined. filter by different levels of specificity and correctness

Look at relevant correlations.

Look at notes (both from json @testing/Image_search/Evaluation/human_evaluation.json and @testing/Image_search/Evaluation/qualitative_analysis_v3.md) for qualitative analysis.

Disregard items with N/A or Scene tags

Bonus tag should count for Score average, but not for TP/FP/TN/FN

Look at bonus tags for qualitative analysis.

For scores and Precission/recall, disregard the type of location claim (depicted subject/photographer position/both), but make a separate analysis of this.

Think of how to handle the fact that GCV is fundamentally different from the other approaches.

Look at description score as well. 

Look at processing time for each approach

Analyze wrong claims (look location and entities both seperately and together). Look at how wrong they are (scores) and also do some filtering based on confidence, specificity and correctness score. 

Note that some N/A are correct, but just irrelevant or location claims, so they should not be counted either positive nor negative. Disregard all N/As.

Analyze performance between fast and strong modes. See how much better a strong mode performs and compare it to how much processing time it uses. 

Look at entities by category. Maybe some models are better than others at certain categories. Do both by score and by precision and recall / f1 score with correctness 1 and specificity >= max specificity and max specificity -1

Do correlation of confidence and correctness per approach

Analyze how important GPS is by the different image categories

Should do an anlysis of landmarks only for entities, this is the most important category.

Do a per image analysis. There are over 200 images sp find a good and creative way of displaying this. Maybe Color code each approach and visualize in a way where you can see the best performers by which colors appear the most based on scores.

Each entity in GT has an importance tag (High, medium or low). Make analysis of this too. 

It is better to be slightly underspecific and correct than specific and -.5 wrong. however, Very underspecific to the point of what an ignorant person can reason to anyways is not really valuable

Put more importance on with GPS. In a real case scenario, the user knows where they are (at least parent region) and is willing to tell the AI or turn on gps for the app. 

For analysis of the finished notbook, Recall should be more important than precission. In a real world scenario, A user doesnt care about FPs, They would care that the AI model recognizes what theyre curious about.

For art category, specificity for Location claims are more strict. for full score, it must correctly guess the gallery/exhibition/room,. correct museum or city will get 4/5

For later analysis, description score is not that important, as this can be adapted with fine tuning and prompt engineering

Actually, remembering what i said about picking one for location claim. We also need to take confidence into account. What should we do here?

Lack of location claims should be 0 in score. Also 0 in score should be considered as no claim made (or to generic/unspecific to be counted as a claim)

Compare Strong and Fast versions of each models

Location claims are less important for runs with gps

Analyze important entity misses (FN) per model. This means where importance is high and it should have >= max spec and one with >= max spec -1. and 1 as correctness. Look at different difficulty levels for this as well. Not individually, but count them. Maybe a bar chart or something else interesting.

Reflect on what to do if a wrong claim has higher confidence than a correct one. 

Use P value for everything

Keep colorcoding consistent

Perform statistical anlysis tests

For depicted subject location claims, you should add them up (or use another statistical mathematical operation). The point is to not punish it if it gets more but less specific claims correct. Average would punish it if it just makes a more general claim while getting the specifics right. Then again, Same claim with different name should not count twice... 

Do a threshold vs. Score graphs for both location and entities

Take all the entities in ground truth (some images was skipped, do not oinclude these), and the highest score (it can make several claims for the same, chose the best one) for each model for each entity (A FN counts as 0) and then average them out. It will be something like "What is the averege best score for each entity for each model?". Also fo this in a way where it takes false negatives into account in some way. 

Do an anlysis of bonus points in a way you find fitting

Note that "Max spec" is just the maximum we expect from the models to get correct. It should get full pot for that specificity. But, if max spec is less than 5, then it should be possible for models to get full pot and some extra points for going above max spec. Which means, it get extra points if it goes over. But, for counting as a TP, it only has to reach the max spec (or -1 if I specifically allow it, which i do in some cases above). 

For scoring, if there are several claims to the same GT entity, pick only the one with the highest score

For location, pick the one with the highest confidence. Also do an analysis of how specific it can be before being wrong. If there are several correct claims with the same confidence, pick the most specific ones. If there are several claims with same confidence, but some are correct and some are not, average them out. If you think this is wrong or have a better solution, let me know.

In general, focus more on entity claims than location claims.

If an entity claim is linked to multiple entities, then the score should coune once per link (so double the score if its linked toi 2, triple if 3 etc.)

When seing correlation between GPS on/off, do it overall, and individually per model. When doing it overall, remember that you eed to take into account that different models perform differently. 

Highlight performances that stand out in any way

Look at weird angles, obstructions etc. from Evaluator Notes and photographer notes. See if some models are better than others at this. Need to do some statistical signficance analysis of this, is the difference larger in these tricky scenarios than easy normal photos. If a model is better in tricky scenarios isnt really meaningful if its better in all scenarios anyways.

In terms of precission/recall etc. +.5 or 0 in correctness should not be considered FP nor FN. Just lack of claim.

As image 194 as a reference, You can see that the models are pretty good at recognizing the exact room, but not the exact painting. But I was able to find the painting by a simple google search, I think I could strengthen the models by giving them access to web search as well.