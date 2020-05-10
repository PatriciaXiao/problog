0.333333333333333::burglary.
0.2::earthquake.
0.344256265317537::alarm :- burglary, earthquake.
1.0::alarm :- burglary, \+earthquake.
0.0::alarm :- \+burglary, earthquake.
