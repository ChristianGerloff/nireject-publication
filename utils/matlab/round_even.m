function rounded_number = round_even(number)
    %% round to nearest even integer.

    %% INPUTS

        % number [double] number to be rounded

    %% AUTHOR

        % Christian Gerloff
        
    rounded_number = 2*floor(number/2);
end