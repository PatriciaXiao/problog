%%% The program:
t(0.5)::burglary.
0.2::earthquake.

t(_)::alarm :- burglary, earthquake.
t(_)::alarm :- burglary, \+earthquake.
t(_)::alarm :- \+burglary, earthquake.

