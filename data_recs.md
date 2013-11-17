Data collection ideas and guidelines for Amnesty International Urgent Alerts network
========================

__Eric Williams and Michael Shvartsman, with recommendations from many others__

This is intended as a companion document to the AI Req for Urgent Action Tracking, to add some more ideas regarding the sorts of data and data-collection behaviors that would be helpful for the sorts of predictive analytics we initially had in mind for this data dive. For example:

* Prediction of the timing and unique nature of an alert's eventual resolution (e.g. for warning activists on the ground).
* Analysis and visualization of alert and update sequence by risk type, issue type, geography etc.
* Evaluating the effectiveness of AI urgent actions (in terms of both member mobilization and eventual effect on the issue at hand).

High-level concepts
--------------------
The basic idea behind all of those is that it is much easier to analyze and process data that is standardized and tagged with analysis in mind. 11,000 documents are too many to manually tag and categorize, but not quite many enough for text mining techniques to be productive at our desired level of accuracy (for predicting real risk on the ground), especially once they are broken out by geography, issue type, and so on.

Dates
------------
Standardizing both date formatting and where dates are included going forward would be incredibly helpful. In particular:

* Including both the date of event and the date of UA issue in the alert's record. If we are attempting to predict risk to an activist on the ground, we would like to predict the time of the event iself (e.g. kidnapping, jailing) rather than the time that the UA comes out, so this information is crucial. On the other hand, if the outcome of interest is the response to the UA itself, then the issue date is what is of interest
* Standard date formatting. There are a number of different standards presently used in the database (2-digit years and 4-digit years, month-first and month-last, and so on). Standardizing those will save time parsing.
* Including each standardly-included type of date in its own field: for example, if issue date and appeal date are included in each UA, they should be in their own field in the database.

Standardized event tagging
--------------------------
For assessment of time-based risk (e.g. survival analysis and hazard functions), standardized tagging of event outcomes would be incredibly helpful. For example, for kidnapping there could be a “kidnapped” event and a “released” event. For “threat of violence”, outcomes could be “threatened” and “threat investigated” or “assaulted” and so on. Then we can predict these outcomes by event type over time and provide timely warnings to activists on the ground.

Separation of issue, risk and outcome category
--------------------------------------------------------------
Presently the categorization system is used for separate types of categories: the category of a risk to an activist (e.g. threats of violence, incarceration etc), issues (e.g. water rights, LGBTI rights), and outcome category (e.g. “torture”). Focus of prediction should drive outcome categorization.  For example, if the interest is the effectiveness of the UA itself to mobilize action, the current status of ‘action’ at each UA needs to be explicitly input (e.g. community response entry). If interest is the outcome of the subject of the UA, then a per-category outcome must be outlined in each UA (e.g. for a ‘risk of imprisonment’ UA, category: “is subject(s) currently imprisoned: yes/no”)

Other useful predictors
-----------------------------
In addition to the key items above, some other ideas came out of discussion with the team. For example:

* Narrower geographic information
* Names, genders and ages of individuals involved in a standard field
* Staff member’s subjective assessment of on-the-ground risk

Rigid tagging guidelines
--------------------------------
Presently the tags are inconsistently applied. For example, the “torture” category can be applied to situations when someone is at risk of torture, is actually tortured, or when the UA is related to another UA where torture is involved. This means that the label “torture” cannot be used as a consistent predictor or consistent outcome. Other tags are ambiguous between outcomes: for example, “execution” can mean either death penalty or an extrajudicial execution.

Standardized and consistent language use
---------------------------------------------------
Related to the above, a consistent template for UAs would do a lot to encourage the above recommendations, as well as make it easier for AI members to find the information they are looking for in the alerts they receive (which are usually fairly long by email standards).

Standard database structure or software
----------------------------------------------------
A standard database (relational or otherwise) will eliminate much of the need to preprocess raw text, and improve speed and quality of access to analytics done on the predetermined fields described above. In addition, standard metadata (e.g. Dublin Core) and API access to document text would greatly facilitate text analysis when it becomes necessary.


