function varargout = simulation_parameters(path, varargin)
    %% Specifies the parameters for the simulation
    
    %% INPUTS

        % path [string]: Path to save the results
    
    %% OUTPUTS

        % parameters [struct]: Structure containing the parameters

    %% AUTHOR

        % Christian Gerloff

    Args = struct('scenario_name', 'default',...  % Scenario name
                  'scenario_adjustments', struct);  % Scenario adjustments to overwrite default values
    Args = parseargs_special(varargin, Args);

    %% General settings
    parameters.sim.simulation_path = path;
    parameters.sim.scenario_name = Args.scenario_name;
    parameters.sim.save_dotnirs = false;  % Store preprocessed results as .nirs files
    parameters.sim.raw_snirf = true;  % Store raw intensity data in SNIRF format
    parameters.sim.decision = 1;  % Options: 1 = good channel, 3 = bad channel; sets the bad channel decision for all subjects and channels
    parameters.sim.seed = 20211001;
    parameters.sim.fs = 10;  % Sampling frequency

    %% Design setting for block and event-related designs
    parameters.design.design_vector = [0 1 0 1 0];  % Options: 0 = rest, 1 = task; e.g., [0 1 0 1 0]
    parameters.design.min_rest_duration = 30;  % Minimum rest block length, varies by trial settings, in seconds
    parameters.design.n_stimuli_per_block = 20;  % Number of stimuli per block
    parameters.design.duration_stimuli = 1;  % Duration of each stimulus in seconds
    parameters.design.min_break_stimuli = 5;  % Minimum break before stimuli in seconds
    parameters.design.max_break_stimuli = 6;  % Maximum break before stimuli in seconds
    parameters.design.consistent_length = true;  % Ensures consistent length
    parameters.design.shortdistance = false;  % Adds short distance channels to probe
    
    %% Base signal
    parameters.signal.ar_order = 10;  % Temporal correlation between channels, see Barker et al., 2013
    parameters.signal.sigma = 0.33;  % Spatial correlation between channels, see Barker et al., 2013
    parameters.signal.neural_frange = [0.08 0.5];  % Frequency range in Hz
    parameters.signal.heartrate_mu = 1.2;  % Normally distributed heart rate with mean (mu) in Hz
    parameters.signal.heartrate_sigma = 0.2;  % Standard deviation (sigma) of normally distributed heart rate in Hz
    parameters.signal.respiration_mu = 0.25;  % Normally distributed respiration rate with mean (mu) in Hz
    parameters.signal.respiration_sigma = 0.05;  % Standard deviation (sigma) of normally distributed respiration rate in Hz
    parameters.signal.meyer_mu = 0.1;  % Normally distributed Mayer waves with mean (mu) in Hz
    parameters.signal.meyer_sigma = 0.02;  % Standard deviation (sigma) of normally distributed Mayer waves in Hz
    parameters.signal.heartrate_amp = 0.15;  % Amplitude of heart rate
    parameters.signal.respiration_amp = 0.15;  % Amplitude of respiration
    parameters.signal.meyer_amp = 0.15;  % Amplitude of Mayer waves
    parameters.signal.heartrate_amp_coupling = 1;  % Scales HbR amplitude
    parameters.signal.respiration_amp_coupling = 1;  % Scales HbR amplitude
    parameters.signal.meyer_amp_coupling = 0.5;  % Scales HbR amplitude
    parameters.signal.physiological_phaseshift = 0.1;  % Normally distributed phase shift
    parameters.signal.physiological_phaseshift_coupling = 1; % Shifts phase between chromophores
    
    %% HRF settings to couple or decouple oxy and deoxy
    parameters.hrf.perc_active_channels = 1;  % Options: [0, 1] relative number of channels including HRF
    parameters.hrf.short_channel_hrf = false;  % Add HRF to short channels
    parameters.hrf.basis = 'default';  % Options: boxcar, fir, gamma, canonical[default]; sets the basis function
    parameters.hrf.beta_mu = 3;  % Mean of normally distributed HRF magnitude for each stimulus condition
    parameters.hrf.beta_sigma = 0;  % Standard deviation of normally distributed HRF magnitude for each stimulus condition
    parameters.hrf.beta_coupling_mu = -0.5;  % Mean of normally distributed coupling between HbO and HbR magnitude for each stimulus condition
    parameters.hrf.beta_coupling_sigma = 0;  % Standard deviation of normally distributed coupling between HbO and HbR magnitude for each stimulus condition

    %% Artifacts
    parameters.artifacts.n_spikes = 0;  % Spikes per minute
    parameters.artifacts.spikes_amp_mu = 7;  % Mean of normally distributed spike amplitude, see Barker et al., 2013
    parameters.artifacts.spikes_amp_sigma = 2;  % Standard deviation of normally distributed spike amplitude
    parameters.artifacts.spikes_duration_mu = 2;  % Mean of normally distributed spike duration
    parameters.artifacts.spikes_duration_sigma = 1;  % Standard deviation of normally distributed spike duration
    parameters.artifacts.n_shifts = 0;  % Shifts per minute
    parameters.artifacts.shifts_amp_mu = 1.5;  % Mean of normally distributed shift amplitude
    parameters.artifacts.shifts_amp_sigma = 2;  % Standard deviation of normally distributed shift amplitude
    parameters.artifacts.shifts_unidirected = false;  % Options: true, false; if true, shifts are unidirectional

    %% Preprocessing settings
    parameters.preprocessing = 'TDDR'; % Options: 'TDDR' or 'MARA'
    
    %% Following parameters can be ignored and where not used
    parameters.mara.tmotion = .5;
    parameters.mara.tmask = 2;
    parameters.mara.threshold_std = 14;
    parameters.mara.threshold_amp = 2;
    parameters.mara.spline_p = .99;

    %% Overwrite default values
    if ~isempty(fieldnames(Args.scenario_adjustments))
        categories = fieldnames(Args.scenario_adjustments);
        for f = 1:numel(categories)
            category = string(categories{f});
            settings = fieldnames(Args.scenario_adjustments.(category));
            for s = 1:numel(settings)
                setting = string(settings{s});
                % parameters.(f).(s) = Args.scenario_adjustments.(f).(s);
                parameters = setfield(...
                    parameters,...
                    category,...
                    setting,...
                    Args.scenario_adjustments.(category).(setting));
            end
        end
    end

    %% Save
    parameters.sim.scenario_path = strcat(parameters.sim.simulation_path, '/',...
                                          parameters.sim.scenario_name);
    varargout={parameters};
    varargout=varargout(1:nargout);
end