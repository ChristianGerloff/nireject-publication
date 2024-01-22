function [stim, rest, timeseries, n_samples] = design_experiment(...
    fs,...
    design_vector,...
    min_rest_duraion,...
    n_stimuli_per_block,...
    duration_stimuli,...
    min_break_stimuli,...
    max_break_stimuli,...
    consitent_length,...
    varargin)
    %% Encodes block or event related design
    
    %% INPUTS
    
        % fs [int]: sampling frequency
        % design_vector [array]: encodes the experimental design
        % min_rest_duraion [int]: represents parameter struct of experiment
        % n_stimuli_per_block [int]: number of stimuli per block
        % duration_stimuli [int]: duration of stimuli in sec.
        % min_break_stimuli [int]: min break before stimuli in sec.
        % max_break_stimuli [int]: max break before stimuli in sec.
        % consitent_length [boolean]: % ensures consient length
        % varargin [*kwargs]: keyword based arguments
    
    %% OUTPUTS

        % stim [Dictionary]: that encodes the stimuli per condition
        % rest [Dictionary]: that encodes the rest per condition
        % timeseries [array]: timestamp in sec.
        % number of samples [int]:  number of samples

    %% AUTHOR

        % Christian Gerloff

    Args = struct('seed', 20211001);
    Args = parseargs_special(varargin, Args);

    % initialization
    stim = Dictionary();
    block_end = 0;
    trails = [];
    seed = Args.seed;
    if consitent_length == false
        seed = randi([42, 77617665], 1, 1);
    end
    rng(seed);

    % prebuild blocks
    rest_leap = duration_stimuli + max_break_stimuli;
    duration_stimuli = duration_stimuli * ones(size(n_stimuli_per_block));
    default_break_stimuli = randi([min_break_stimuli max_break_stimuli],...
                                  n_stimuli_per_block,...
                                  1);
    % create rest infos
    rest = nirs.design.StimulusEvents();
    rest.name = 'rest';

    % create trails within a single condition
    for i = 1:size(design_vector, 2)
        if design_vector(i) == 0
            % duration of last stimuli of previous block should be
            % considered
            if i > 1 &&  design_vector(i-1) == 1
                n_rest = min_rest_duraion + rest_leap;   
                rest.onset = [rest.onset; block_end + rest_leap];
            else
                n_rest = min_rest_duraion;
                rest.onset = [rest.onset; block_end + rest_leap];
            end
            rest.amp = [rest.amp; 0];
            rest.dur = [rest.dur; min_rest_duraion];
            block_end = block_end + n_rest;
        else
            % shuffle breaks between each stimuli
            rng(seed+i*100);
            breaks = default_break_stimuli(...
                randperm(length(default_break_stimuli)));
            block = block_end + cumsum(breaks + duration_stimuli);
            block_end = block(end);
            trails = [trails; block];
        end
    end
    s = nirs.design.StimulusEvents();
    s.name = 'task';
    s.amp = 1 * ones(size(trails));
    s.dur = duration_stimuli * ones(size(trails));
    s.onset = trails;
    stim(s.name) = s;
    
    timeseries = (0:1/fs:block_end)';
    n_samples = fs * block_end + 1;
end      
            
        





