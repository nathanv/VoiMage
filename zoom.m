function [ZI] = zoom (I,Flag)

I = imread(I);

if strcmp(Flag,'more')
    
    ZI = magnify(I,3, 0, 0);
    
elseif strcmp(Flag,'left')
    
    ZI = magnify(I,2, -25, 0);
    
elseif strcmp(Flag,'right')
    
    ZI = magnify(I,2, 25, 0);
    
elseif strcmp(Flag,'up')
    
    ZI = magnify(I,2, 0, 25);
    
elseif strcmp(Flag,'down')

    ZI = magnify(I,2, 0, -25);  
    
else
    
    ZI = magnify(I,2, 0, 0);  
    
end