% reference:
% https://github.com/ML-KULeuven/problog/blob/master/test/4_bayesian_net.pl

% helper
do_list(N, L):- 
    findall(Num, between(1, N, Num), L).

member_classic(X, [X|Xs]).
member_classic(X, [Y|Ys]) :-
    member_classic(X, Ys).

append([], X, X).
append([X | Y], Z, [X | W]) :- append( Y, Z, W).

0.5::heads(C, N) :- coin(C, N).

coin(C, N) :- do_list(N, List), member_classic(C, List).

% M consecutives in N flips
consecutive(M,N) :- do_list(N, List), consecutive(List,N,M,0). % all possible flips


% check if the list has a sublist of true that is length M
consecutive(_,_,M,Len) :- Len >= M.
consecutive([Hd|Tl],N,M,Len) :- 
    heads(Hd,N),
    IncLen is Len + 1,
    consecutive(Tl, N, M, IncLen).
consecutive([Hd|Tl],N,M,Len) :- 
    \+heads(Hd,N),
    consecutive(Tl, N, M, 0).

%%% Queries
query(consecutive(2, 5)).



%someHeads :- heads(_, 2).
%query(someHeads).