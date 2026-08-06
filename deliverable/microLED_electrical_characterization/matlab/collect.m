function T = collect(datadir)
%COLLECT Fit every seat1 sweep and return one table row per channel.
f = dir(fullfile(datadir, 's*_D*_seat1.csv'));
sample = []; die = strings(0); colour = strings(0);
Rs = []; nid = []; V0 = []; seRs = []; vf10 = []; imax = []; res = [];
for k = 1:numel(f)
    parts = split(string(erase(f(k).name, ".csv")), "_");
    S = readsweep(fullfile(f(k).folder, f(k).name));
    if max(S.i) < 1e-3, continue; end                    % open channel, nothing to fit
    [r, nn, v0, se, rr] = fitdiode(S.i, S.v);
    sample(end+1,1) = str2double(extractAfter(parts(1), "s"));               %#ok<AGROW>
    die(end+1,1)    = parts(2);                                          %#ok<AGROW>
    colour(end+1,1) = parts(3);                                          %#ok<AGROW>
    Rs(end+1,1) = r;  nid(end+1,1) = nn;  V0(end+1,1) = v0;              %#ok<AGROW>
    seRs(end+1,1) = se;  res(end+1,1) = std(rr);                         %#ok<AGROW>
    imax(end+1,1) = max(S.i)*1000;                                       %#ok<AGROW>
    vf10(end+1,1) = interp1(S.i, S.v, min(10e-3, max(S.i)), "linear");   %#ok<AGROW>
end
T = table(sample, die, colour, Rs, nid, V0, seRs, res, vf10, imax);
T.physical = T.nid >= 1.2 & T.nid <= 2.4 & T.Rs > 0;
end
