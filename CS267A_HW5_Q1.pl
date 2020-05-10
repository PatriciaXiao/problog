% reference:
% https://github.com/ML-KULeuven/problog/blob/master/test/4_bayesian_net.pl
% https://dtai.cs.kuleuven.be/problog/tutorial/basic/02_bayes.html
% https://dtai.cs.kuleuven.be/problog/wasp2017/session4.html %%% especially useful!

person(john).
person(mary).

0.001::burglary.
0.002::earthquake.

0.9::alarm :- burglary, earthquake.
0.8::alarm :- burglary, \+earthquake.
0.1::alarm :- \+burglary, earthquake.

0.8::calls(X) :- alarm, person(X).
0.1::calls(X) :- \+alarm, person(X).

evidence(calls(john),true).
evidence(calls(mary),true).

query(burglary).
query(earthquake).