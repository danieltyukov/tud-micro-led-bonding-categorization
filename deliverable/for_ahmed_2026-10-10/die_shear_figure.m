clear; close all;
here   = fileparts(mfilename("fullpath"));
outdir = fullfile(here, "figures");
if ~exist(outdir, "dir"), mkdir(outdir); end
DS = readtable(fullfile(here, "die_shear_strength.csv"));

CB = [0.145 0.353 0.706];   % same blue as the daisy chain figure
FS = 9;  W = 8.9;

set(groot, defaultAxesFontName = "Helvetica", defaultTextFontName = "Helvetica", ...
    defaultAxesFontSize = FS, defaultAxesLineWidth = 0.7, defaultAxesBox = "on", ...
    defaultAxesTickDir = "in", defaultAxesGridAlpha = 0.10, defaultAxesLayer = "top");

% bars, matching daisy_chain_resistance_bars
fig = newfig(W, 6.4);
bar(DS.condition, DS.shear_MPa, 0.68, FaceColor = CB, ...
    FaceAlpha = 0.75, EdgeColor = "none");
errorbar(DS.condition, DS.shear_MPa, DS.shear_dev_MPa, "k", ...
         LineStyle = "none", LineWidth = 1.0, CapSize = 4);
xlim([0.4 8.6]); ylim([0 60]); xticks(1:8); yticks(0:10:50); grid on
xlabel("Assembly condition"); ylabel("Die shear strength (MPa)");
save_fig(fig, fullfile(outdir, "die_shear_strength_bars"));

% marker variant, matching daisy_chain_resistance
fig = newfig(W, 6.4);
errorbar(DS.condition, DS.shear_MPa, DS.shear_dev_MPa, "k", ...
         LineStyle = "none", LineWidth = 1.0, CapSize = 4);
plot(DS.condition, DS.shear_MPa, "s", MarkerSize = 5.2, ...
     MarkerFaceColor = CB, MarkerEdgeColor = "k", LineWidth = 0.7);
xlim([0.4 8.6]); ylim([8 52]); xticks(1:8); yticks(10:10:50); grid on
xlabel("Assembly condition"); ylabel("Die shear strength (MPa)");
save_fig(fig, fullfile(outdir, "die_shear_strength"));

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
