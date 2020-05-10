% reference:
% https://github.com/ML-KULeuven/problog/blob/master/test/4_bayesian_net.pl

0.7::burglary.
0.2::earthquake.
0.9::p_alarm1.
0.8::p_alarm2.
0.1::p_alarm3.

alarm :- burglary, earthquake, p_alarm1.
alarm :- burglary, \+earthquake, p_alarm2.
alarm :- \+burglary, earthquake, p_alarm3.


%%% Evidence
evidence(alarm,true).

%%% Queries
query(burglary).
query(earthquake).
