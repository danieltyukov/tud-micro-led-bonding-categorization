function [Rs, n, V0, seRs, resid] = fitdiode(i, v, imin)
%FITDIODE Least-squares fit of V = V0 + n*VT*ln(I) + I*Rs. Linear in all three.
if nargin < 3, imin = 0.5e-3; end
VT = 25.85e-3;
k  = i > imin;
X  = [ones(sum(k),1), log(i(k)), i(k)];
y  = v(k);
p  = X \ y;
V0 = p(1);
n  = p(2) / VT;
Rs = p(3);
resid = y - X*p;
s2    = sum(resid.^2) / (numel(y) - 3);
Cov   = s2 * inv(X'*X);                                                     %#ok<MINV>
seRs  = sqrt(Cov(3,3));
end
