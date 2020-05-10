% reference:
% https://github.com/ML-KULeuven/problog/blob/master/test/4_bayesian_net.pl
% https://dtai.cs.kuleuven.be/problog/tutorial/basic/02_bayes.html
% https://dtai.cs.kuleuven.be/problog/wasp2017/session4.html %%% especially useful!
% problog lfi myprogram.pl myexamples.pl -O mylearnedprogram.pl

%%% The program:
t(0.5)::burglary.
0.2::earthquake.
t(_)::p_alarm1.
t(_)::p_alarm2.
t(_)::p_alarm3.

alarm :- burglary, earthquake, p_alarm1.
alarm :- burglary, \+earthquake, p_alarm2.
alarm :- \+burglary, earthquake, p_alarm3.

