function save_json(data, path, filename)
    %% Stores struct as a json file

    %% INPUTS

        % data [struct]: struct that will be stored as json
        % path [string]: path of json
        % filename [string]: filename of json file
           
    %% AUTHOR

        % Christian Gerloff

    % create folder
    if not(isfolder(path))
        mkdir(path)
    end

    full_filename = fullfile(path,...
                            filename);

    id_json = fopen(full_filename, 'w'); 
    json = jsonencode(data);
    fprintf(id_json, json); 
    fclose(id_json);
end