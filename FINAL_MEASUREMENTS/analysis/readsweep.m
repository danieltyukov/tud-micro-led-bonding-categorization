function S = readsweep(f)
%READSWEEP Read one iv_sweep CSV. Returns struct with i (A) and v (V).
lines = readlines(f);
keep  = ~startsWith(lines, "#") & ~startsWith(lines, "level") & strlength(strip(lines)) > 0;
M     = str2double(split(lines(keep), ","));
S.level = M(:,1);
S.i     = M(:,2) / 1000;
S.v     = M(:,3);
S.vgnd  = M(:,7);
S.vcc   = M(:,8);
end
