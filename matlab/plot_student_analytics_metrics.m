function plot_student_analytics_metrics(outputDir)
%PLOT_STUDENT_ANALYTICS_METRICS Plot synthetic student analytics outputs.
%   plot_student_analytics_metrics('outputs') reads generated CSV files and
%   creates simple MATLAB figures. This helper expects synthetic outputs only.

if nargin < 1
    outputDir = 'outputs';
end
resultsDir = fullfile(outputDir, 'results');
figuresDir = fullfile(outputDir, 'figures');
if ~exist(figuresDir, 'dir')
    mkdir(figuresDir);
end

predPath = fullfile(resultsDir, 'synthetic_support_need_predictions.csv');
fairPath = fullfile(resultsDir, 'synthetic_fairness_audit.csv');
accessPath = fullfile(resultsDir, 'synthetic_access_audit.csv');

if exist(predPath, 'file')
    pred = readtable(predPath);
    figure('Name','Support Need Scores');
    histogram(pred.support_need_score);
    title('Synthetic support-need score distribution');
    xlabel('Support-need score'); ylabel('Student count');
    saveas(gcf, fullfile(figuresDir, 'matlab_support_need_scores.png'));
end

if exist(fairPath, 'file')
    fair = readtable(fairPath);
    [groups, dims] = findgroups(fair.audit_dimension);
    gaps = splitapply(@max, fair.support_rate_gap, groups);
    figure('Name','Fairness Gaps');
    bar(gaps);
    set(gca, 'XTickLabel', dims);
    title('Max support-rate gap by audit dimension');
    ylabel('Support-rate gap');
    saveas(gcf, fullfile(figuresDir, 'matlab_fairness_gaps.png'));
end

if exist(accessPath, 'file')
    access = readtable(accessPath);
    figure('Name','Access Risk');
    histogram(access.access_risk_score);
    title('Synthetic access-risk score distribution');
    xlabel('Access-risk score'); ylabel('Event count');
    saveas(gcf, fullfile(figuresDir, 'matlab_access_risk.png'));
end
end
