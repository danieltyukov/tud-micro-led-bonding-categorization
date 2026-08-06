%FIGURES Electrical characterization figures, rounds 1 and 2.
% R1 = DMM screening (RESULTS/R1_*.csv). R2 = Arduino I-V sweeps (data/R2_sweeps).
clear; close all;
here    = fileparts(mfilename("fullpath"));
datadir = fullfile(here, "..", "data", "R2_sweeps");
r1dir   = fullfile(here, "..", "..", "RESULTS");
outdir  = fullfile(here, "figures");
if ~exist(outdir, "dir"), mkdir(outdir); end

CR = [0.792 0.094 0.114];  CG = [0.106 0.510 0.271];  CB = [0.145 0.353 0.706];
CK = [0.30 0.30 0.30];     CA = [0.902 0.545 0.090];
FS = 9;  LW = 1.3;  W = 8.9;
MODES = ["pass" "suspect" "cross_lit" "open" "short" "die_detached"];
MCOL  = [0.80 0.86 0.80; 1.00 0.85 0.40; CA; CR; 0.45 0.05 0.08; 0.72 0.72 0.72];

set(groot, defaultAxesFontName = "Helvetica", defaultTextFontName = "Helvetica", ...
    defaultAxesFontSize = FS, defaultAxesLineWidth = 0.7, defaultAxesBox = "on", ...
    defaultAxesTickDir = "in", defaultAxesGridAlpha = 0.10, defaultAxesLayer = "top");

T  = collect(datadir);  writetable(T, fullfile(here, "fit_results.csv"));
R  = T(T.colour == "R" & T.physical, :);
C1 = readtable(fullfile(r1dir, "R1_channels.csv"), TextType = "string");
C1 = C1(startsWith(C1.die, "D") & ~startsWith(C1.die, "DC"), :);       % addressable dice only

N = zeros(8, numel(MODES));
for s = 1:8
    for m = 1:numel(MODES), N(s,m) = sum(C1.sample == s & C1.verdict == MODES(m)); end
end
tot = sum(N, 2);  ok = N(:,1);
[lo, hi] = wilson(ok, tot);

%% Fig 1 - representative I-V, one die, three colours
fig = newfig(W, 6.4);
for c = ["R" "G" "B"]
    S = readsweep(fullfile(datadir, sprintf("s1_D1_%s_seat1.csv", c)));
    col = CR*(c=="R") + CG*(c=="G") + CB*(c=="B");
    plot(S.i*1000, S.v, "o-", Color = col, MarkerSize = 2.4, MarkerFaceColor = col, LineWidth = LW);
end
logx([0.3 20]); ylim([1.6 3.05]); grid on
xlabel("Forward current (mA)"); ylabel("Junction voltage {\itV}_{die} (V)");
legend(["Red" "Green" "Blue"], Location = "southeast", Box = "off");
save_fig(fig, fullfile(outdir, "fig1_iv_curves"));

%% Fig 2 - channel defect map from the round 1 screening
G = zeros(24, 8);
for k = 1:height(C1)
    d = str2double(extractAfter(C1.die(k), "D"));
    c = find(["R" "G" "B"] == C1.channel(k));
    m = find(MODES == C1.verdict(k));
    if ~isempty(c) && ~isempty(m) && ~isnan(d), G((C1.sample(k)-1)*3 + c, d) = m; end
end
fig = newfig(W, 7.6);
imagesc(G, [0 6]); colormap(gca, [1 1 1; MCOL]);
set(gca, YDir = "reverse", XTick = 1:8, XTickLabel = "D"+string(1:8), ...
    YTick = 2:3:24, YTickLabel = "S"+string(1:8), TickLength = [0 0], ...
    XMinorTick = "off", YMinorTick = "off");
for y = 3.5:3:21.5, yline(y, "-", Color = "w", LineWidth = 1.6); end
xlabel("Die position"); ylabel("Assembly condition");
h = gobjects(1,6);
for k = 1:6, h(k) = patch(NaN, NaN, MCOL(k,:), EdgeColor = [.5 .5 .5]); end
legend(h, ["pass" "suspect" "cross-lit" "open" "short" "detached"], ...
       Location = "southoutside", Box = "off", NumColumns = 3, FontSize = FS-1.5);
set(gca, Position = [0.155 0.29 0.815 0.67]);
save_fig(fig, fullfile(outdir, "fig2_defect_map"));

