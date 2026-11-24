
function [data] = load_dmf (filename)

fileID = fopen(filename);
assert(fileID ~= -1);

%% read header
header = '';

while (true)
  header = strcat(header, fgetl(fileID));
  if ( strcmp(header(end-7:end), '<data />') )
    break;
  end
end

%disp(header);

%% parse header
bracket_open_pos = strfind(header, '<');
bracket_close_pos = strfind(header, '>');
assert(length(bracket_open_pos) == length(bracket_close_pos));
assert(bracket_open_pos(1) < bracket_close_pos(1));

% check document type
bracket_content = strtrim( header(bracket_open_pos(1)+1 : bracket_close_pos(1)-1) );
assert(strcmp(bracket_content, '?DMF version="1.0"?'));

% check last element for conformity
bracket_content = strtrim( header(bracket_open_pos(end)+1 : bracket_close_pos(end)-1) );
assert(strcmp(bracket_content, 'data /'));

% read general settings
bracket_content = strtrim( header(bracket_open_pos(2)+1 : bracket_close_pos(2)-1) );
assert(strcmp(get_xml_identifier(bracket_content), 'settings'));
struct_key_size = sscanf(bracket_content, 'settings struct_key_size="%u');

% read string settings
bracket_content = strtrim( header(bracket_open_pos(3)+1 : bracket_close_pos(3)-1) );
assert(strcmp(get_xml_identifier(bracket_content), 'string'));
string_length_size = sscanf(bracket_content, 'string length_size="%u');

% read struct definitions
current_struct = 0;
current_field = 0;
for i = 4:length(bracket_close_pos)-1
  bracket_content = strtrim( header(bracket_open_pos(i)+1 : bracket_close_pos(i)-1) );
  identifier = get_xml_identifier(bracket_content);
  if (strcmp(identifier, 'struct'))
    current_struct = current_struct + 1;
    
    struct_def(current_struct).key = sscanf(bracket_content, 'struct key="%u');
    
    pos = strfind(bracket_content, 'name="');
    for j = pos+6 : length(bracket_content)
      if (strcmp(bracket_content(j), '"'))
        break;
      end
    end
    struct_def(current_struct).name = bracket_content(pos+6:j-1);
    
    current_field = 0;
  elseif (strcmp(identifier, 'field'))
    current_field = current_field + 1;
    
    pos = strfind(bracket_content, 'type="');
    for j = pos+6 : length(bracket_content)
      if (strcmp(bracket_content(j), '"'))
        break;
      end
    end
    struct_def(current_struct).field(current_field).type = bracket_content(pos+6:j-1);
    
    bracket_content = bracket_content(j:end);
    
    pos = strfind(bracket_content, 'name="');
    for j = pos+6 : length(bracket_content)
      if (strcmp(bracket_content(j), '"'))
        break;
      end
    end
    struct_def(current_struct).field(current_field).name = bracket_content(pos+6:j-1);
    
    bracket_content = bracket_content(j:end);
    
    pos = strfind(bracket_content, 'unit="');
    for j = pos+6 : length(bracket_content)
      if (strcmp(bracket_content(j), '"'))
        break;
      end
    end
    struct_def(current_struct).field(current_field).unit = bracket_content(pos+6:j-1);
    
    struct_def(current_struct).field(current_field).descr = strtrim( header(bracket_close_pos(i)+1 : bracket_open_pos(i+1)-1) );
  end
end

%parse_pos = 2;
%for i = 1:length(bracket_open_pos)
%while (parse_pos <= length(bracket_close_pos))
%  bracket_content = strtrim( header(bracket_open_pos(parse_pos)+1 : bracket_close_pos(parse_pos)-1) );
%  if (strcmp(bracket_content(end), '/')) % single element entry (ending with /)
%    %bracket_content
%  else % multi-element entry
%    % get opening element, e.g. <X>
%    identifier = get_xml_identifier(bracket_content)
%    
%    % find closing element, e.g. </X>
%    closing_identifier = strcat('/', identifier);
%    for i = parse_pos:length(bracket_close_pos)
%      bracket_content2 = strtrim( header(bracket_open_pos(i)+1 : bracket_close_pos(i)-1) );
%      identifier2 = get_xml_identifier(bracket_content2);
%      if (strcmp(identifier2, closing_identifier))
%        %identifier2
%        %header( bracket_close_pos(parse_pos)+1 : bracket_open_pos(i)-1 )
%        parse_pos = i;
%        break;
%      end
%    end
%    
%  end
%  parse_pos = parse_pos + 1;
%end


% test struct loading
key_vector = [struct_def.key];



% prepare storage
for key_idx = 1:length(key_vector)
  for i = 1:length(struct_def(key_idx).field)
    if ( strcmp(struct_def(key_idx).field(i).type, 'string') )
      data.(struct_def(key_idx).name).(struct_def(key_idx).field(i).name) = char();
    else
      data.(struct_def(key_idx).name).(struct_def(key_idx).field(i).name) = [];
    end
  end
end



key_reader = get_uint_reader(fileID, struct_key_size);
string_length_reader = get_uint_reader(fileID, string_length_size);

% load actual data
while (~feof(fileID))
  key = key_reader();
  if (isempty(key))
    break;
  end
  
  key_idx = find(key_vector == key, 1);
  assert(~isempty(key_idx));
  
  %data.(struct_def(key_idx).name) = 1;

  for i = 1:length(struct_def(key_idx).field)
    %disp(struct_def(key_idx).field(i).type);
    switch (struct_def(key_idx).field(i).type)
      case 'int8'
        val = fread(fileID, 1, "int8=>int8");
      case 'int16'
        val = fread(fileID, 1, "int16=>int16");
      case 'int32'
        val = fread(fileID, 1, "int32=>int32");
      case 'int64'
        val = fread(fileID, 1, "int64=>int64");
        
      case 'uint8'
        val = fread(fileID, 1, "uint8=>uint8");
      case 'uint16'
        val = fread(fileID, 1, "uint16=>uint16");
      case 'uint32'
        val = fread(fileID, 1, "uint32=>uint32");
      case 'uint64'
        val = fread(fileID, 1, "uint64=>uint64");
      
      case 'float32'
        val = fread(fileID, 1, "float32=>float32");
      case 'float64'
        val = fread(fileID, 1, "float64=>float64");
      case 'string'
        len = string_length_reader();
        val = fread(fileID, [1,len], "char=>char");
      otherwise
        error('Unsupported data type');
    end
    data.(struct_def(key_idx).name).(struct_def(key_idx).field(i).name) = [data.(struct_def(key_idx).name).(struct_def(key_idx).field(i).name); val];
  end % for
end

fclose(fileID);

data.struct_def = struct_def;

end


function [readerFunc] = get_uint_reader(fileID, uint_len)

switch (uint_len)
  case 2
    readerFunc = @() fread(fileID, 1, "uint16=>uint16");
  case 4
    readerFunc = @() fread(fileID, 1, "uint32=>uint32");
  case 8
    readerFunc = @() fread(fileID, 1, "uint64=>uint64");
  otherwise
    fclose(fileID);
    error('Unsupported struct key size.');
end

end


function [identifier] = get_xml_identifier (bracket_content)

for i = 1:length(bracket_content)
  if ( strcmp(bracket_content(i), ' ') )
    break;
  end
end

if (i == length(bracket_content))
  identifier = bracket_content(1:i);
else
  identifier = bracket_content(1:i-1);
end

end

