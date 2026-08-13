%DAISY_CHAIN_FIGURE  Total daisy-chain resistance per assembly condition, v1 board.
%
% Standalone. Put this next to daisy_chain_resistance.csv and run it. Writes
% daisy_chain_resistance.(png|pdf) and daisy_chain_resistance_bars.(png|pdf).
%
% Same style as the rest of the electrical figures: Helvetica 9 pt, 8.9 cm column
% width, box on, minor ticks, 600 dpi raster and vector PDF.
%
% Data is a separate experiment on the v1 board, six 1x1 mm^2 Au-coated dummy dies
% per chain, one chain per condition. Not the LED coupons.

clear; close all;
here = fileparts(mfilename("fullpath"));
DC   = readtable(fullfile(here, "daisy_chain_resistance.csv"));

CB = [0.145 0.353 0.706];   % same blue as the V_F figure
FS = 9;  W = 8.9;

set(groot, defaultAxesFontName = "Helvetica", defaultTextFontName = "Helvetica", ...
    defaultAxesFontSize = FS, defaultAxesLineWidth = 0.7, defaultAxesBox = "on", ...
    defaultAxesTickDir = "in", defaultAxesGridAlpha = 0.10, defaultAxesLayer = "top");

% markers, matching the R_s and V_F figures
fig = newfig(W, 6.4);
errorbar(DC.condition, DC.R_total_ohm, DC.R_dev_ohm, "k", ...
         LineStyle = "none", LineWidth = 1.0, CapSize = 4);
plot(DC.condition, DC.R_total_ohm, "s", MarkerSize = 5.2, ...
     MarkerFaceColor = CB, MarkerEdgeColor = "k", LineWidth = 0.7);
xlim([0.4 8.6]); ylim([0.15 0.68]); xticks(1:8); yticks(0.2:0.1:0.6); grid on
xlabel("Assembly condition"); ylabel("Total chain resistance (\Omega)");
save_fig(fig, fullfile(here, "daisy_chain_resistance"));

% bar variant
fig = newfig(W, 6.4);
bar(DC.condition, DC.R_total_ohm, 0.68, FaceColor = CB, ...
    FaceAlpha = 0.75, EdgeColor = "none");
errorbar(DC.condition, DC.R_total_ohm, DC.R_dev_ohm, "k", ...
         LineStyle = "none", LineWidth = 1.0, CapSize = 4);
xlim([0.4 8.6]); ylim([0 0.72]); xticks(1:8); yticks(0:0.2:0.6); grid on
xlabel("Assembly condition"); ylabel("Total chain resistance (\Omega)");
save_fig(fig, fullfile(here, "daisy_chain_resistance_bars"));

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