%% Fig 3 - yield and failure mode by condition. The process comparison.
fig = newfig(W, 6.8);
b = bar(1:8, 100*N./tot, 0.68, "stacked", EdgeColor = "none");
for k = 1:6, b(k).FaceColor = MCOL(k,:); end
errorbar(1:8, 100*ok./tot, 100*ok./tot - lo, hi - 100*ok./tot, "k", ...
         LineStyle = "none", LineWidth = 1.0, CapSize = 4);
ylim([0 118]); xticks(1:8); yticks(0:25:100); grid on
xlabel("Assembly condition"); ylabel("Channels (%)");
text(1:8, 112*ones(1,8), string(ok)+"/"+string(tot), FontSize = FS-2.2, ...
     HorizontalAlignment = "center");
legend(b, ["pass" "suspect" "cross-lit" "open" "short" "detached"], ...
       Location = "southoutside", Box = "off", NumColumns = 3, FontSize = FS-1.5);
set(gca, Position = [0.155 0.30 0.815 0.62]);
save_fig(fig, fullfile(outdir, "fig3_yield_modes"));

%% Fig 4 - R_s per condition against the re-seating floor
seatsd = 0.843;  gm = mean(R.Rs);
fig = newfig(W, 6.4);
patch([0.4 8.6 8.6 0.4], gm + [-1 -1 1 1]*seatsd, CA, FaceAlpha = 0.13, EdgeColor = "none");
yline(gm, "-", Color = [.55 .55 .55], LineWidth = 0.8);
for s = 1:8
    v = R.Rs(R.sample == s);
    if isempty(v), continue; end
    plot(s + (rand(size(v))-0.5)*0.24, v, "o", MarkerSize = 3.2, ...
         MarkerFaceColor = CR, MarkerEdgeColor = "none");
    if numel(v) > 1, errorbar(s, mean(v), std(v), "k", LineWidth = 1.0, CapSize = 4); end
    plot(s, mean(v), "s", MarkerSize = 5.2, MarkerFaceColor = "k", MarkerEdgeColor = "k");
end
xlim([0.4 8.6]); ylim([9.4 13.9]); xticks(1:8); grid on
xlabel("Assembly condition"); ylabel("{\itR}_s, red channel (\Omega)");
text(0.62, gm + seatsd*0.70, "\pm1\sigma re-seating", FontSize = FS-1.5, Color = CA*0.72);
save_fig(fig, fullfile(outdir, "fig4_rs_by_condition"));

%% Fig 5 - re-seating repeatability sets that floor
chans = ["s7_D1_R" "s7_D3_R" "s8_D6_R"];  cols = [CR; CB; CG];
fig = newfig(W, 5.9);
for k = 1:numel(chans)
    v = zeros(1,3);
    for s = 1:3
        S = readsweep(fullfile(datadir, sprintf("%s_seat%d.csv", chans(k), s)));
        v(s) = fitdiode(S.i, S.v);
    end
    plot(1:3, v, "o-", Color = cols(k,:), LineWidth = LW, MarkerSize = 4.2, MarkerFaceColor = "w");
end
xlim([0.85 3.15]); ylim([10 12.7]); xticks(1:3); grid on
xlabel("Independent re-seating of the same two jumpers"); ylabel("{\itR}_s (\Omega)");
legend(["S7 D1" "S7 D3" "S8 D6"], Location = "northwest", Box = "off", NumColumns = 3);
save_fig(fig, fullfile(outdir, "fig5_reseat_repeatability"));

%% Fig 6 - forward voltage at 10 mA by condition
fig = newfig(W, 6.4);
for s = 1:8
    v = R.vf10(R.sample == s);
    if isempty(v), continue; end
    plot(s + (rand(size(v))-0.5)*0.24, v, "o", MarkerSize = 3.2, ...
         MarkerFaceColor = CB, MarkerEdgeColor = "none");
    if numel(v) > 1, errorbar(s, mean(v), std(v), "k", LineWidth = 1.0, CapSize = 4); end
    plot(s, mean(v), "s", MarkerSize = 5.2, MarkerFaceColor = "k", MarkerEdgeColor = "k");
end
xlim([0.4 8.6]); xticks(1:8); grid on
xlabel("Assembly condition"); ylabel("{\itV}_F at 10 mA, red (V)");
save_fig(fig, fullfile(outdir, "fig6_vf_by_condition"));

