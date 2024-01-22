function varargout = features_parameters(path, varargin)
    %% Specifies the parameters of the features
    
    %% INPUTS

        % path [string]: Path to save the results
    
    %% OUTPUTS

        % parameters [struct]: Structure containing the parameters

    %% AUTHOR

        % Christian Gerloff
        
    Args = struct('feature_space_name', 'default',...  % Feature space name
                  'feature_adjustments', struct);  % Feature adjustments to overwrite default values
    Args = parseargs_special(varargin, Args);
    
    %% General feature space settings
    parameters.feature_space.path = path;
    parameters.feature_space.name = Args.feature_space_name;
    parameters.feature_space.fs = 10;  % Sampling frequency [Hz]

    %% Signal to noise measures
    parameters.snr.lower_bound = 0.0156;  % Lower bound of IIR bandpass filter [Hz]
    parameters.snr.upper_bound = parameters.feature_space.fs/2;  % Upper bound of IIR bandpass filter [Hz]
    parameters.snr.order = 4;  % Order of IIR (*2) bandpass filter
    parameters.snr.decision = 10;  % Decision threshold of SNR detector, see Nguyen, Hoehl, Vrtička et al.

    %% Spike rate
    parameters.sr.max_width = 1;  % Maximum width of peaks

    %% Signal level
    parameters.sl.level_1 = [0.01; 10];  % Estimation of signal level range to determine threshold
    parameters.sl.threshold_1 = [0.03; 2.5];  % Threshold for lower bound, see Nguyen, Hoehl, Vrtička et al.
    parameters.sl.level_2 = [10; 10000];  % Estimation of signal level range to determine threshold
    parameters.sl.threshold_2 = [3; 250];  % Threshold for lower bound, see hmrR_PruneChannels.m * 10^-4
    
    %% Heart rate detection
    parameters.hr.heart_rate_mu = 1.2;
    parameters.hr.heart_rate_min = 0.7;
    parameters.hr.heart_rate_max = 1.5;
    parameters.hr.frequency_range = [0.01; 1.6];

    %% Coefficient of variation parameters
    parameters.cov.threshold = 0.1;  % Threshold of standard deviation / mean (COV)
    parameters.cov.diff_threshold = 0.05;  % Threshold of differences between COV of both wavelengths
    
    %% Scalp coupling metrics
    parameters.scm.lower_bound = 0.7;  % Lower bound of IIR bandpass filter [Hz]. Default in MNE: 0.7, else 0.5 
    parameters.scm.upper_bound = 1.5;  % Upper bound of IIR bandpass filter [Hz]. Default in MNE: 1.5, else 2.5
    parameters.scm.order = 4;  % Order of IIR (*2) bandpass filter
    parameters.scm.normalize = 'coeff';  % Normalizes the sequence so that the autocorrelations at zero lag is equal to 1
    parameters.scm.t_window = 10;  % Window of SCI in seconds. Default: 2-10s.
    parameters.scm.sci = 0.5;  % Threshold of scalp coupling index. Default: 0.5
    parameters.scm.power = 0.1;  % Threshold of signal power. Default: 0.1

    %% Signal quality score
    parameters.sqs.lower_bound = 0.5;  % Lower bound of IIR bandpass filter [Hz]. Default: see Paper.
    parameters.sqs.upper_bound = 2.5;  % Upper bound of IIR bandpass filter [Hz]. Default: see Paper.
    parameters.sqs.order = 4;  % Order of IIR (*2) bandpass filter
    parameters.sqs.thr_upper_intensity = 2.5;  % Threshold of intensity, see Sappia et al.
    parameters.sqs.thr_lower_intensity = 0.04;  % Threshold of intensity, see Sappia et al.
    parameters.sqs.thr_hbratio = 1.95;  % Threshold of Hb ratio, see Sappia et al.
    parameters.sqs.thr_diff_autocorr = 0.025;  % Threshold of auto-correlation differences, see Sappia et al.
    parameters.sqs.slope = 1.796;  % Slope of score, see Sappia et al.
    parameters.sqs.intercept = 0.846;  % Intercept of score, see Sappia et al.



    %% Continuous wavelet transform
    parameters.cwt.n_samples = 4000;  % Number of samples to consider for CWT
    parameters.cwt.lead_samples = 0;  % Cut lead samples
    parameters.cwt.followup_samples = 0;  % Cut follow-up samples
    parameters.cwt.down_sr = 2;  % Downsampling frequency rate
    parameters.cwt.wavelet = 'amor';  % Mother wavelet
    parameters.cwt.vpo = 8;  % Voices per octave, 8-12
    parameters.cwt.frequency_limits = [0.05; 1.5];

    %% Overwrite default values
    if ~isempty(fieldnames(Args.feature_adjustments))
        categories = fieldnames(Args.feature_adjustments);
        for f = 1:numel(categories)
            category = string(categories{f});
            settings = fieldnames(Args.feature_adjustments.(category));
            for s = 1:numel(settings)
                setting = string(settings{s});
                % parameters.(f).(s) = Args.scenario_adjustments.(f).(s);
                parameters = setfield(...
                    parameters,...
                    category,...
                    setting,...
                    Args.feature_adjustments.(category).(setting));
            end
        end
    end

    %% Save
    parameters.feature_space.path = strcat(parameters.feature_space.path, '/',...
                                           parameters.feature_space.name);
    varargout={parameters};
    varargout=varargout(1:nargout);
end