%% Fig 7 - shunt the sweep found and the diode test missed
fig = newfig(W, 6.4);
A = readsweep(fullfile(datadir, "s3_D1_R_seat1.csv"));
B = readsweep(fullfile(datadir, "s1_D1_R_seat1.csv"));
plot(B.i*1000, B.v, "o-", Color = CK, MarkerSize = 2.4, MarkerFaceColor = CK, LineWidth = LW);
plot(A.i*1000, A.v, "o-", Color = CR, MarkerSize = 2.4, MarkerFaceColor = CR, LineWidth = LW);
logx([0.3 20]); ylim([1.05 2.25]); grid on
xlabel("Forward current (mA)"); ylabel("{\itV}_{die} (V)");
legend(["Healthy die (S1 D1)" "Contaminated die (S3 D1)"], Location = "southeast", Box = "off");
text(0.62, 1.46, "~2.9 k\Omega shunt", FontSize = FS-1.5, Color = CR);
text(0.62, 1.36, "across the junction", FontSize = FS-1.5, Color = CR);
save_fig(fig, fullfile(outdir, "fig7_shunt_detection"));

%% Fig 8 - self-heating versus current-on time
os = [64 256 1024];  ont = [5.0 20.0 79.9];  rs = zeros(1,3);  se = zeros(1,3);
for k = 1:3
    S = readsweep(fullfile(datadir, sprintf("heat_os%d_D1_R.csv", os(k))));
    [rs(k), ~, ~, se(k)] = fitdiode(S.i, S.v);
end
fig = newfig(W, 5.8);
errorbar(ont, rs, se, "o-", Color = CR, LineWidth = LW, MarkerSize = 4.6, ...
         MarkerFaceColor = CR, CapSize = 4);
logx([3.5 130]); ylim([8 10.6]); xticks([5 20 80]); xticklabels(["5" "20" "80"]); grid on
xlabel("Current-on time per point (ms)"); ylabel("Extracted {\itR}_s (\Omega)");
save_fig(fig, fullfile(outdir, "fig8_self_heating"));

%% numbers quoted in the text
fprintf("\n--- yield, addressable channels ---\n");
for s = 1:8
    fprintf("S%d %2d/%2d = %5.1f%%  [%4.1f %5.1f]  modes:", s, ok(s), tot(s), ...
            100*ok(s)/tot(s), lo(s), hi(s));
    for m = 2:6, if N(s,m) > 0, fprintf(" %s=%d", MODES(m), N(s,m)); end, end
    fprintf("\n");
end
p = chi2yield(N(:,1), tot);
fprintf("chi-square on yield across the 8 conditions: p = %.2g\n", p);
[pRs, tblRs] = anova1(R.Rs, R.sample, "off");
[pVf, tblVf] = anova1(R.vf10, R.sample, "off");
fprintf("ANOVA R_s   : F = %.2f, p = %.3f\n", tblRs{2,5}, pRs);
fprintf("ANOVA V_F   : F = %.2f, p = %.3f\n", tblVf{2,5}, pVf);
fprintf("R_s  mean %.3f sd %.3f  (N=%d), re-seating sd %.3f\n", ...
        mean(R.Rs), std(R.Rs), height(R), seatsd);
fprintf("V_F  mean %.4f sd %.4f V\n", mean(R.vf10), std(R.vf10));
fprintf("smallest resolvable dR_s at n=4: %.2f ohm\n", 2.4*seatsd*sqrt(2/4));

function [lo, hi] = wilson(k, n)
z = 1.96; p = k./n; d = 1 + z^2./n;
c = (p + z^2./(2*n)) ./ d;
h = z*sqrt(p.*(1-p)./n + z^2./(4*n.^2)) ./ d;
lo = 100*max(0, c-h); hi = 100*min(1, c+h);
end

function p = chi2yield(ok, tot)
obs = [ok, tot-ok];
exp_ = sum(obs,2) * sum(obs,1) / sum(obs(:));
X2 = sum((obs-exp_).^2 ./ max(exp_, eps), "all");
p = 1 - chi2cdf(X2, numel(ok)-1);
end

function logx(lims)
set(gca, XScale = "log"); xlim(lims);
xticks([0.5 1 2 5 10 20 50 100]); xticklabels(["0.5" "1" "2" "5" "10" "20" "50" "100"]);
end

function fig = newfig(wcm, hcm)
fig = figure(Units = "centimeters", Position = [2 2 wcm hcm], Color = "w");
ax = axes(fig); hold(ax, "on"); box(ax, "on");
set(ax, Units = "normalized", Position = [0.155 0.175 0.815 0.795], ...
    XMinorTick = "on", YMinorTick = "on");
end

function save_fig(fig, base)
exportgraphics(fig, base + ".png", Resolution = 600);
exportgraphics(fig, base + ".pdf", ContentType = "vector");
end
